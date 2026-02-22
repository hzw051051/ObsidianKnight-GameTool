"""
验证购买失败界面识别修复（测试战斗界面是否会误判）
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
from src.image_recognition import ImageRecognizer, GameState

# 测试上传的战斗界面图片
img_path = "C:/Users/28143/.gemini/antigravity/brain/f2afe9da-cfe0-41d3-ae19-d9e67d22acda/uploaded_image_1770503297741.png"

print("=" * 60)
print("测试购买失败界面识别修复")
print("=" * 60)

img = cv2.imread(img_path)
if img is None:
    print(f"❌ 无法加载图片: {img_path}")
else:
    recognizer = ImageRecognizer("templates")
    state = recognizer.detect_state(img)
    
    print(f"\n识别结果: {state.name}")
    
    if state == GameState.PURCHASE_FAILED:
        print("❌ 错误！战斗界面被误识别为购买失败")
    else:
        print(f"✅ 正确！识别为 {state.name}")
        print("   （应该是 OBSTACLE_CONTINUE 或 UNKNOWN 战斗状态）")

print("\n" + "=" * 60)
