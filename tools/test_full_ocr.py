import cv2
import numpy as np
from paddleocr import PaddleOCR

def test_full_ocr():
    # 移除 show_log 尝试解决初始化失败
    try:
        ocr = PaddleOCR(use_angle_cls=False, lang='ch')
    except Exception as e:
        print(f"OCR Init Error: {e}")
        return

    img = cv2.imread("debug_screenshot.png")
    if img is None:
        print("Image not found")
        return

    print("Running full OCR...")
    result = ocr.ocr(img)
    
    for line in result:
        for word in line:
            bbox = word[0]
            text = word[1][0]
            conf = word[1][1]
            print(f"Text: {text}, Conf: {conf:.2f}, BBox: {bbox}")

if __name__ == "__main__":
    test_full_ocr()
