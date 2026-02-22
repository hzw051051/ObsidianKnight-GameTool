"""
测试购买失败界面识别和点击功能
使用方法：确保模拟器停留在购买失败界面，然后运行此脚本
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.adb_controller import ADBController
from src.image_recognition import ImageRecognizer, GameState
from src.config_loader import Config

def main():
    print("=" * 50)
    print("购买失败界面测试脚本")
    print("=" * 50)
    
    # 初始化组件
    config = Config("config")
    adb = ADBController(host=config.adb_host, port=config.adb_port)
    recognizer = ImageRecognizer("templates")
    
    # 连接模拟器
    print("\n[1] 连接模拟器...")
    if not adb.connect():
        print("❌ 连接失败！请确保雷电模拟器已启动")
        return
    print("✅ 连接成功")
    
    # 截图
    print("\n[2] 截取当前界面...")
    screenshot = adb.screenshot()
    if screenshot is None:
        print("❌ 截图失败")
        return
    print("✅ 截图成功")
    
    # 转换格式
    screen = recognizer.pil_to_cv2(screenshot)
    
    # 识别状态
    print("\n[3] 识别界面状态...")
    state = recognizer.detect_state(screen)
    print(f"识别结果: {state.name}")
    
    # 检查是否为购买失败界面
    if state == GameState.PURCHASE_FAILED:
        print("✅ 成功识别为购买失败界面！")
        
        # 获取确认按钮坐标
        x, y = config.btn_purchase_confirm_pos
        print(f"\n[4] 准备点击确认按钮: ({x}, {y})")
        
        # 询问是否执行点击
        response = input("是否执行点击? (y/n): ")
        if response.lower() == 'y':
            print("执行点击...")
            adb.tap(x, y)
            print("✅ 点击完成！")
            
            # 等待并再次检测
            import time
            time.sleep(2)
            print("\n[5] 再次检测界面状态...")
            screenshot2 = adb.screenshot()
            if screenshot2:
                screen2 = recognizer.pil_to_cv2(screenshot2)
                state2 = recognizer.detect_state(screen2)
                print(f"新状态: {state2.name}")
                if state2 != GameState.PURCHASE_FAILED:
                    print("✅ 成功离开购买失败界面！")
                else:
                    print("⚠️ 仍在购买失败界面，可能需要调整坐标")
        else:
            print("取消点击")
    else:
        print(f"❌ 当前不是购买失败界面，而是: {state.name}")
        print("请确保模拟器停留在购买失败界面后重试")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
