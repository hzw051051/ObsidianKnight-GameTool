import cv2
import numpy as np

# 从之前的卡牌选择截图中提取132的ID模板
img = cv2.imread("C:/Users/28143/.gemini/antigravity/brain/4ad4d424-3e9d-4fc2-9bae-4d1736436b30/uploaded_image_1770476376872.png")

if img is not None:
    # 第三张卡的ID位置（根据1600x900分辨率）
    # x=1200, y=550 (卡牌中心)
    # ID在上方约y-440的位置
    x, y = 1200, 550
    
    # ID区域（更精确的位置）
    h, w = img.shape[:2]
    left, top = max(0, x - 100), max(0, y - 450)
    right, bottom = min(w, x + 100), min(h, y - 370)
    
    print(f"提取区域: ({left},{top}) 到 ({right},{bottom})")
    id_region = img[top:bottom, left:right]
    
    if id_region.size == 0:
        print("区域为空，调整参数...")
        # 使用更保守的区域
        left, top = 1100, 100
        right, bottom = 1300, 150
        id_region = img[top:bottom, left:right]
    
    # 转为灰度并二值化
    gray = cv2.cvtColor(id_region, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    
    # 找到轮廓并提取紧凑的边界
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        all_pts = np.vstack([cnt for cnt in contours])
        bx, by, bw, bh = cv2.boundingRect(all_pts)
        final_roi = id_region[by:by+bh, bx:bx+bw]
        
        cv2.imwrite("templates/cards/132.png", final_roi)
        print(f"已创建 132.png 模板 ({bw}x{bh})")
    else:
        print("未找到132的ID文字")
else:
    print("无法读取截图")
