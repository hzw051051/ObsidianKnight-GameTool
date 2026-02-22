import cv2
import numpy as np

img = cv2.imread('C:/Users/28143/.gemini/antigravity/brain/0df11ffa-1831-4e22-bb9e-eac2604b91ce/uploaded_image_1770953010437.png')
img = cv2.resize(img, (1600, 900))
h, w = img.shape[:2]
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Gold check
top_region_hsv = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
gold_mask = cv2.inRange(top_region_hsv, np.array([15, 80, 80]), np.array([40, 255, 255]))
gold_pixels = cv2.countNonZero(gold_mask)
print(f"Gold: {gold_pixels}")

# PURCHASE_FAILED block
center_text_region = img[int(h*0.35):int(h*0.55), int(w*0.3):int(w*0.7)]
center_gray = cv2.cvtColor(center_text_region, cv2.COLOR_BGR2GRAY)
white_text_pixels = cv2.countNonZero((center_gray > 200).astype(np.uint8))
dark_bg_pixels = cv2.countNonZero((center_gray < 80).astype(np.uint8))
print(f"White: {white_text_pixels}, Dark: {dark_bg_pixels}")

button_check_region = hsv[int(h*0.55):int(h*0.75), int(w*0.35):int(w*0.65)]
orange_mask = cv2.inRange(button_check_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
button_orange_pixels = cv2.countNonZero(orange_mask)
print(f"Button Orange: {button_orange_pixels}")

pf_x, pf_y = 800, 640
pf_rect = hsv[pf_y-30:pf_y+30, pf_x-100:pf_x+100]
pf_orange_mask = cv2.inRange(pf_rect, np.array([10, 120, 120]), np.array([25, 255, 255]))
pf_density = cv2.countNonZero(pf_orange_mask) / (pf_rect.size/3)
print(f"Density: {pf_density:.4f}")

if white_text_pixels > 2000 and dark_bg_pixels > 20000 and button_orange_pixels > 5000:
    print("Passes primary check")
    if 0.5 < pf_density < 0.9:
        print("MATCH: PURCHASE_FAILED")
    else:
        print(f"Fails density check ({pf_density:.4f} not in [0.5, 0.9])")
else:
    print("Fails primary check")
