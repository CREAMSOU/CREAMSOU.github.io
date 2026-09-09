@echo off
chcp 65001 >nul
cd /d %~dp0
call npm run build
echo 构建完成，输出在 docs\.vitepress\dist
pause
