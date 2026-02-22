import cv2
import numpy as np
import os

paths = [
    'templates/ui/obstacle_specialbox.png',
    'C:/Users/28143/.gemini/antigravity/brain/0df11ffa-1831-4e22-bb9e-eac2604b91ce/uploaded_image_0_1770726731915.png',
    'C:/Users/28143/.gemini/antigravity/brain/0df11ffa-1831-4e22-bb9e-eac2604b91ce/uploaded_image_1_1770726731915.png',
    'C:/Users/28143/.gemini/antigravity/brain/0df11ffa-1831-4e22-bb9e-eac2604b91ce/uploaded_image_2_1770726731915.png'
]

for p in paths:
    img = cv2.imread(p)
    if img is None:
        print(f"Failed to load: {p}")
        continue
    img = cv2.resize(img, (1600, 900))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # OBSTACLE_SPECIALBOX region
    region = hsv[400:550, 725:875]
    gray = cv2.countNonZero(cv2.inRange(region, np.array([0, 0, 50]), np.array([180, 50, 200])))
    orange = cv2.countNonZero(cv2.inRange(region, np.array([10, 150, 150]), np.array([25, 255, 255])))
    
    print(f"File: {os.path.basename(p)}")
    print(f"  Gray: {gray}, Orange: {orange}")
    
    # Higher region (where the 0.45 confidence was found)
    # The circular button is usually higher up.
    # In the special box image, the button's "?" is around y=350, icon y=430.
    
    # Let's check a wider range for silver/gold presence which is typical for UI
    top_region_hsv = hsv[int(900*0.05):int(900*0.35), int(1600*0.3):int(1600*0.7)]
    gold = cv2.countNonZero(cv2.inRange(top_region_hsv, np.array([15, 80, 80]), np.array([40, 255, 255])))
    silver = cv2.countNonZero(cv2.inRange(top_region_hsv, np.array([0, 0, 150]), np.array([180, 50, 255])))
    print(f"  Top Gold: {gold}, Top Silver: {silver}")
