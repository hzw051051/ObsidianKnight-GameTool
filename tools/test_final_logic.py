import cv2
import time
from src.image_recognition import ImageRecognizer
from src.config_loader import Config

def final_test():
    print("--- 启动最终闭环验证 (轻量化图标识别方案) ---")
    recognizer = ImageRecognizer()
    config = Config()
    
    img = cv2.imread("debug_screenshot.png")
    if img is None: 
        print("错误: 未找到测试截图")
        return

    card_positions = [(585, 550), (900, 550), (1200, 550)]
    
    start_time = time.perf_counter()
    card_ids = recognizer.detect_card_ids(img, card_positions, config.card_weights)
    duration = (time.perf_counter() - start_time) * 1000 # 毫秒
    
    print(f"识别耗时: {duration:.2f} 毫秒") # 应该在 1-10ms 左右
    print(f"检测到的ID列表: {card_ids}")
    
    # 模拟决策
    from src.state_machine import GameStateMachine
    from unittest.mock import MagicMock
    
    # 简单的伪装状态机进行决策测试
    sm = GameStateMachine(MagicMock())
    sm.config = config
    best_index = sm._select_best_card(card_ids)
    print(f"决策结果: 选择第 {best_index + 1} 张卡牌 (ID: {card_ids[best_index]})")
    
    if card_ids == ['159', '103', '85']:
        print("✅ ID识别完全正确!")
    else:
        print("❌ ID识别不完整，请检查模板库。")

if __name__ == "__main__":
    final_test()
