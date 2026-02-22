"""
诊断脚本：测试ADB连接和点击功能
"""
import subprocess
import sys

def run_cmd(cmd):
    """执行命令并返回结果"""
    print(f"执行: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        print(f"返回码: {result.returncode}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"错误: {e}")
        return False

def main():
    adb_path = r"E:\leidian\LDPlayer9\adb.exe"
    
    print("=" * 50)
    print("1. 检查ADB版本")
    print("=" * 50)
    run_cmd([adb_path, "version"])
    
    print("\n" + "=" * 50)
    print("2. 列出已连接设备")
    print("=" * 50)
    run_cmd([adb_path, "devices", "-l"])
    
    print("\n" + "=" * 50)
    print("3. 测试点击 (900, 800) - 使用 emulator-5554")
    print("=" * 50)
    success = run_cmd([adb_path, "-s", "emulator-5554", "shell", "input", "tap", "900", "800"])
    
    if success:
        print("\n✓ 点击命令执行成功，请查看模拟器是否有反应")
    else:
        print("\n✗ 点击命令执行失败")
    
    print("\n" + "=" * 50)
    print("按回车键退出...")
    input()

if __name__ == "__main__":
    main()
