@echo off
REM ===================================
REM  DailyTracker 前端开发启动脚本
REM  启动 Vite 开发服务器 (localhost:5173)
REM ===================================

cd /d "%~dp0"
echo Starting DailyTracker Frontend Dev Server...
echo.
call npm run dev
pause
