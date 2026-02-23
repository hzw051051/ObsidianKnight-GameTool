"""
配置加载模块
支持JSONC格式（带注释的JSON）
"""
import json
import re
from pathlib import Path
from typing import Dict, Any

# --- 极速日志记录逻辑 ---
def log_debug(msg):
    try:
        import os
        from datetime import datetime
        with open("error.log", "a", encoding="utf-8") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] [PID:{os.getpid()}] [Config] {msg}\n")
    except:
        pass


def remove_json_comments(json_str: str) -> str:
    """
    移除JSON字符串中的注释
    
    支持:
    - 单行注释 //
    - 不处理字符串内的注释
    """
    result = []
    in_string = False
    escape_next = False
    i = 0
    
    while i < len(json_str):
        char = json_str[i]
        
        # 处理转义字符
        if escape_next:
            result.append(char)
            escape_next = False
            i += 1
            continue
        
        if char == '\\' and in_string:
            result.append(char)
            escape_next = True
            i += 1
            continue
        
        # 处理字符串边界
        if char == '"':
            in_string = not in_string
            result.append(char)
            i += 1
            continue
        
        # 在字符串外检测注释
        if not in_string:
            # 检测单行注释 //
            if char == '/' and i + 1 < len(json_str) and json_str[i + 1] == '/':
                # 跳过直到行尾
                while i < len(json_str) and json_str[i] != '\n':
                    i += 1
                continue
        
        result.append(char)
        i += 1
    
    return ''.join(result)


def load_jsonc(file_path: str) -> Dict[str, Any]:
    """
    加载JSONC文件（支持注释的JSON）
    
    Args:
        file_path: 文件路径
        
    Returns:
        解析后的字典
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {file_path}")
    
    content = path.read_text(encoding='utf-8')
    
    # 移除注释
    clean_content = remove_json_comments(content)
    
    # 解析JSON
    return json.loads(clean_content)


class Config:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目录路径
        """
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}
        self._card_weights: Dict[str, int] = {}
        
        self._load_configs()
    
    def _load_configs(self):
        """加载所有配置文件"""
        # 加载通用配置
        config_path = self.config_dir / "config.jsonc"
        if config_path.exists():
            self._config = load_jsonc(str(config_path))
            log_debug(f"已加载配置: {config_path.absolute()}")
        else:
            log_debug(f"警告: 配置文件不存在: {config_path.absolute()}")
            self._config = {
                "debug": False, # 新增 debug 属性
                "obstacle_choice": 3,
                "loop_delay_ms": 500,
                "screenshot_interval_ms": 200,
                "adb_host": "127.0.0.1",
                "adb_port": 5555
            }
        
        # 加载卡牌权重配置
        weights_path = self.config_dir / "card_weights.jsonc"
        if weights_path.exists():
            raw_weights = load_jsonc(str(weights_path))
            # 确保键是字符串
            self._card_weights = {str(k): int(v) for k, v in raw_weights.items()}
            print(f"已加载卡牌权重: {len(self._card_weights)}张卡牌")
        else:
            print(f"警告: 卡牌权重配置不存在: {weights_path}")
            self._card_weights = {}
    
    def reload(self):
        """重新加载配置"""
        self._load_configs()
    
    @property
    def debug(self) -> bool:
        """是否显示调试信息"""
        return self._config.get("debug", False)
    
    # ===== 通用配置 =====
    
    @property
    def obstacle_choice(self) -> int:
        """障碍物选择时的默认选项（1/2/3）"""
        return self._config.get("obstacle_choice", 3)
    
    @property
    def loop_delay_ms(self) -> int:
        """主循环间隔（毫秒）"""
        return self._config.get("loop_delay_ms", 500)
    
    @property
    def screenshot_interval_ms(self) -> int:
        """截图检测间隔（毫秒）"""
        return self._config.get("screenshot_interval_ms", 200)
    
    @property
    def adb_host(self) -> str:
        """ADB主机地址"""
        return self._config.get("adb_host", "127.0.0.1")
    
    @property
    def adb_port(self) -> int:
        """ADB端口"""
        return self._config.get("adb_port", 5555)
    
    @property
    def max_log_lines(self) -> int:
        """日志最大行数"""
        return self._config.get("max_log_lines", 500)
    
    @property
    def adb_path(self) -> str:
        """ADB可执行文件路径"""
        return self._config.get("adb_path", "adb")
    
    @property
    def card_weights(self) -> Dict[str, int]:
        """获取所有卡牌权重"""
        return self._card_weights

    def get_card_weight(self, card_id: Any) -> int:
        """
        获取卡牌权重
        
        Args:
            card_id: 卡牌ID (int 或 str)
            
        Returns:
            权重值，不存在返回0
        """
        return self._card_weights.get(str(card_id), 0)
    
    def get_all_card_weights(self) -> Dict[str, int]:
        """获取所有卡牌权重"""
        return self._card_weights.copy()
    
    # ===== 坐标配置 =====
    
    @property
    def btn_start_pos(self) -> tuple:
        """开始按钮坐标"""
        pos = self._config.get("btn_start_pos", [900, 800])
        return tuple(pos)
    
    @property
    def btn_retry_pos(self) -> tuple:
        """重试按钮坐标"""
        pos = self._config.get("btn_retry_pos", [900, 800])
        return tuple(pos)
    
    @property
    def btn_continue_pos(self) -> tuple:
        """继续按钮坐标"""
        pos = self._config.get("btn_continue_pos", [1500, 350])
        return tuple(pos)
    
    @property
    def btn_purchase_confirm_pos(self) -> tuple:
        """购买失败确认按钮坐标"""
        pos = self._config.get("btn_purchase_confirm_pos", [900, 675])
        return tuple(pos)
    
    @property
    def btn_level_up_pos(self) -> tuple:
        """升级确认按钮坐标"""
        pos = self._config.get("btn_level_up_pos", [800, 760])
        return tuple(pos)
    
    @property
    def btn_cancel_purchase_pos(self) -> tuple:
        """取消购买按钮坐标"""
        pos = self._config.get("btn_cancel_purchase_pos", [1500, 200])
        return tuple(pos)

    @property
    def btn_open_chest_pos(self) -> tuple:
        """开启特质宝箱按钮坐标"""
        pos = self._config.get("btn_open_chest_pos", [800, 500])
        return tuple(pos)

    @property
    def card_positions(self) -> list:
        """卡牌位置列表"""
        positions = self._config.get("card_positions", [[400, 400], [800, 400], [1200, 400]])
        return [tuple(p) for p in positions]
    
    @property
    def choice_positions(self) -> list:
        """选项位置列表"""
        positions = self._config.get("choice_positions", [[600, 250], [900, 250], [1200, 250]])
        return [tuple(p) for p in positions]


# 测试代码
if __name__ == "__main__":
    config = Config()
    
    print("\n=== 通用配置 ===")
    print(f"obstacle_choice: {config.obstacle_choice}")
    print(f"loop_delay_ms: {config.loop_delay_ms}")
    print(f"adb_host: {config.adb_host}")
    print(f"adb_port: {config.adb_port}")
    
    print("\n=== 卡牌权重 ===")
    for card_id, weight in config.get_all_card_weights().items():
        print(f"  卡牌 {card_id}: 权重 {weight}")
