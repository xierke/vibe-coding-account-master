#!/usr/bin/env bash
# ===================================
#  DailyTracker 前端开发启动脚本 (Bash)
#  启动 Vite 开发服务器 (localhost:5173)
# ===================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "Starting DailyTracker Frontend Dev Server..."
echo ""
npm run dev
