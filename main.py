"""
黑曜石骑士游戏助手 V1
主程序入口

使用方法：
1. 启动雷电模拟器并打开游戏
2. 进入关卡准备界面
3. 运行本程序: python main.py
4. 点击「连接模拟器」按钮
5. 点击「开始」按钮开始自动刷本
6. 点击「停止」按钮停止自动化
"""
import os
import sys
import multiprocessing
import traceback
from pathlib import Path
from datetime import datetime

# --- 极速日志记录逻辑 ---
def log_debug(msg):
    try:
        with open("error.log", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] [PID:{os.getpid()}] {msg}\n")
    except:
        pass

log_debug(f"程序启动 (main.py) - 参数: {sys.argv}")

# 确保源码目录在路径中
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

from src.state_machine import GameAutomation
from src.gui import GameAssistantGUI


def main():
    """主函数"""
    # 切换工作目录到程序所在目录
    os.chdir(src_dir)
    
    # 创建自动化实例
    automation = GameAutomation(
        config_dir="config",
        templates_dir="templates"
    )
    
    # 创建并运行GUI
    gui = GameAssistantGUI(automation)
    gui.run()


if __name__ == "__main__":
    # Nuitka/PyInstaller 打包支持
    multiprocessing.freeze_support()
    main()
