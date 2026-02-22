import cv2
import numpy as np
import os

def extract_and_save():
    img = cv2.imread("debug_screenshot.png")
    if img is None: return
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # 区域范围 (y: 100-120 左右是ID数字的顶端)
    # y=550是中心, y-440=110
    roi_y_start, roi_y_end = 100, 140
    rois = [
        (525, 645), # Card 1
        (840, 960), # Card 2
        (1140, 1260) # Card 3
    ]
    
    os.makedirs("templates/digits", exist_ok=True)
    
    for i, (x1, x2) in enumerate(rois):
        roi = binary[roi_y_start:roi_y_end, x1:x2]
        cv2.imwrite(f"debug_roi_{i}.png", roi)
        
        # 寻找轮廓
        contours, _ = cv2.findContours(roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # 按x排序
        digit_boxes = []
        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            if h > 10 and w > 2: # 过滤杂色
                digit_boxes.append((x, y, w, h))
        
        digit_boxes.sort()
        
        for j, (x, y, w, h) in enumerate(digit_boxes):
            digit_img = roi[y:y+h, x:x+w]
            cv2.imwrite(f"templates/digits/temp_{i}_{j}.png", digit_img)
            print(f"Saved: templates/digits/temp_{i}_{j}.png (Size: {w}x{h})")

if __name__ == "__main__":
    extract_and_save()
