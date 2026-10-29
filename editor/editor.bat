@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动博客控制台...
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 server.py
) else (
  python server.py
)
if errorlevel 1 (
  echo.
  echo 启动失败：没找到 Python。
  echo 装一个 Python 3，安装时勾选 "Add Python to PATH"，再双击本文件。
  pause
)
