"""
使用ldconsole测试点击
"""
import subprocess

def main():
    ldconsole = r"E:\leidian\LDPlayer9\ldconsole.exe"
    
    print("=" * 50)
    print("测试1: 使用ldconsole发送点击")
    print("=" * 50)
    
    # 方法1: 使用action命令
    cmd = [ldconsole, "action", "--index", "0", "--key", "call.input", "--value", "tap 900 800"]
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"返回码: {result.returncode}")
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    
    print("\n" + "=" * 50)
    print("测试2: 使用adb2命令")
    print("=" * 50)
    
    # 方法2: 使用adb2命令
    cmd = [ldconsole, "adb2", "--index", "0", "--command", "shell input tap 900 800"]
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(f"返回码: {result.returncode}")
    print(f"stdout: {result.stdout}")
    print(f"stderr: {result.stderr}")
    
    print("\n请查看模拟器是否有反应！")
    input("按回车键退出...")

if __name__ == "__main__":
    main()
