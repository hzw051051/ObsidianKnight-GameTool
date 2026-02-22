"""
坐标校准工具
截取模拟器内部屏幕，帮助获取正确的点击坐标
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.adb_controller import ADBController
import cv2
import numpy as np

print("=" * 60)
print("模拟器坐标校准工具")
print("=" * 60)

# 连接ADB
adb = ADBController('127.0.0.1', 5554)
if not adb.connect():
    print("❌ 无法连接模拟器")
    sys.exit(1)

print("✅ 已连接模拟器\n")

# 截图
screen = adb.screenshot()
if screen is None:
    print("❌ 截图失败")
    sys.exit(1)

screen_np = np.array(screen)
screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
h, w = screen_bgr.shape[:2]

# 保存截图
output_file = "calibration_screenshot.png"
cv2.imwrite(output_file, screen_bgr)

print(f"模拟器内部分辨率: {w}x{h}")
print(f"\n✅ 截图已保存: {output_file}")
print("\n" + "=" * 60)
print("使用方法:")
print("1. 打开截图文件 calibration_screenshot.png")
print("2. 用画图软件查看需要点击位置的坐标")
print("3. 这个坐标就是正确的模拟器内部坐标")
print("=" * 60)

# 显示当前配置的坐标
print("\n当前 config.jsonc 中的坐标:")
print("-" * 40)

from src.config_loader import Config
config = Config()

print(f"开始按钮:     {config.btn_start_pos}")
print(f"重试按钮:     {config.btn_retry_pos}")
print(f"继续按钮:     {config.btn_continue_pos}")
print(f"购买确认:     {config.btn_purchase_confirm_pos}")
print(f"卡牌位置:     {config.card_positions}")
print(f"选项位置:     {config.choice_positions}")

print("\n" + "=" * 60)
print("请检查这些坐标是否在模拟器分辨率范围内 (0-{w}, 0-{h})".format(w=w, h=h))
print("=" * 60)
