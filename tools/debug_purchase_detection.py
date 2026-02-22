"""
调试购买失败界面识别 - 打印详细检测数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from src.adb_controller import ADBController
from src.image_recognition import ImageRecognizer, GameState
from src.config_loader import Config

def debug_detection(screen):
    """详细分析界面检测数据"""
    h, w = screen.shape[:2]
    print(f"\n屏幕尺寸: {w}x{h}")
    print("=" * 60)
    
    hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    
    # ===== 新的购买失败界面检测 =====
    print("\n【购买失败界面检测 - 新逻辑】")
    
    # 检测中央区域的棕色木质边框
    center_region = screen[int(h*0.3):int(h*0.7), int(w*0.25):int(w*0.75)]
    center_hsv = cv2.cvtColor(center_region, cv2.COLOR_BGR2HSV)
    brown_mask = cv2.inRange(center_hsv, np.array([10, 50, 100]), np.array([30, 200, 200]))
    brown_pixels = cv2.countNonZero(brown_mask)
    print(f"  中央棕色边框像素: {brown_pixels} (阈值: >18000)")
    
    # 检测中下部橙色确认按钮
    button_check_region = screen[int(h*0.5):int(h*0.75), int(w*0.35):int(w*0.65)]
    button_check_hsv = cv2.cvtColor(button_check_region, cv2.COLOR_BGR2HSV)
    orange_mask = cv2.inRange(button_check_hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
    button_orange_pixels = cv2.countNonZero(orange_mask)
    print(f"  中下部橙色按钮像素: {button_orange_pixels} (阈值: >5000)")
    
    purchase_match = brown_pixels > 18000 and button_orange_pixels > 5000
    print(f"  {'✅ 匹配购买失败' if purchase_match else '❌ 不匹配购买失败'}")
    print(f"  条件1 (棕色>18000): {brown_pixels > 18000}")
    print(f"  条件2 (橙色>5000): {button_orange_pixels > 5000}")
    
    # ===== 障碍物选择界面检测 =====
    print("\n【障碍物选择界面检测】")
    
    # 检测左下角属性面板
    bottom_left = screen[int(h*0.5):, :int(w*0.25)]
    bl_hsv = cv2.cvtColor(bottom_left, cv2.COLOR_BGR2HSV)
    dark_mask2 = cv2.inRange(bl_hsv, np.array([0, 0, 0]), np.array([180, 255, 80]))
    dark_pixels2 = cv2.countNonZero(dark_mask2)
    print(f"  左下角深色像素: {dark_pixels2} (阈值: >5000)")
    
    # 检测顶部金色选项框
    top_region_hsv = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
    gold_mask = cv2.inRange(top_region_hsv, np.array([15, 80, 80]), np.array([40, 255, 255]))
    gold_pixels = cv2.countNonZero(gold_mask)
    print(f"  顶部金色像素: {gold_pixels} (阈值: >2000)")
    
    obstacle_match = dark_pixels2 > 5000 and gold_pixels > 2000
    print(f"  ✅ 匹配障碍物选择" if obstacle_match else f"  ❌ 不匹配障碍物选择")
    
    # ===== 底部橙色区域检测 =====
    print("\n【底部橙色检测】")
    orange_lower = np.array([10, 150, 150])
    orange_upper = np.array([25, 255, 255])
    orange_mask_full = cv2.inRange(hsv, orange_lower, orange_upper)
    bottom_region = orange_mask_full[int(h*0.7):, :]
    bottom_orange_pixels = cv2.countNonZero(bottom_region)
    print(f"  底部橙色像素: {bottom_orange_pixels}")
    
    print("\n" + "=" * 60)

def main():
    print("=" * 60)
    print("购买失败界面识别调试工具")
    print("=" * 60)
    
    # 初始化
    config = Config("config")
    adb = ADBController(host=config.adb_host, port=config.adb_port)
    recognizer = ImageRecognizer("templates")
    
    # 连接模拟器
    print("\n连接模拟器...")
    if not adb.connect():
        print("❌ 连接失败")
        return
    print("✅ 连接成功")
    
    # 截图
    print("截取界面...")
    screenshot = adb.screenshot()
    if screenshot is None:
        print("❌ 截图失败")
        return
    
    # 保存截图
    screenshot.save("debug_purchase_failed.png")
    print("✅ 截图已保存: debug_purchase_failed.png")
    
    # 转换格式
    screen = recognizer.pil_to_cv2(screenshot)
    
    # 详细分析
    debug_detection(screen)
    
    # 识别状态
    print("\n最终识别结果:")
    state = recognizer.detect_state(screen)
    print(f">>> {state.name}")
    
    if state == GameState.PURCHASE_FAILED:
        print("✅ 识别正确！")
    else:
        print(f"❌ 识别错误！应该是 PURCHASE_FAILED，实际是 {state.name}")

if __name__ == "__main__":
    main()
