"""
测试脚本：截图并保存，用于分析按钮坐标
"""
import sys
sys.path.insert(0, ".")

from src.adb_controller import ADBController

def main():
    print("正在连接模拟器...")
    adb = ADBController()
    
    if not adb.connect():
        print("连接失败!")
        return
    
    print(f"连接成功: {adb.device_id}")
    
    # 截图并保存
    print("正在截图...")
    img = adb.screenshot()
    
    if img:
        filename = "debug_screenshot.png"
        img.save(filename)
        print(f"截图已保存: {filename}")
        print(f"图片尺寸: {img.size}")
        print("\n请用图片查看器打开 debug_screenshot.png，")
        print("查看'重试'按钮中心的像素坐标，然后告诉我坐标值。")
    else:
        print("截图失败!")

if __name__ == "__main__":
    main()
