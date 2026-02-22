import cv2
import numpy as np

def test_retry_sift():
    templ = cv2.imread('templates/ui/btn_retry_banner.png')
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(templ, None)
    
    images = [
        ('C:/Users/28143/.gemini/antigravity/brain/0df11ffa-1831-4e22-bb9e-eac2604b91ce/uploaded_image_1770974995450.png', 'Dark Cards'),
        ('templates/ui/card_selection.png', 'Normal Cards'),
        ('templates/ui/victory.png', 'Victory'),
        ('templates/ui/level_prepare.png', 'Prepare')
    ]
    
    for path, label in images:
        img = cv2.imread(path)
        if img is None: continue
        img = cv2.resize(img, (1600, 900))
        # ROI for the retry button
        roi = img[700:, 1200:]
        kp2, des2 = sift.detectAndCompute(roi, None)
        
        if des2 is None:
            print(f"{label}: 0 matches")
            continue
            
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(des1, des2, k=2)
        good = [m for m, n in matches if len(matches) > 1 and m.distance < 0.7*n.distance]
        print(f"{label}: {len(good)} matches")

test_retry_sift()
