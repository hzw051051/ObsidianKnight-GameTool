"""
测试真实购买失败弹窗识别
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from src.image_recognition import ImageRecognizer, GameState

# 测试图片路径
battle_img = "C:/Users/28143/.gemini/antigravity/brain/f2afe9da-cfe0-41d3-ae19-d9e67d22acda/uploaded_image_1770503297741.png"
popup_img = "C:/Users/28143/.gemini/antigravity/brain/f2afe9da-cfe0-41d3-ae19-d9e67d22acda/uploaded_image_1770504753642.png"

print("=" * 60)
print("测试购买失败弹窗识别")
print("=" * 60)

recognizer = ImageRecognizer("templates")

# 测试1: 战斗界面（应该不是购买失败）
print("\n【测试1：战斗界面】")
img1 = cv2.imread(battle_img)
if img1 is not None:
    h, w = img1.shape[:2]
    
    # 调试信息 - 使用新的白色文字检测
    center_text = img1[int(h*0.35):int(h*0.55), int(w*0.3):int(w*0.7)]
    center_gray = cv2.cvtColor(center_text, cv2.COLOR_BGR2GRAY)
    white_pixels = cv2.countNonZero((center_gray > 200).astype(np.uint8))
    dark_pixels = cv2.countNonZero((center_gray < 80).astype(np.uint8))
    
    button_region = img1[int(h*0.55):int(h*0.75), int(w*0.35):int(w*0.65)]
    button_hsv = cv2.cvtColor(button_region, cv2.COLOR_BGR2HSV)
    orange_mask = cv2.inRange(button_hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
    orange_pixels = cv2.countNonZero(orange_mask)
    
    print(f"  中央白色文字: {white_pixels} (阈值>2000)")
    print(f"  中央深色背景: {dark_pixels} (阈值>20000)")
    print(f"  橙色按钮像素: {orange_pixels} (阈值>5000)")
    
    state = recognizer.detect_state(img1)
    print(f"  识别结果: {state.name}")
    if state == GameState.PURCHASE_FAILED:
        print("  ❌ 错误！战斗界面被误判")
    else:
        print("  ✅ 正确！")

# 测试2: 购买失败弹窗（应该识别为购买失败）
print("\n【测试2：购买失败弹窗】")
img2 = cv2.imread(popup_img)
if img2 is not None:
    h, w = img2.shape[:2]
    
    # 调试信息 - 使用新的白色文字检测
    center_text = img2[int(h*0.35):int(h*0.55), int(w*0.3):int(w*0.7)]
    center_gray = cv2.cvtColor(center_text, cv2.COLOR_BGR2GRAY)
    white_pixels = cv2.countNonZero((center_gray > 200).astype(np.uint8))
    dark_pixels = cv2.countNonZero((center_gray < 80).astype(np.uint8))
    
    button_region = img2[int(h*0.55):int(h*0.75), int(w*0.35):int(w*0.65)]
    button_hsv = cv2.cvtColor(button_region, cv2.COLOR_BGR2HSV)
    orange_mask = cv2.inRange(button_hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
    orange_pixels = cv2.countNonZero(orange_mask)
    
    print(f"  中央白色文字: {white_pixels} (阈值>3000)")
    print(f"  中央深色背景: {dark_pixels} (阈值>20000)")
    print(f"  橙色按钮像素: {orange_pixels} (阈值>5000)")
    
    state = recognizer.detect_state(img2)
    print(f"  识别结果: {state.name}")
    if state == GameState.PURCHASE_FAILED:
        print("  ✅ 正确！识别为购买失败")
    else:
        print(f"  ❌ 错误！应该是PURCHASE_FAILED，实际是{state.name}")

print("\n" + "=" * 60)
