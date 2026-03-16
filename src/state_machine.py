"""
状态机模块
控制游戏自动化的核心逻辑
"""
import time
import random
from typing import Optional, Callable, List
import threading  # 新增：多线程支持

from .adb_controller import ADBController
from .image_recognition import ImageRecognizer, GameState
from .config_loader import Config

# --- 极速日志记录逻辑 ---
def log_debug(msg):
    try:
        import os
        from datetime import datetime
        with open("error.log", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] [PID:{os.getpid()}] [StateMachine] {msg}\n")
    except:
        pass


class GameAutomation:
    """游戏自动化控制器"""
    
    def __init__(self, config_dir: str = "config", templates_dir: str = "templates"):
        """
        初始化游戏自动化
        
        Args:
            config_dir: 配置目录
            templates_dir: 模板图片目录
        """
        # 加载配置
        self.config = Config(config_dir)
        
        # 初始化ADB控制器
        self.adb = ADBController(
            host=self.config.adb_host,
            port=self.config.adb_port,
            adb_path=self.config.adb_path
        )
        
        # 初始化图像识别器
        self.recognizer = ImageRecognizer(templates_dir)
        
        # 运行状态
        self._running = False
        self._paused = False
        
        # 继续按钮自动点击线程
        self._continue_thread = None
        self._continue_running = False
        self._continue_paused = False  # 胜利/开始界面时暂停点击
        
        # 统计信息
        self.stats = {
            "runs": 0,           # 完成的轮次
            "cards": 0,          # 选择的卡牌数量
            "obstacles": 0       # 遇到的障碍物数量
        }
        
        # 上一次的状态，用于检测状态变化
        self._last_state = None
        
        # 回调函数
        self._on_state_change = None
        self._on_log = None
    
    def set_callbacks(self, on_state_change=None, on_log=None):
        """设置回调函数"""
        self._on_state_change = on_state_change
        self._on_log = on_log
    
    def _log(self, message: str):
        """输出日志"""
        print(message)
        if self._on_log:
            self._on_log(message)
    
    def _notify_state(self, state: str):
        """通知状态变化"""
        if self._on_state_change:
            self._on_state_change(state)
    
    def connect(self) -> bool:
        """连接到模拟器"""
        self._log("正在连接模拟器...")
        if self.adb.connect():
            self._log("✓ 模拟器连接成功")
            return True
        else:
            self._log("✗ 模拟器连接失败，请确保雷电模拟器已启动")
            return False
    
    def start(self):
        """开始自动化"""
        self._running = True
        self._paused = False
        self._log("▶ 开始自动化")
        self._notify_state("运行中")
        
        # 启动继续按钮自动点击线程
        self._start_continue_clicker()
        
        self._main_loop()
    
    def stop(self):
        """停止自动化"""
        self._running = False
        
        # 停止继续按钮线程
        self._stop_continue_clicker()
        
        self._log("⏹ 停止自动化")
        self._notify_state("已停止")
    
    def pause(self):
        """暂停自动化"""
        self._paused = True
        self._log("⏸ 暂停自动化")
        self._notify_state("已暂停")
    
    def resume(self):
        """恢复自动化"""
        self._paused = False
        self._log("▶ 恢复自动化")
        self._notify_state("运行中")
    
    def _start_continue_clicker(self):
        """启动继续按钮自动点击线程"""
        if self._continue_thread and self._continue_thread.is_alive():
            return  # 线程已在运行
        
        self._continue_running = True
        self._continue_thread = threading.Thread(target=self._continue_click_loop, daemon=True)
        self._continue_thread.start()
        self._log("  ✓ 继续按钮自动点击线程已启动（每0.5秒）")
    
    def _stop_continue_clicker(self):
        """停止继续按钮自动点击线程"""
        self._continue_running = False
        if self._continue_thread:
            self._continue_thread.join(timeout=1)
            self._continue_thread = None
    
    def _continue_click_loop(self):
        """继续按钮点击循环（后台线程）"""
        while self._continue_running:
            try:
                # 只要自动化在运行，且不在暂停状态，且不在胜利/准备等非持续点击状态
                if not self._paused and not self._continue_paused:
                    continue_x, continue_y = self.config.btn_continue_pos
                    self.adb.tap(continue_x, continue_y)
                else:
                    if self._continue_paused:
                        # log_debug("继续按钮点击已暂停 (当前界面不需要持续点击)")
                        pass
            except Exception as e:
                pass  # 静默失败，不影响主流程
            
            time.sleep(0.5)  # 每0.5秒点击一次
            
            time.sleep(0.5)  # 每0.5秒点击一次
    
    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._running
    
    @property
    def is_paused(self) -> bool:
        """是否已暂停"""
        return self._paused
    
    def _handle_purchase(self, screen):
        """处理购买界面（点击右上角关闭）"""
        self._notify_state("取消购买")
        self._log("💰 发现购买弹窗 - 点击关闭")
        self._continue_paused = True
        
        # 使用配置文件中的取消购买按钮坐标
        if hasattr(self.config, 'btn_cancel_purchase_pos'):
            x, y = self.config.btn_cancel_purchase_pos
        else:
            x, y = (1520, 80) # 默认值
            
        self.adb.tap(x, y)
        time.sleep(1)
        
    def _handle_level_up(self, screen):
        """处理升级界面（点击升级按钮）"""
        self._notify_state("升级")
        self._log("⬆️ 升级界面 - 点击升级")
        
        # 使用配置文件中的升级按钮坐标
        if hasattr(self.config, 'btn_level_up_pos'):
            x, y = self.config.btn_level_up_pos
        else:
            x, y = (800, 780) # 默认值
            
        self.adb.tap(x, y)
        time.sleep(1)
        
    def _handle_level_up_after(self, screen):
        """处理升级后界面（点击右上角关闭）"""
        self._notify_state("升级完成")
        self._log("✔️ 升级后界面 - 点击关闭")
        # 逻辑同购买取消，点击右上角
        self._handle_purchase(screen)
        
    def _main_loop(self):
        """主循环"""
        while self._running:
            # 暂停检查
            if self._paused:
                time.sleep(0.1)
                continue
            
            try:
                # 截图
                log_debug("正在请求截图...")
                screenshot = self.adb.screenshot()
                if screenshot is None:
                    log_debug("警告: 截图失败")
                    if self.config.debug:
                        self._log("警告: 截图失败，重试中...")
                    time.sleep(1)
                    continue
                
                # 转换为OpenCV格式
                screen = self.recognizer.pil_to_cv2(screenshot)
                
                # 检测当前状态
                state = self.recognizer.detect_state(screen)
                log_debug(f"检测到状态: {state.name}")
                
                # 状态切换检测
                state_changed = (state != self._last_state)
                
                if state_changed:
                    if state != GameState.UNKNOWN:
                        self._log(f"[状态切换] {state.name}")
                    self._last_state = state
                
                # 需要重复处理的状态（应对游戏卡顿）
                repeat_states = [
                    GameState.PURCHASE_FAILED,    # 购买失败（优先处理）
                    GameState.LEVEL_PREPARE,      # 开始界面
                    GameState.CARD_SELECTION,     # 卡牌选择
                    GameState.OBSTACLE_CHOICE,    # 障碍物选择
                    GameState.OBSTACLE_SPECIALBOX, # 特殊障碍物宝箱
                    GameState.VICTORY,            # 胜利界面
                    GameState.PURCHASE,           # 购买弹窗
                    GameState.LEVEL_UP,           # 升级界面
                    GameState.LEVEL_UP_AFTER,     # 升级后确认界面
                    GameState.ARENA_OK            # 赛季结束奖励界面
                ]
                
                # 状态切换时处理，或特定状态重复处理
                if state_changed or state in repeat_states:
                    log_debug(f"准备执行处理逻辑 (state={state.name}, changed={state_changed})")
                    self._handle_state(state, screen, is_repeat=not state_changed)
                else:
                    if state == GameState.UNKNOWN:
                        log_debug("未知状态，跳过处理")
                
            except Exception as e:
                import traceback
                self._log(f"错误: {e}")
                self._log(traceback.format_exc())
                time.sleep(1)
            
            # 循环间隔
            time.sleep(self.config.loop_delay_ms / 1000.0)
    
    def _handle_state(self, state: GameState, screen, is_repeat: bool = False):
        """处理游戏状态"""
        
        if state == GameState.PURCHASE_FAILED:
            self._handle_purchase_failed(screen)
        
        elif state == GameState.LEVEL_PREPARE:
            self._handle_level_prepare(screen)
        
        elif state == GameState.CARD_SELECTION:
            self._handle_card_selection(screen, is_repeat)
        
        elif state == GameState.OBSTACLE_CONTINUE:
             self._handle_obstacle_continue(screen)
        
        elif state == GameState.OBSTACLE_CHOICE:
            self._handle_obstacle_choice(screen, is_repeat)
        
        elif state == GameState.VICTORY:
            self._handle_victory(screen, is_repeat)
        
        elif state == GameState.DEFEAT:
            self._handle_defeat(screen)
            
        elif state == GameState.PURCHASE:
            self._handle_purchase(screen)
            
        elif state == GameState.LEVEL_UP:
            self._handle_level_up(screen)
            
        elif state == GameState.LEVEL_UP_AFTER:
            self._handle_level_up_after(screen)
        
        elif state == GameState.OBSTACLE_SPECIALBOX:
            self._handle_obstacle_specialbox(screen, is_repeat)
        
        elif state == GameState.ARENA_OK:
            if self.config.enable_arena_ok_detection:
                self._handle_arena_ok(screen)
            else:
                # 配置中禁用了检测，忽略该状态
                pass
        
        elif state == GameState.UNKNOWN:
            # 未知状态，可能是战斗中，等待
            pass
    
    def _handle_level_prepare(self, screen):
        """处理关卡准备界面"""
        self._notify_state("关卡准备")
        
        # 暂停继续按钮点击，避免在胜利→开始界面切换时循环卡住
        self._continue_paused = True
        
        # 查找开始按钮
        result = self.recognizer.find_template(screen, "btn_start")
        if result:
            x, y, _ = result
            self.adb.tap(x, y)
        else:
            # 使用配置文件中的坐标
            x, y = self.config.btn_start_pos
            self.adb.tap(x, y)
        
        time.sleep(1)  # 等待游戏加载
    
    def _handle_card_selection(self, screen, is_repeat: bool = False):
        """处理卡牌选择界面"""
        if not is_repeat:
            self._notify_state("选择卡牌")
            self._continue_paused = False
        
        # 无论是不是重复，进入此函数说明画面还在卡牌界面，根据需要执行点击
        # 注意：卡牌选择如果要防重点，可以加个短冷却
        
        need_double_select = False
        try:
            # 检测是否需要选择2次（左下角蓝色"选择2个！"图标）
            import cv2
            import numpy as np
            h, w = screen.shape[:2]
            bottom_left_icon = screen[int(h*0.7):int(h*0.85), :int(w*0.15)]
            icon_hsv = cv2.cvtColor(bottom_left_icon, cv2.COLOR_BGR2HSV)
            # 检测蓝色（H: 100-130, S: 100-255, V: 100-255）
            blue_mask = cv2.inRange(icon_hsv, np.array([100, 100, 100]), np.array([130, 255, 255]))
            blue_pixels = cv2.countNonZero(blue_mask)
            
            need_double_select = blue_pixels > 1000  # 如果有蓝色图标，需要选择2次
            
            if need_double_select:
                self._log(f"  检测到'选择2个'标志，将连续选择两次")
        except Exception as e:
            self._log(f"  检测'选择2个'标志失败: {e}，默认单选")
            need_double_select = False
        
        # TODO: 实现卡牌ID识别，暂时随机选择
        card_ids = [None, None, None]
        
        # 第一次选择
        best_index = self._select_best_card(card_ids)
        if not is_repeat:
            self._log(f"🃏 选择卡牌 #{best_index + 1}")
        
        x, y = self.config.card_positions[best_index]
        self.adb.tap(x, y)
        
        if not is_repeat:
            self.stats["cards"] += 1
        
        if need_double_select:
            # 需要选择第二次
            time.sleep(0.3)  # 短暂等待第一张卡消失
            
            # 第二次选择（避免选同一张）
            second_index = self._select_best_card(card_ids, exclude_index=best_index)
            if not is_repeat:
                self._log(f"🃏 选择卡牌 #{second_index + 1} (第2次)")
            
            x2, y2 = self.config.card_positions[second_index]
            self.adb.tap(x2, y2)               
            if not is_repeat:
                self.stats["cards"] += 1
            time.sleep(0.5)
        else:
            time.sleep(0.5)
    
    def _select_best_card(self, card_ids: List[Optional[str]], exclude_index: Optional[int] = None) -> int:
        """
        根据权重选择最佳卡牌
        
        Args:
            card_ids: 卡牌ID列表
            exclude_index: 要排除的卡牌索引（用于第二次选择）
            
        Returns:
            选择的卡牌索引
        """
        best_index = 0
        best_weight = -1
        has_known_card = False
        
        for i, card_id in enumerate(card_ids):
            # 跳过被排除的索引
            if exclude_index is not None and i == exclude_index:
                continue
                
            if card_id is not None:
                weight = self.config.get_card_weight(card_id)
                if weight > 0:
                    has_known_card = True
                    if weight > best_weight:
                        best_weight = weight
                        best_index = i
        
        # 如果没有已知卡牌，随机选择（排除已选的）
        if not has_known_card:
            available_indices = [i for i in range(len(card_ids)) if i != exclude_index]
            if available_indices:
                best_index = random.choice(available_indices)
            else:
                best_index = random.randint(0, len(card_ids) - 1)
            self._log(f"  无已知卡牌，随机选择 #{best_index + 1}")
        
        return best_index
    
    def _handle_obstacle_continue(self, screen):
        """处理障碍物界面（继续按钮）"""
        self._notify_state("障碍物")
        
        # 核心修复：进入障碍物界面说明已经脱离了胜利/准备阶段，恢复背景点击
        self._continue_paused = False
        
        # 除了依靠后台线程，这里主动点一次，增加响应速度
        x, y = self.config.btn_continue_pos
        self.adb.tap(x, y)
        
        self.stats["obstacles"] += 1
        time.sleep(0.5)
    
    def _handle_obstacle_choice(self, screen, is_repeat: bool = False):
        """处理障碍物界面（三选一）"""
        choice = self.config.obstacle_choice
        
        if not is_repeat:
            self._notify_state("选择奖励")
            # 进入游戏，恢复继续按钮点击
            self._continue_paused = False
            # 打印详细信息
            self._log(f"🔥 障碍物选择 - 第{choice}个")
        
        # 使用配置文件中的坐标
        positions = self.config.choice_positions
        
        if len(positions) >= choice:
            x, y = positions[choice - 1]  # 转为0索引
            self.adb.tap(x, y)
        
        if not is_repeat:
            self.stats["obstacles"] += 1
        time.sleep(0.8)
    
    def _handle_obstacle_specialbox(self, screen, is_repeat: bool = False):
        """处理特殊障碍物宝箱界面"""
        if not is_repeat:
            self._notify_state("开启宝箱")
            self._log("🎁 发现特殊障碍物宝箱 - 点击开启")
        
        # 使用配置文件中的坐标
        x, y = self.config.btn_open_chest_pos
        self.adb.tap(x, y)
        
        if not is_repeat:
            self.stats["obstacles"] += 1
        time.sleep(1)
    
    def _handle_victory(self, screen, is_repeat: bool = False):
        """处理胜利界面"""
        if not is_repeat:
            self._notify_state("胜利")
            # 暂停继续按钮点击，避免在胜利→开始界面切换时循环卡住
            self._continue_paused = True
            # 更新统计
            self.stats["runs"] += 1
            self._log(f"🏆 胜利! 完成第 {self.stats['runs']} 轮")
        
        # 查找重试按钮并点击（每次检测到都会尝试点击，直到界面消失）
        result = self.recognizer.find_template(screen, "btn_retry")
        if result:
            x, y, _ = result
            self.adb.tap(x, y)
        else:
            # 使用配置文件中的坐标
            x, y = self.config.btn_retry_pos
            self.adb.tap(x, y)
        
        time.sleep(1)
    
    def _handle_defeat(self, screen):
        """处理失败界面"""
        self._log("💀 失败 - 点击继续")
        self._notify_state("失败")
        self._continue_paused = True
        
        # 使用重试按钮坐标（失败界面也是这个位置）
        x, y = self.config.btn_retry_pos
        self.adb.tap(x, y)
        
        time.sleep(1)
    
    def _handle_purchase_failed(self, screen):
        """处理购买失败界面"""
        self._log("⚠️ 购买失败弹窗 - 点击确认")
        self._notify_state("购买失败")
        
        # 点击确认按钮关闭弹窗
        x, y = self.config.btn_purchase_confirm_pos
        self.adb.tap(x, y)
        
        time.sleep(2)  # 增加等待时间，确保弹窗完全关闭（容错处理）

    def _handle_arena_ok(self, screen):
        """处理赛季结束奖励界面（点击 OK 按钮）"""
        self._notify_state("赛季奖励")
        self._continue_paused = True
        
        # 使用配置文件中的 OK 按钮坐标
        x, y = self.config.btn_ok_pos
        self._log(f"🏆 发现赛季结束奖励界面 - 点击 OK 坐标({x}, {y})")
        result = self.adb.tap(x, y)
        self._log(f"  tap 结果: {result}")
        time.sleep(1)


# 测试代码
if __name__ == "__main__":
    automation = GameAutomation()
    
    if automation.connect():
        print("\n按 Ctrl+C 停止")
        try:
            automation.start()
        except KeyboardInterrupt:
            automation.stop()
            print("\n已停止")
