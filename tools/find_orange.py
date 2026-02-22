import cv2
import numpy as np

def find_orange():
    img = cv2.imread('debug_screenshot.png')
    if img is None:
        print("Error: Could not load debug_screenshot.png")
        return
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 橙色范围
    lower = np.array([10, 100, 100])
    upper = np.array([25, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    
    # 寻找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area > 1000:
            x, y, w, h = cv2.boundingRect(cnt)
            print(f"Cluster {i}: Area={area}, BBox=({x},{y},{w},{h}), Center=({x+w//2}, {y+h//2})")

if __name__ == "__main__":
    find_orange()
