"""
调试卡牌选择界面识别问题
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from src.image_recognition import ImageRecognizer, GameState
from src.adb_controller import ADBController

print("=" * 60)
print("卡牌选择界面识别调试")
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

print(f"屏幕尺寸: {w}x{h}\n")

# 转换HSV
hsv = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2HSV)

print("【检测详细数据】\n")

# 1. 底部橙色像素
orange_mask = cv2.inRange(hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
bottom_region = orange_mask[int(h*0.7):, :]
bottom_orange_pixels = cv2.countNonZero(bottom_region)
print(f"1. 底部橙色像素: {bottom_orange_pixels} (阈值>3000)")

# 2. Best time区域检测
best_time_region = screen_bgr[int(h*0.85):int(h*0.95), :int(w*0.15)]
bt_gray = cv2.cvtColor(best_time_region, cv2.COLOR_BGR2GRAY)
white_text = cv2.countNonZero((bt_gray > 200).astype(np.uint8))
dark_bg = cv2.countNonZero((bt_gray < 60).astype(np.uint8))
print(f"2. Best time区域:")
print(f"   白色文字: {white_text} (阈值>150)")
print(f"   深色背景: {dark_bg} (阈值>300)")
print(f"   判定条件: white_text>{white_text>150} AND dark_bg>{dark_bg>300} AND white_text<dark_bg:{white_text<dark_bg}")
best_time_match = white_text > 150 and dark_bg > 300 and white_text < dark_bg
print(f"   → Best time匹配: {best_time_match}")

# 3. 左上角"英语"按钮
top_left_region = hsv[:int(h*0.3), :int(w*0.3)]
english_btn_mask = cv2.inRange(top_left_region, np.array([10, 100, 100]), np.array([25, 255, 255]))
english_pixels = cv2.countNonZero(english_btn_mask)
print(f"\n3. 左上角英语按钮: {english_pixels} (阈值>7000)")

# 4. 右下角"重投"按钮
bottom_right_region = hsv[int(h*0.7):, int(w*0.7):]
retry_btn_mask = cv2.inRange(bottom_right_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
retry_pixels = cv2.countNonZero(retry_btn_mask)
print(f"4. 右下角重投按钮: {retry_pixels} (阈值>8000)")

# 5. 中间卡牌内容
card_region = screen_bgr[int(h*0.1):int(h*0.6), int(w*0.2):int(w*0.8)]
card_hsv = cv2.cvtColor(card_region, cv2.COLOR_BGR2HSV)
color_mask = cv2.inRange(card_hsv, np.array([0, 50, 50]), np.array([180, 255, 255]))
card_pixels = cv2.countNonZero(color_mask)
print(f"5. 中间卡牌彩色内容: {card_pixels} (阈值>50000)")

# 判断逻辑
print("\n" + "=" * 60)
print("【判断结果】\n")

if bottom_orange_pixels > 3000:
    print("✅ 检测到底部橙色按钮")
    
    if best_time_match:
        print("  → 匹配Best time区域 → 识别为 LEVEL_PREPARE ⚠️")
    elif english_pixels > 7000 or retry_pixels > 8000 or card_pixels > 50000:
        print(f"  → 卡牌选择条件满足:")
        print(f"     英语按钮: {english_pixels > 7000} ({english_pixels})")
        print(f"     重投按钮: {retry_pixels > 8000} ({retry_pixels})")
        print(f"     卡牌内容: {card_pixels > 50000} ({card_pixels})")
        print("  → 识别为 CARD_SELECTION ✅")
    else:
        print("  → 未匹配任何条件 → 继续后续检测")
else:
    print("❌ 未检测到底部橙色按钮")

# 实际识别结果
print("\n" + "=" * 60)
print("【实际识别结果】\n")
recognizer = ImageRecognizer("templates")
detected_state = recognizer.detect_state(screen_bgr)
print(f"识别状态: {detected_state.name}")

if detected_state == GameState.CARD_SELECTION:
    print("✅ 正确识别为卡牌选择")
elif detected_state == GameState.LEVEL_PREPARE:
    print("❌ 错误！被识别为关卡准备")
else:
    print(f"⚠️ 被识别为其他状态: {detected_state.name}")

print("\n" + "=" * 60)
