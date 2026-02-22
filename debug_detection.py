"""
调试特定图片的识别问题
"""
import cv2
import numpy as np
import sys
import os
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, os.getcwd())
from src.image_recognition import ImageRecognizer, GameState

def debug_image(image_path, template_name):
    print(f"Loading image: {image_path}")
    img_orig = cv2.imread(image_path)
    if img_orig is None:
        print("Failed to load image")
        return

    # 1600x900
    img = cv2.resize(img_orig, (1600, 900))
    
    recognizer = ImageRecognizer()
    
    # 1. 尝试检测状态
    state = recognizer.detect_state(img)
    print(f"Detected State: {state.name}")
    
    # 2. 检查模板是否存在
    if template_name not in recognizer.templates:
        print(f"Template '{template_name}' not found in loaded templates!")
        print(f"Loaded templates: {list(recognizer.templates.keys())}")
        return
        
    template = recognizer.templates[template_name]
    print(f"Template size: {template.shape}")
    
    # 3. 手动执行模板匹配并输出置信度
    result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    print(f"Max Confidence for '{template_name}': {max_val:.4f}")
    
    if max_val < 0.8:
        print("Confidence is below threshold 0.8")
    else:
        print(f"Found at: {max_loc}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python debug_detection.py <image_path> <template_name>")
    else:
        debug_image(sys.argv[1], sys.argv[2])
