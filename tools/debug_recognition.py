import cv2
import numpy as np
from src.image_recognition import ImageRecognizer, GameState

def debug_state():
    recognizer = ImageRecognizer()
    screen = cv2.imread("debug_screenshot.png")
    if screen is None:
        print("无法读取 debug_screenshot.png")
        return

    h, w = screen.shape[:2]
    hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    
    # 橙色检测
    orange_lower = np.array([10, 150, 150])
    orange_upper = np.array([25, 255, 255])
    orange_mask = cv2.inRange(hsv, orange_lower, orange_upper)
    bottom_region = orange_mask[int(h*0.7):, :]
    bottom_orange_pixels = cv2.countNonZero(bottom_region)
    print(f"底部橙色像素数: {bottom_orange_pixels}")
    
    # 绿色检测 (胜利界面)
    victory_region = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
    green_lower = np.array([35, 80, 80])
    green_upper = np.array([85, 255, 255])
    green_mask = cv2.inRange(victory_region, green_lower, green_upper)
    green_pixels = cv2.countNonZero(green_mask)
    print(f"顶部绿色像素数: {green_pixels}")
    
    # 银色检测 (卡牌界面)
    center_region = screen[int(h*0.1):int(h*0.7), int(w*0.1):int(w*0.9)]
    gray_center = cv2.cvtColor(center_region, cv2.COLOR_BGR2GRAY)
    white_mask = cv2.inRange(gray_center, 180, 255)
    print(f"中央白色/银色像素数: {cv2.countNonZero(white_mask)}")
    
    # 英语按钮检测 (左上角，扩大范围)
    top_left_region = hsv[:int(h*0.3), :int(w*0.3)]
    english_btn_mask = cv2.inRange(top_left_region, np.array([10, 100, 100]), np.array([25, 255, 255]))
    print(f"左上角英语按钮区域像素数: {cv2.countNonZero(english_btn_mask)}")
    
    # 金色检测 (顶部选项)
    top_region_hsv = hsv[int(h*0.05):int(h*0.35), int(w*0.2):int(w*0.8)]
    gold_mask = cv2.inRange(top_region_hsv, np.array([15, 80, 80]), np.array([40, 255, 255]))
    print(f"顶部金色像素数: {cv2.countNonZero(gold_mask)}")

    state = recognizer.detect_state(screen)
    print(f"识别到的最终状态: {state}")

if __name__ == "__main__":
    debug_state()
