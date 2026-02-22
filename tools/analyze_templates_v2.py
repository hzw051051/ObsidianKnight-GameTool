"""
分析 UI 模板图片，提取特征
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cv2
import numpy as np
from pathlib import Path
from src.image_recognition import ImageRecognizer, GameState

def analyze_image(name, img_path, recognizer):
    print(f"\n{'='*20} 分析: {name} {'='*20}")
    img_orig = cv2.imread(str(img_path))
    if img_orig is None:
        print("无法加载图片")
        return
        
    # 强制缩放到 1600x900 以匹配逻辑
    img = cv2.resize(img_orig, (1600, 900))

    # 1. 运行当前检测逻辑
    state = recognizer.detect_state(img)
    print(f"当前识别结果: {state.name}")

    h, w = img.shape[:2]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # 2. 分析各个特征区域
    print("\n[特征区域分析]")

    # 底部橙色 (通用)
    orange_mask = cv2.inRange(hsv, np.array([10, 150, 150]), np.array([25, 255, 255]))
    bottom_region = orange_mask[int(h*0.7):, :]
    print(f"底部橙色像素: {cv2.countNonZero(bottom_region)}")

    # 障碍物选择 - 顶部金色
    top_region_hsv = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
    gold_mask = cv2.inRange(top_region_hsv, np.array([15, 80, 80]), np.array([40, 255, 255]))
    # 银色 (用于识别障碍物选择框的标题部分)
    silver_mask = cv2.inRange(top_region_hsv, np.array([0, 0, 150]), np.array([180, 50, 255]))
    print(f"顶部金色像素 (障碍物): {cv2.countNonZero(gold_mask)}")
    print(f"顶部银色像素 (障碍物框): {cv2.countNonZero(silver_mask)}")
    
    # 购买失败确认按钮密度检测 (中心点 800, 640)
    pf_x, pf_y = 800, 640
    pf_rect = hsv[pf_y-30:pf_y+30, pf_x-100:pf_x+100]
    pf_orange_mask = cv2.inRange(pf_rect, np.array([10, 120, 120]), np.array([25, 255, 255]))
    print(f"购买失败按钮橙色密度: {cv2.countNonZero(pf_orange_mask) / (pf_rect.size/3):.2f}")
    
    # 障碍物选择 - 左下深色
    bottom_left = img[int(h*0.5):, :int(w*0.25)]
    bl_hsv = cv2.cvtColor(bottom_left, cv2.COLOR_BGR2HSV)
    dark_mask = cv2.inRange(bl_hsv, np.array([0, 0, 0]), np.array([180, 255, 80]))
    print(f"左下深色像素 (障碍物): {cv2.countNonZero(dark_mask)}")

    # 蓝色"选择2个"图标 (左下角)
    # 区域: [0.7h:0.85h, 0:0.15w] -> [630:765, 0:240] (1600x900)
    blue_icon_region = hsv[int(h*0.7):int(h*0.85), :int(w*0.15)]
    blue_mask = cv2.inRange(blue_icon_region, np.array([100, 100, 100]), np.array([130, 255, 255]))
    blue_mask = cv2.inRange(blue_icon_region, np.array([100, 100, 100]), np.array([130, 255, 255]))
    print(f"左下蓝色图标像素 (双选): {cv2.countNonZero(blue_mask)}")

    # 卡牌选择按钮
    top_left_region = hsv[:int(h*0.3), :int(w*0.3)]
    english_btn_mask = cv2.inRange(top_left_region, np.array([10, 100, 100]), np.array([25, 255, 255]))
    print(f"左上英语按钮像素: {cv2.countNonZero(english_btn_mask)}")

    bottom_right_region = hsv[int(h*0.7):, int(w*0.7):]
    retry_btn_mask = cv2.inRange(bottom_right_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
    print(f"右下重投按钮像素: {cv2.countNonZero(retry_btn_mask)}")
    
    # 障碍物继续按钮 (右侧灰色条块)
    right_mid_region = hsv[int(h*0.3):int(h*0.6), int(w*0.8):]
    gray_mask = cv2.inRange(right_mid_region, np.array([0, 0, 50]), np.array([180, 50, 200]))
    print(f"右侧灰色像素 (全域): {cv2.countNonZero(gray_mask)}")
    
    # 障碍物继续按钮特定位置密度 (1470, 305)
    cont_x, cont_y = 1470, 305
    cont_rect = hsv[cont_y-30:cont_y+30, cont_x-20:cont_x+20]
    cont_gray_mask = cv2.inRange(cont_rect, np.array([0, 0, 50]), np.array([180, 50, 200]))
    print(f"继续按钮灰色密度: {cv2.countNonZero(cont_gray_mask) / (cont_rect.size/3):.2f}")
    
    # 卡牌描述区域 (米色背景)
    # 区域: [0.5h:0.75h, 0.1w:0.9w] (下半部分)
    description_region = hsv[int(h*0.5):int(h*0.75), int(w*0.1):int(w*0.9)]
    # 米色/浅黄色: H[15-35], S[5-60], V[180-255]
    beige_mask = cv2.inRange(description_region, np.array([15, 5, 180]), np.array([35, 80, 255]))
    print(f"中部米色像素 (卡牌描述): {cv2.countNonZero(beige_mask)}")

    # 胜利界面绿色横幅
    # 区域: [0.05h:0.35h, 0.3w:0.7w]
    victory_region = hsv[int(h*0.05):int(h*0.35), int(w*0.3):int(w*0.7)]
    green_lower = np.array([35, 80, 80])
    green_upper = np.array([85, 255, 255])
    green_mask = cv2.inRange(victory_region, green_lower, green_upper)
    print(f"顶部绿色像素 (胜利): {cv2.countNonZero(green_mask)}")

    # 卡牌描述区域 (米色背景)
    # 区域: [0.5h:0.75h, 0.1w:0.9w] (下半部分)
    description_region = hsv[int(h*0.5):int(h*0.75), int(w*0.1):int(w*0.9)]
    # 米色/浅黄色: H[15-35], S[5-60], V[180-255]
    beige_mask = cv2.inRange(description_region, np.array([15, 5, 180]), np.array([35, 80, 255]))
    print(f"中部米色像素 (卡牌描述): {cv2.countNonZero(beige_mask)}")

    # 关卡准备界面开始按钮 (底部中间黄色)
    # 区域: [0.8h:0.95h, 0.4w:0.6w]
    start_btn_region = hsv[int(h*0.8):int(h*0.95), int(w*0.4):int(w*0.6)]
    start_btn_mask = cv2.inRange(start_btn_region, np.array([15, 100, 100]), np.array([40, 255, 255]))
    print(f"底部开始按钮像素 (准备): {cv2.countNonZero(start_btn_mask)}")

    print(f"图片尺寸: {w}x{h}")

    # ... (previous code)

    # 购买界面 - 关闭按钮区域 (右上角)
    # config: btn_cancel_purchase_pos: [1520, 80]
    # 检查 1520, 80 周围是否是红色/橙色关闭按钮
    x, y = 1520, 80
    x1, y1 = max(0, x-40), max(0, y-40)
    x2, y2 = min(w, x+40), min(h, y+40)
    
    if x1 < x2 and y1 < y2:
        cancel_btn_region = hsv[y1:y2, x1:x2]
        if cancel_btn_region.size > 0:
            red_mask1 = cv2.inRange(cancel_btn_region, np.array([0, 100, 100]), np.array([10, 255, 255]))
            red_mask2 = cv2.inRange(cancel_btn_region, np.array([160, 100, 100]), np.array([180, 255, 255]))
            cancel_btn_pixels = cv2.countNonZero(red_mask1) + cv2.countNonZero(red_mask2)
            print(f"右上关闭按钮红色像素 (购买): {cancel_btn_pixels}")
        else:
             print("右上关闭按钮区域为空")
    else:
        print(f"右上关闭按钮区域无效: {x1}:{x2}, {y1}:{y2}")

    # ...

    # 升级界面 - 升级按钮区域
    # config: btn_level_up_pos: [800, 780]
    x, y = 800, 780
    x1, y1 = max(0, x-100), max(0, y-40)
    x2, y2 = min(w, x+100), min(h, y+40)
    
    if x1 < x2 and y1 < y2:
        level_up_btn_region = hsv[y1:y2, x1:x2]
        if level_up_btn_region.size > 0:
            level_up_orange_mask = cv2.inRange(level_up_btn_region, np.array([10, 150, 150]), np.array([25, 255, 255]))
            print(f"下方升级按钮橙色像素 (升级): {cv2.countNonZero(level_up_orange_mask)}")
        else:
            print("下方升级按钮区域为空")
    else:
        print(f"下方升级按钮区域无效: {x1}:{x2}, {y1}:{y2}")

    # 关卡准备界面 - Best Time 区域
    # 区域: [0.85h:0.95h, 0:0.15w]
    best_time_region = img[int(h*0.85):int(h*0.95), :int(w*0.15)]
    bt_gray = cv2.cvtColor(best_time_region, cv2.COLOR_BGR2GRAY)
    white_text = cv2.countNonZero((bt_gray > 200).astype(np.uint8))
    dark_bg = cv2.countNonZero((bt_gray < 60).astype(np.uint8))
    print(f"Best Time区域: 白色文字={white_text}, 深色背景={dark_bg}")
    
    return state.name

def main():
    templates_dir = Path("templates")
    recognizer = ImageRecognizer()

    # 使用 rglob 递归查找所有子文件夹中的 png 图片
    files = sorted(list(templates_dir.rglob("*.png")))
    # 过滤掉 cards 文件夹中的小图以及 ui 文件夹中的一些非全屏小模板
    exclude_keywords = ["cards", "card_frame", "choice_box", "btn_cancel", "btn_level_up", "english_btn", "digits_survey"]
    files = [f for f in files if not any(kw in str(f) for kw in exclude_keywords)]
    results = []
    
    for f in files:
        state_name = analyze_image(f.name, f, recognizer)
        results.append({'file': f.name, 'state': state_name})

    print("\n" + "="*50)
    print("最终识别结果汇总")
    print("="*50)
    print(f"{'图片文件':<30} | {'识别结果':<20}")
    print("-" * 52)
    
    correct_count = 0
    total_count = 0
    
    expected_states_map = {
        "card_selection": "CARD_SELECTION",
        "card_selection_multiple": "CARD_SELECTION",
        "issue_card_selection_stuck": "CARD_SELECTION",
        "level_prepare": "LEVEL_PREPARE",
        "level_up": "LEVEL_UP",
        "level_up_after": "LEVEL_UP_AFTER",
        "obstacle_choice": "OBSTACLE_CHOICE",
        "issue_obstacle_choice_stuck": "OBSTACLE_CHOICE",
        "issue_card_selection_misidentified_as_prepare": "CARD_SELECTION",
        "issue_obstacle_choice_normal": "OBSTACLE_CHOICE",
        "issue_running_misidentified_as_choice": "UNKNOWN",
        "obstacle_continue": "OBSTACLE_CONTINUE",
        "purchase": "PURCHASE",
        "purchase_failed": "PURCHASE_FAILED",
        "victory": "VICTORY"
    }

    for result in results:
        fname = Path(result['file']).stem
        detected = result['state']
        
        # 修正匹配逻辑
        expected = "UNKNOWN"
        # 优先完全匹配
        if fname in expected_states_map:
             expected = expected_states_map[fname]
        else:
            # 尝试前缀匹配
            for key, val in expected_states_map.items():
                if fname.startswith(key):
                    expected = val
                    break
        
        is_match = (detected == expected)
        mark = "✅" if is_match else "❌"
        if is_match: correct_count += 1
        total_count += 1
        
        print(f"{fname:<30} | {detected:<20} {mark} (预期: {expected})")
        
    print("-" * 52)
    print(f"准确率: {correct_count}/{total_count} ({correct_count/total_count*100:.1f}%)")
    print("="*50)

if __name__ == "__main__":
    main()
