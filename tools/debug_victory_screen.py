"""
调试胜利界面和开始界面的识别问题
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from src.image_recognition import ImageRecognizer, GameState
from src.adb_controller import ADBController

print("=" * 60)
print("胜利/开始界面识别调试")
print("=" * 60)
print("\n请将游戏切换到需要测试的界面，然后按回车键...")
input()

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
cv2.imwrite("debug_current_screen.png", screen_bgr)
print(f"屏幕尺寸: {w}x{h}")
print("截图已保存: debug_current_screen.png\n")

# 转换HSV
hsv = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2HSV)

print("【各状态检测条件分析】\n")

# 1. 底部橙色像素（共同前提）
orange_mask = cv2.inRange(hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
bottom_region = orange_mask[int(h*0.7):, :]
bottom_orange_pixels = cv2.countNonZero(bottom_region)
print(f"0. 底部橙色像素: {bottom_orange_pixels} (阈值>3000)")

# 2. 胜利界面检测（绿色胜利横幅）
victory_region = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
green_mask = cv2.inRange(victory_region, np.array([35, 80, 80]), np.array([85, 255, 255]))
green_pixels = cv2.countNonZero(green_mask)
print(f"\n1. 【胜利界面】顶部绿色像素: {green_pixels} (阈值>8000)")
print(f"   → 匹配: {green_pixels > 8000}")

# 3. 障碍物选择检测
bottom_left = screen_bgr[int(h*0.5):, :int(w*0.25)]
bl_hsv = cv2.cvtColor(bottom_left, cv2.COLOR_BGR2HSV)
dark_mask = cv2.inRange(bl_hsv, np.array([0, 0, 0]), np.array([180, 255, 80]))
dark_pixels = cv2.countNonZero(dark_mask)

top_region_hsv = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
gold_mask = cv2.inRange(top_region_hsv, np.array([15, 80, 80]), np.array([40, 255, 255]))
gold_pixels = cv2.countNonZero(gold_mask)

print(f"\n2. 【障碍物选择】")
print(f"   左下角深色: {dark_pixels} (阈值>5000)")
print(f"   顶部金色: {gold_pixels} (阈值>10000)")
print(f"   → 匹配: {dark_pixels > 5000 and gold_pixels > 10000}")

# 4. 卡牌选择检测
top_left_region = hsv[:int(h*0.3), :int(w*0.3)]
english_btn_mask = cv2.inRange(top_left_region, np.array([10, 100, 100]), np.array([25, 255, 255]))
english_pixels = cv2.countNonZero(english_btn_mask)

bottom_right_region = hsv[int(h*0.7):, int(w*0.7):]
retry_btn_mask = cv2.inRange(bottom_right_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
retry_pixels = cv2.countNonZero(retry_btn_mask)

card_region = screen_bgr[int(h*0.1):int(h*0.6), int(w*0.2):int(w*0.8)]
card_hsv = cv2.cvtColor(card_region, cv2.COLOR_BGR2HSV)
color_mask = cv2.inRange(card_hsv, np.array([0, 50, 50]), np.array([180, 255, 255]))
card_pixels = cv2.countNonZero(color_mask)

print(f"\n3. 【卡牌选择】")
print(f"   左上英语按钮: {english_pixels} (阈值>7000)")
print(f"   右下重投按钮: {retry_pixels} (阈值>8000)")
print(f"   中间卡牌内容: {card_pixels} (阈值>50000)")
print(f"   → 匹配: {english_pixels > 7000 or retry_pixels > 8000 or card_pixels > 50000}")

# 5. 开始界面检测（Best time）
best_time_region = screen_bgr[int(h*0.85):int(h*0.95), :int(w*0.15)]
bt_gray = cv2.cvtColor(best_time_region, cv2.COLOR_BGR2GRAY)
white_text = cv2.countNonZero((bt_gray > 200).astype(np.uint8))
dark_bg = cv2.countNonZero((bt_gray < 60).astype(np.uint8))

print(f"\n4. 【开始界面】Best time区域")
print(f"   白色文字: {white_text} (阈值>150)")
print(f"   深色背景: {dark_bg} (阈值>300)")
print(f"   → 匹配: {white_text > 150 and dark_bg > 300 and white_text < dark_bg}")

# 实际识别结果
print("\n" + "=" * 60)
print("【实际识别结果】\n")
recognizer = ImageRecognizer("templates")
detected_state = recognizer.detect_state(screen_bgr)
print(f"识别状态: {detected_state.name}")
print("=" * 60)
