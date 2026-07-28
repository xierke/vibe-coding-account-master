@echo off
chcp 65001 >nul
REM ===================================
REM  DailyTracker 一键启动脚本
REM  同时启动 后端(8000) + 前端(5173)
REM ===================================

cd /d "%~dp0"

echo ========================================
echo   DailyTracker 一键启动
echo   后端: http://localhost:8000
echo   前端: http://localhost:5173
echo   文档: http://localhost:8000/docs
echo ========================================
echo.

echo [1/2] 启动后端 (FastAPI)...
start "DailyTracker-API" cmd /k "cd backend && python run.py"

echo [2/2] 启动前端 (Vite)...
start "DailyTracker-Web" cmd /k "cd frontend && npm run dev"

echo.
echo 两个服务已在独立窗口中启动。
echo 关闭此窗口不会停止服务。
echo.
pause
