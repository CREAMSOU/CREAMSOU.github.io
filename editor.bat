@echo off
chcp 65001 >nul
cd /d %~dp0
"C:\Users\cream\.workbuddy\binaries\python\envs\default\Scripts\python.exe" editor\server.py
pause
