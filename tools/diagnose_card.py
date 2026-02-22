"""
卡牌选择界面诊断工具
分析为什么卡牌选择被误判为障碍物三选一
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from src.adb_controller import ADBController

def diagnose_card_screen():
    print("=== 卡牌选择界面诊断工具 ===\n")
    
    # 连接并截图
    adb = ADBController()
    if not adb.connect():
        print("❌ 无法连接到模拟器")
        return
    
    print("✓ 已连接，正在截图...")
    pil_img = adb.screenshot()
    if pil_img is None:
        print("❌ 截图失败")
        return
    
    # 转换为OpenCV格式
    screen = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    h, w = screen.shape[:2]
    hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    
    print(f"✓ 截图成功: {w}x{h}\n")
    
    # === 检测1：障碍物三选一 ===
    print("【检测1：障碍物三选一】")
    
    # 左下角属性面板
    bottom_left = screen[int(h*0.5):, :int(w*0.25)]
    bl_hsv = cv2.cvtColor(bottom_left, cv2.COLOR_BGR2HSV)
    dark_mask = cv2.inRange(bl_hsv, np.array([0, 0, 0]), np.array([180, 255, 80]))
    dark_pixels = cv2.countNonZero(dark_mask)
    
    # 顶部金色框
    top_region_hsv = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
    gold_mask = cv2.inRange(top_region_hsv, np.array([15, 80, 80]), np.array([40, 255, 255]))
    gold_pixels = cv2.countNonZero(gold_mask)
    
    print(f"  - 属性面板深色像素: {dark_pixels} (需要 > 5000)")
    print(f"  - 顶部金色像素:     {gold_pixels} (需要 > 2000)")
    
    if dark_pixels > 5000 and gold_pixels > 2000:
        print(f"  ⚠️  会被误判为: OBSTACLE_CHOICE\n")
        obstacle_match = True
    else:
        print(f"  ✓ 不会误判为障碍物\n")
        obstacle_match = False
    
    # === 检测2：卡牌选择 ===
    print("【检测2：卡牌选择】")
    
    # 左上角英语按钮
    top_left_region = hsv[:int(h*0.3), :int(w*0.3)]
    english_btn_mask = cv2.inRange(top_left_region, np.array([10, 100, 100]), np.array([25, 255, 255]))
    english_pixels = cv2.countNonZero(english_btn_mask)
    
    # 右下角重投按钮
    bottom_right_region = hsv[int(h*0.7):, int(w*0.7):]
    retry_btn_mask = cv2.inRange(bottom_right_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
    retry_pixels = cv2.countNonZero(retry_btn_mask)
    
    print(f"  - 英语按钮橙色像素: {english_pixels} (当前阈值 > 110000)")
    print(f"  - 重投按钮橙色像素: {retry_pixels} (当前阈值 > 5000)")
    
    if english_pixels > 110000 or retry_pixels > 5000:
        print(f"  ✅ 应识别为: CARD_SELECTION")
        card_match = True
    else:
        print(f"  ❌ 阈值太高，无法识别为卡牌选择")
        card_match = False
    print()
    
    # === 最终结果 ===
    print("【诊断结果】")
    
    if obstacle_match and not card_match:
        print("⚠️  问题：卡牌界面被误判为障碍物三选一！")
        print("\n【建议修复】")
        
        # 降低卡牌选择阈值
        if english_pixels > 1000:
            suggested_english = max(1000, english_pixels - 500)
            print(f"  - 英语按钮阈值：110000 → {suggested_english}")
        if retry_pixels > 1500:
            suggested_retry = max(1500, retry_pixels - 500)
            print(f"  - 重投按钮阈值：5000 → {suggested_retry}")
            
    elif card_match:
        print("✅ 界面应该被正确识别为: CARD_SELECTION")
    else:
        print("⚠️  两个检测都未触发")
    
    print("\n=== 诊断完成 ===")

if __name__ == "__main__":
    print("请确保游戏在【卡牌选择界面】，然后按Enter开始诊断...")
    input()
    diagnose_card_screen()
