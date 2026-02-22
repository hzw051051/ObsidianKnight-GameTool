import cv2
import numpy as np

def test_sift():
    img = cv2.imread('C:/Users/28143/.gemini/antigravity/brain/0df11ffa-1831-4e22-bb9e-eac2604b91ce/uploaded_image_1770817145644.png')
    img = cv2.resize(img, (1600, 900))
    roi = img[250:650, 600:1000]
    
    templ = cv2.imread('templates/ui/btn_specialbox_circle.png')
    
    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(templ, None)
    kp2, des2 = sift.detectAndCompute(roi, None)
    
    if des1 is None or des2 is None:
        print("No descriptors found")
        return
        
    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)
    
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
            
    print(f"SIFT Good matches: {len(good)}")

    # ORB test
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(templ, None)
    kp2, des2 = orb.detectAndCompute(roi, None)
    if des1 is not None and des2 is not None:
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des1, des2)
        print(f"ORB matches: {len(matches)}")

test_sift()
