@echo off
chcp 65001 >nul
cd /d %~dp0
echo 正在启动本地预览... 浏览器打开 http://localhost:5173 （Ctrl+C 停止）
call npm run dev
