import cv2
import numpy as np
import os

def survey_digits():
    img = cv2.imread("debug_screenshot.png")
    if img is None: return
    
    # 转换为灰度并二值化 (降低一点阈值以防万一)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    
    # 扫描上半部分 (y < 200)
    top_half = binary[:200, :]
    cv2.imwrite("debug_top_binary.png", top_half)
    
    contours, _ = cv2.findContours(top_half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    os.makedirs("templates/digits_survey", exist_ok=True)
    
    matches = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # ID文字通常高度在 20-30 像素之间
        if 15 < h < 45 and 4 < w < 40:
            matches.append((x, y, w, h))
            
    # 按x排序方便观察
    matches.sort()
    
    for i, (x, y, w, h) in enumerate(matches):
        digit_img = top_half[y:y+h, x:x+w]
        cv2.imwrite(f"templates/digits_survey/match_{i}_{x}_{y}.png", digit_img)
        print(f"Found Blob: x={x}, y={y}, w={w}, h={h} -> Saved as match_{i}.png")

if __name__ == "__main__":
    survey_digits()
