"""
GUI控制界面模块
提供简单的开始/停止控制面板
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from datetime import datetime


class GameAssistantGUI:
    """游戏助手控制界面"""
    
    def __init__(self, automation):
        """
        初始化GUI
        
        Args:
            automation: GameAutomation实例
        """
        self.automation = automation
        self.automation.set_callbacks(
            on_state_change=self._on_state_change,
            on_log=self._on_log
        )
        
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("黑曜石骑士游戏助手 V1")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # 设置图标（如果有的话）
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
        # 线程变量
        self._automation_thread = None
        
        # 日志行数计数器
        self._log_line_count = 0
        
        # 创建UI组件
        self._create_widgets()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_widgets(self):
        """创建UI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # === 状态区域 ===
        status_frame = ttk.LabelFrame(main_frame, text="状态", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 连接状态
        conn_frame = ttk.Frame(status_frame)
        conn_frame.pack(fill=tk.X)
        
        ttk.Label(conn_frame, text="模拟器连接:").pack(side=tk.LEFT)
        self.conn_label = ttk.Label(conn_frame, text="未连接", foreground="gray")
        self.conn_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(conn_frame, text="游戏状态:").pack(side=tk.LEFT)
        self.state_label = ttk.Label(conn_frame, text="等待开始", foreground="gray")
        self.state_label.pack(side=tk.LEFT, padx=5)
        
        # 统计信息
        stats_frame = ttk.Frame(status_frame)
        stats_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(stats_frame, text="完成轮次:").pack(side=tk.LEFT)
        self.runs_label = ttk.Label(stats_frame, text="0")
        self.runs_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(stats_frame, text="选择卡牌:").pack(side=tk.LEFT)
        self.cards_label = ttk.Label(stats_frame, text="0")
        self.cards_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(stats_frame, text="障碍物:").pack(side=tk.LEFT)
        self.obstacles_label = ttk.Label(stats_frame, text="0")
        self.obstacles_label.pack(side=tk.LEFT, padx=5)
        
        # === 控制按钮 ===
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.connect_btn = ttk.Button(
            btn_frame, text="连接模拟器", command=self._on_connect
        )
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.start_btn = ttk.Button(
            btn_frame, text="▶ 开始", command=self._on_start, state=tk.DISABLED
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            btn_frame, text="⏹ 停止", command=self._on_stop, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.reload_btn = ttk.Button(
            btn_frame, text="🔄 重载配置", command=self._on_reload
        )
        self.reload_btn.pack(side=tk.RIGHT)
        
        # === 日志区域 ===
        log_frame = ttk.LabelFrame(main_frame, text="日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, height=12, wrap=tk.WORD, state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 清除日志按钮
        ttk.Button(
            log_frame, text="清除日志", command=self._clear_log
        ).pack(anchor=tk.E, pady=(5, 0))
    
    def _on_connect(self):
        """连接模拟器"""
        self.connect_btn.config(state=tk.DISABLED)
        self._log("正在连接模拟器...")
        
        def connect_thread():
            success = self.automation.connect()
            self.root.after(0, lambda: self._on_connect_result(success))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def _on_connect_result(self, success: bool):
        """连接结果回调"""
        if success:
            self.conn_label.config(text="已连接", foreground="green")
            self.start_btn.config(state=tk.NORMAL)
            self._log("✓ 模拟器连接成功")
        else:
            self.conn_label.config(text="连接失败", foreground="red")
            self.connect_btn.config(state=tk.NORMAL)
            self._log("✗ 模拟器连接失败，请确保雷电模拟器已启动")
    
    def _on_start(self):
        """开始自动化"""
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.connect_btn.config(state=tk.DISABLED)
        
        def start_thread():
            self.automation.start()
        
        self._automation_thread = threading.Thread(target=start_thread, daemon=True)
        self._automation_thread.start()
    
    def _on_stop(self):
        """停止自动化"""
        self.automation.stop()
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
    
    def _on_reload(self):
        """重载配置"""
        self.automation.config.reload()
        self._log("✓ 配置已重新加载")
    
    def _on_state_change(self, state: str):
        """状态变化回调"""
        self.root.after(0, lambda: self._update_state(state))
    
    def _update_state(self, state: str):
        """更新状态显示"""
        self.state_label.config(text=state)
        
        # 更新统计
        stats = self.automation.stats
        self.runs_label.config(text=str(stats["runs"]))
        self.cards_label.config(text=str(stats["cards"]))
        self.obstacles_label.config(text=str(stats["obstacles"]))
    
    def _on_log(self, message: str):
        """日志回调"""
        self.root.after(0, lambda: self._log(message))
    
    def _log(self, message: str):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
        # 日志行数计数
        self._log_line_count += 1
        
        # 达到上限时自动清空
        max_lines = self.automation.config.max_log_lines
        if self._log_line_count >= max_lines:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self._log_line_count = 0
            # 重新插入清空提示
            timestamp = datetime.now().strftime("%H:%M:%S")
            clear_msg = f"[{timestamp}] ✅ 日志已自动清空（超过{max_lines}行）\n"
            self.log_text.insert(tk.END, clear_msg)
            self._log_line_count = 1  # 清空提示算一行
            self.log_text.config(state=tk.DISABLED)
    
    def _clear_log(self):
        """清除日志"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self._log_line_count = 0  # 重置计数器
        self.log_text.config(state=tk.DISABLED)
    
    def _on_close(self):
        """关闭窗口"""
        if self.automation.is_running:
            self.automation.stop()
        self.root.destroy()
    
    def run(self):
        """运行GUI主循环"""
        self._log("游戏助手已启动")
        self._log("请先点击「连接模拟器」按钮")
        self.root.mainloop()


# 测试代码
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.state_machine import GameAutomation
    
    automation = GameAutomation()
    gui = GameAssistantGUI(automation)
    gui.run()
