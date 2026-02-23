@echo off
setlocal
chcp 65001 > nul

echo ======================================================
echo          黑曜石骑士游戏助手 - 编译工具
echo ======================================================
echo.
echo [信息] 使用 Nuitka 编译为 EXE。
echo [信息] 建议关闭所有开启的游戏助手窗口。
echo.

:: 检查 Python 环境变量
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到 Python，请先安装 Python 并添加到环境变量。
    pause
    exit /b 1
)

:: 尝试运行打包脚本
echo [信息] 正在启动打包进程...
python build\pack.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 编译过程中出现问题。
    pause
    exit /b %errorlevel%
)

echo.
echo [成功] 编译任务已完成！
echo [提示] 成果物位于 dist 目录中。
echo.
pause
