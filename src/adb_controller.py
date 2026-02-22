"""
ADB控制模块
用于连接雷电模拟器并执行屏幕操作
"""
import subprocess
import time
import os
from typing import Optional, Tuple
from PIL import Image
import io


class ADBController:
    """ADB控制器，负责与模拟器交互"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = 5555, adb_path: str = "adb"):
        """
        初始化ADB控制器
        
        Args:
            host: 模拟器ADB主机地址
            port: 模拟器ADB端口（雷电模拟器9默认5555）
            adb_path: 手动指定的ADB路径
        """
        self.host = host
        self.port = port
        self.device_id = f"{host}:{port}"
        self._connected = False
        
        # 保存并查找ADB路径
        self.config_adb_path = adb_path
        self.adb_path = self._find_adb()
    
    def _find_adb(self) -> str:
        """查找ADB可执行文件路径"""
        # 1. 首先尝试配置文件中指定的路径
        if self.config_adb_path and os.path.exists(self.config_adb_path):
            return self.config_adb_path
            
        # 2. 尝试系统PATH中的adb
        try:
            result = subprocess.run(
                ["adb", "version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return "adb"
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        
        # 3. 尝试通过运行中的进程查找
        try:
            # 使用 PowerShell 查找 dnplayer.exe 的路径
            cmd = ["powershell", "-Command", "Get-Process dnplayer -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Path"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                ld_dir = os.path.dirname(result.stdout.strip())
                adb_exe = os.path.join(ld_dir, "adb.exe")
                if os.path.exists(adb_exe):
                    return adb_exe
        except Exception:
            pass
            
        # 4. 尝试预设的常见路径
        ld_paths = [
            r"E:\LDPlayer\LDPlayer9\adb.exe",
            r"D:\LDPlayer\LDPlayer9\adb.exe",
            r"C:\LDPlayer\LDPlayer9\adb.exe",
            r"E:\leidian\LDPlayer9\adb.exe",
            r"C:\leidian\LDPlayer9\adb.exe",
            r"D:\leidian\LDPlayer9\adb.exe",
        ]
        
        for path in ld_paths:
            if os.path.exists(path):
                return path
        
        # 默认使用系统adb（即使不存在，作为最后方案）
        return "adb"
    
    def _run_adb(self, args: list, timeout: int = 30) -> Tuple[bool, str]:
        """
        执行ADB命令
        
        Args:
            args: ADB命令参数列表
            timeout: 超时时间（秒）
            
        Returns:
            (成功标志, 输出内容)
        """
        cmd = [self.adb_path, "-s", self.device_id] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='ignore'
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "命令执行超时"
        except Exception as e:
            return False, str(e)
    
    def connect(self) -> bool:
        """
        连接到模拟器
        
        Returns:
            是否连接成功
        """
        # 首先检查是否有已连接的设备
        try:
            result = subprocess.run(
                [self.adb_path, "devices"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding='utf-8',
                errors='ignore'
            )
            
            # 解析设备列表
            lines = result.stdout.strip().split('\n')
            for line in lines[1:]:  # 跳过第一行 "List of devices attached"
                if '\t' in line:
                    device_id, status = line.split('\t')
                    if status.strip() == 'device':
                        # 找到已连接的设备
                        self.device_id = device_id.strip()
                        self._connected = True
                        print(f"找到已连接设备: {self.device_id}")
                        return True
            
            # 如果没有找到设备，尝试connect命令
            connect_targets = [
                f"{self.host}:{self.port}",
                "127.0.0.1:5555",
                "127.0.0.1:5554",
                "emulator-5554",
                "emulator-5556",
            ]
            
            for target in connect_targets:
                cmd = [self.adb_path, "connect", target]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    encoding='utf-8',
                    errors='ignore'
                )
                output = result.stdout + result.stderr
                
                if "connected" in output.lower() and "cannot" not in output.lower():
                    self.device_id = target
                    self._connected = True
                    print(f"已连接到: {self.device_id}")
                    return True
            
            return False
        except Exception as e:
            print(f"连接失败: {e}")
            return False
    
    def disconnect(self) -> bool:
        """断开连接"""
        cmd = [self.adb_path, "disconnect", self.device_id]
        try:
            subprocess.run(cmd, capture_output=True, timeout=5)
            self._connected = False
            return True
        except Exception:
            return False
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        success, output = self._run_adb(["get-state"], timeout=5)
        return success and "device" in output
    
    def screenshot(self) -> Optional[Image.Image]:
        """
        截取模拟器屏幕
        
        Returns:
            PIL Image对象，失败返回None
        """
        # 使用screencap命令截图并直接输出到stdout
        cmd = [self.adb_path, "-s", self.device_id, "exec-out", "screencap", "-p"]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout:
                # 将PNG数据转换为PIL Image
                image = Image.open(io.BytesIO(result.stdout))
                return image
            
            return None
        except Exception as e:
            print(f"截图失败: {e}")
            return None
    
    def tap(self, x: int, y: int) -> bool:
        """
        点击屏幕指定位置
        
        Args:
            x: X坐标
            y: Y坐标
            
        Returns:
            是否成功
        """
        success, output = self._run_adb(["shell", "input", "tap", str(x), str(y)])
        return success
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> bool:
        """
        滑动屏幕
        
        Args:
            x1, y1: 起始坐标
            x2, y2: 结束坐标
            duration_ms: 滑动持续时间（毫秒）
            
        Returns:
            是否成功
        """
        success, _ = self._run_adb([
            "shell", "input", "swipe",
            str(x1), str(y1), str(x2), str(y2), str(duration_ms)
        ])
        return success
    
    def key_event(self, keycode: int) -> bool:
        """
        发送按键事件
        
        Args:
            keycode: Android按键码
            
        Returns:
            是否成功
        """
        success, _ = self._run_adb(["shell", "input", "keyevent", str(keycode)])
        return success
    
    def back(self) -> bool:
        """按返回键"""
        return self.key_event(4)  # KEYCODE_BACK
    
    def home(self) -> bool:
        """按Home键"""
        return self.key_event(3)  # KEYCODE_HOME


# 测试代码
if __name__ == "__main__":
    controller = ADBController()
    
    print("正在连接模拟器...")
    if controller.connect():
        print("连接成功！")
        
        print("正在截图...")
        img = controller.screenshot()
        if img:
            img.save("test_screenshot.png")
            print(f"截图保存成功: test_screenshot.png, 尺寸: {img.size}")
        else:
            print("截图失败")
        
        print("测试点击 (100, 100)...")
        if controller.tap(100, 100):
            print("点击成功")
        else:
            print("点击失败")
    else:
        print("连接失败，请确保雷电模拟器已启动")
