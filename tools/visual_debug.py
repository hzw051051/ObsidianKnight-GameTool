"""
可视化调试工具 - 实时显示识别过程和各区域检测结果
使用方法：python tools/visual_debug.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from src.adb_controller import ADBController
from src.image_recognition import ImageRecognizer, GameState
import time

def draw_detection_regions(img, results):
    """在图像上绘制检测区域和结果"""
    overlay = img.copy()
    h, w = img.shape[:2]
    
    # 1. 底部橙色按钮区域
    cv2.rectangle(overlay, (0, int(h*0.7)), (w, h), (0, 165, 255), 2)
    cv2.putText(overlay, f"Bottom Orange: {results.get('bottom_orange', 0)}", 
                (10, int(h*0.7)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)
    
    # 2. 左上角英语按钮
    cv2.rectangle(overlay, (0, 0), (int(w*0.3), int(h*0.3)), (0, 255, 255), 2)
    cv2.putText(overlay, f"English Btn: {results.get('english_btn', 0)}", 
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
    
    # 3. 右侧继续按钮
    cv2.rectangle(overlay, (int(w*0.85), int(h*0.2)), (w, int(h*0.4)), (255, 0, 255), 2)
    cv2.putText(overlay, f"Continue Btn: {results.get('continue_btn', 0)}", 
                (int(w*0.85)-150, int(h*0.2)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    
    # 4. 中间人物区域（新增）
    cv2.rectangle(overlay, (int(w*0.3), int(h*0.3)), (int(w*0.7), int(h*0.7)), (0, 255, 0), 2)
    cv2.putText(overlay, f"Center Character: {results.get('center_char', 0)}", 
                (int(w*0.3)+10, int(h*0.3)+30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # 5. 左下角属性面板
    cv2.rectangle(overlay, (0, int(h*0.5)), (int(w*0.25), h), (255, 255, 0), 2)
    cv2.putText(overlay, f"Attribute Panel: {results.get('attr_panel', 0)}", 
                (10, int(h*0.5)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    
    # 6. Best time区域
    cv2.rectangle(overlay, (0, int(h*0.85)), (int(w*0.15), int(h*0.95)), (128, 0, 128), 2)
    cv2.putText(overlay, f"Best Time: W{results.get('best_time_white', 0)} D{results.get('best_time_dark', 0)}", 
                (10, int(h*0.85)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (128, 0, 128), 2)
    
    # 显示最终识别结果
    state_text = f"State: {results.get('state', 'UNKNOWN')}"
    cv2.putText(overlay, state_text, (int(w/2)-150, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
    
    return cv2.addWeighted(overlay, 0.7, img, 0.3, 0)

def collect_detection_data(screen, recognizer):
    """收集所有检测区域的数据"""
    h, w = screen.shape[:2]
    hsv = cv2.cvtColor(screen, cv2.COLOR_BGR2HSV)
    results = {}
    
    # 底部橙色
    orange_mask = cv2.inRange(hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
    bottom_region = orange_mask[int(h*0.7):, :]
    results['bottom_orange'] = cv2.countNonZero(bottom_region)
    
    # 左上角英语按钮
    top_left_region = hsv[:int(h*0.3), :int(w*0.3)]
    english_btn_mask = cv2.inRange(top_left_region, np.array([10, 100, 100]), np.array([25, 255, 255]))
    results['english_btn'] = cv2.countNonZero(english_btn_mask)
    
    # 右侧继续按钮（扩大检测范围避免移动影响）
    right_region = screen[int(h*0.2):int(h*0.4), int(w*0.85):]
    right_hsv = cv2.cvtColor(right_region, cv2.COLOR_BGR2HSV)
    continue_mask = cv2.inRange(right_hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
    results['continue_btn'] = cv2.countNonZero(continue_mask)
    
    # 中间人物区域（检测非背景像素）
    center_region = screen[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
    center_gray = cv2.cvtColor(center_region, cv2.COLOR_BGR2GRAY)
    # 非橙色背景的像素（人物、障碍物等）
    _, center_obj = cv2.threshold(center_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    results['center_char'] = cv2.countNonZero(center_obj)
    
    # 左下角属性面板
    bottom_left = screen[int(h*0.5):, :int(w*0.25)]
    bl_hsv = cv2.cvtColor(bottom_left, cv2.COLOR_BGR2HSV)
    dark_mask = cv2.inRange(bl_hsv, np.array([0, 0, 0]), np.array([180, 255, 80]))
    results['attr_panel'] = cv2.countNonZero(dark_mask)
    
    # Best time区域
    best_time_region = screen[int(h*0.85):int(h*0.95), :int(w*0.15)]
    bt_gray = cv2.cvtColor(best_time_region, cv2.COLOR_BGR2GRAY)
    results['best_time_white'] = cv2.countNonZero((bt_gray > 200).astype(np.uint8))
    results['best_time_dark'] = cv2.countNonZero((bt_gray < 60).astype(np.uint8))
    
    # 执行识别
    state = recognizer.detect_state(screen)
    results['state'] = state.name
    
    return results

def main():
    print("=== 可视化调试工具 ===")
    print("按 'q' 退出，按 's' 保存当前截图和数据")
    
    adb = ADBController()
    if not adb.connect():
        print("无法连接到模拟器！")
        return
    
    recognizer = ImageRecognizer()
    
    while True:
        # 截图
        pil_screen = adb.screenshot()
        if pil_screen is None:
            print("截图失败")
            time.sleep(1)
            continue
        
        # 转换为numpy数组
        screen = np.array(pil_screen)
        screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
        
        # 收集检测数据
        results = collect_detection_data(screen, recognizer)
        
        # 绘制可视化
        vis_img = draw_detection_regions(screen, results)
        
        # 缩放显示（适应屏幕）
        display_img = cv2.resize(vis_img, (1200, 675))
        
        # 显示
        cv2.imshow('Recognition Debug', display_img)
        
        # 打印数据
        print(f"\r[{results['state']}] Orange:{results['bottom_orange']} English:{results['english_btn']} "
              f"Continue:{results['continue_btn']} Center:{results['center_char']} "
              f"Attr:{results['attr_panel']}", end='')
        
        # 键盘控制
        key = cv2.waitKey(500) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            timestamp = int(time.time())
            cv2.imwrite(f"debug_visual_{timestamp}.png", vis_img)
            with open(f"debug_data_{timestamp}.txt", 'w', encoding='utf-8') as f:
                for k, v in results.items():
                    f.write(f"{k}: {v}\n")
            print(f"\n已保存: debug_visual_{timestamp}.png")
    
    cv2.destroyAllWindows()
    print("\n调试结束")

if __name__ == "__main__":
    main()
