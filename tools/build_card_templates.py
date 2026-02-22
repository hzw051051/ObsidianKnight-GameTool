import cv2
import numpy as np
import os

def build_card_templates():
    img = cv2.imread("debug_screenshot.png")
    if img is None: return
    
    os.makedirs("templates/cards", exist_ok=True)
    
    # 根据 1600x900 下的卡牌中心位置
    # Card 1: 585, 550  -> ID: 159
    # Card 2: 900, 550  -> ID: 103
    # Card 3: 1200, 550 -> ID: 85 (或者根据 survey, Card 3 其实在更右边?)
    # 让我们根据 survey 结果调优位置:
    # ROI 1: x=506 (ID Start)
    # ROI 2: x=917 (ID Start)
    # ROI 3: x=1302 (ID Start)
    
    id_rects = [
        ("159", (500, 100, 160, 45)), # x, y, w, h
        ("103", (910, 100, 120, 50)),
        ("85", (1300, 110, 100, 50))
    ]
    
    for name, (x, y, w, h) in id_rects:
        roi = img[y:y+h, x:x+w]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
        
        # 寻找文字轮廓以进一步精简
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # 合并所有文字轮廓
            all_pts = np.vstack([cnt for cnt in contours])
            bx, by, bw, bh = cv2.boundingRect(all_pts)
            final_roi = roi[by:by+bh, bx:bx+bw]
            cv2.imwrite(f"templates/cards/{name}.png", final_roi)
            print(f"Saved Template: {name}.png ({bw}x{bh})")

if __name__ == "__main__":
    build_card_templates()
