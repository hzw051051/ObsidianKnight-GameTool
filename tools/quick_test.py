import cv2
from src.image_recognition import ImageRecognizer

# 测试当前上传的截图
img = cv2.imread("C:/Users/28143/.gemini/antigravity/brain/4ad4d424-3e9d-4fc2-9bae-4d1736436b30/uploaded_image_1770475021053.png")
if img is None:
    print("无法加载图片")
else:
    recognizer = ImageRecognizer()
    state = recognizer.detect_state(img)
    print(f"识别结果: {state}")
    print(f"期望结果: GameState.LEVEL_PREPARE")
