import cv2
import time
from src.image_recognition import ImageRecognizer

def test_ocr():
    recognizer = ImageRecognizer()
    screen = cv2.imread("debug_screenshot.png")
    if screen is None:
        print("无法读取 debug_screenshot.png")
        return

    # 定义卡牌坐标 (基于1600x900)
    card_positions = [(585, 550), (900, 550), (1200, 550)]
    
    print("--- 开始 OCR 识别测试 ---")
    start_time = time.time()
    
    # 第一次识别（包含初始化）
    ids = recognizer.detect_card_ids(screen, card_positions)
    init_duration = time.time() - start_time
    print(f"首次识别结果: {ids}")
    print(f"首次识别耗时 (含初始化): {init_duration:.2f}s")
    
    # 第二次识别（热启动测试）
    start_time = time.time()
    ids = recognizer.detect_card_ids(screen, card_positions)
    hot_duration = time.time() - start_time
    print(f"再次识别结果: {ids}")
    print(f"热启动识别耗时: {hot_duration:.2f}s")

if __name__ == "__main__":
    test_ocr()
