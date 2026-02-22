import cv2
import numpy as np

img = cv2.imread('templates/ui/enter_level_up.png')
img = cv2.resize(img, (1600, 900))
h, w = img.shape[:2]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# beige_pixels logic from image_recognition.py
description_region = hsv[int(h*0.5):int(h*0.75), int(w*0.1):int(w*0.9)]
beige_mask = cv2.inRange(description_region, np.array([15, 5, 180]), np.array([35, 80, 255]))
beige_pixels = cv2.countNonZero(beige_mask)

# retry_pixels logic
bottom_right_region = hsv[int(h*0.7):, int(w*0.7):]
retry_btn_mask = cv2.inRange(bottom_right_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
retry_pixels = cv2.countNonZero(retry_btn_mask)

# dark_pixels logic
bottom_left_panel = img[int(h*0.5):, :int(w*0.25)]
bl_hsv = cv2.cvtColor(bottom_left_panel, cv2.COLOR_BGR2HSV)
dark_mask = cv2.inRange(bl_hsv, np.array([0, 0, 0]), np.array([180, 255, 80]))
dark_pixels = cv2.countNonZero(dark_mask)

print(f"Beige: {beige_pixels}")
print(f"Retry: {retry_pixels}")
print(f"Dark: {dark_pixels}")
