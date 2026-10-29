@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在启动博客控制台...
python server.py
if errorlevel 1 (
  echo.
  echo 启动失败。如果提示找不到 python，试试：
  echo   py server.py
  echo 或者把 Python 加到 PATH。
  pause
)
