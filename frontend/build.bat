@echo off
REM ===================================
REM  DailyTracker 前端生产构建脚本
REM  输出到 dist/ 目录
REM ===================================

cd /d "%~dp0"
echo Building DailyTracker Frontend for production...
echo.
call npm run build
echo.
echo Build complete! Output: dist/
pause
