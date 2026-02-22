"""
在截图上标注当前配置的坐标位置
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.adb_controller import ADBController
from src.config_loader import Config
import cv2
import numpy as np

print("=" * 60)
print("坐标可视化工具")
print("=" * 60)

# 连接ADB
adb = ADBController('127.0.0.1', 5554)
if not adb.connect():
    print("❌ 无法连接模拟器")
    sys.exit(1)

# 加载配置
config = Config()

# 截图
screen = adb.screenshot()
if screen is None:
    print("❌ 截图失败")
    sys.exit(1)

screen_np = np.array(screen)
screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
h, w = screen_bgr.shape[:2]

print(f"模拟器分辨率: {w}x{h}\n")

# 在图上标注坐标点
def draw_point(img, pos, label, color):
    x, y = pos
    # 画十字
    cv2.drawMarker(img, (x, y), color, cv2.MARKER_CROSS, 30, 2)
    # 画圆
    cv2.circle(img, (x, y), 15, color, 2)
    # 添加标签
    cv2.putText(img, f"{label} ({x},{y})", (x+20, y-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

# 标注各个坐标
draw_point(screen_bgr, config.btn_start_pos, "Start", (0, 255, 0))
draw_point(screen_bgr, config.btn_retry_pos, "Retry", (255, 0, 0))
draw_point(screen_bgr, config.btn_continue_pos, "Continue", (0, 0, 255))
draw_point(screen_bgr, config.btn_purchase_confirm_pos, "Confirm", (255, 255, 0))

draw_point(screen_bgr, config.btn_level_up_pos, "Level", (255, 255, 255))
draw_point(screen_bgr, config.btn_cancel_purchase_pos, "Cancel", (0, 0, 0))

# 标注卡牌位置
for i, pos in enumerate(config.card_positions):
    draw_point(screen_bgr, pos, f"Card{i+1}", (255, 0, 255))

# 标注选项位置
for i, pos in enumerate(config.choice_positions):
    draw_point(screen_bgr, pos, f"Choice{i+1}", (0, 255, 255))

# 保存
output_file = "coordinates_visualization.png"
cv2.imwrite(output_file, screen_bgr)

print(f"✅ 可视化图片已保存: {output_file}")
print("\n请打开图片查看坐标位置是否正确！")
print("=" * 60)
