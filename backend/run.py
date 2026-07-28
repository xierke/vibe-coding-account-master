"""
DailyTracker — 开发环境启动入口。
直接运行此文件即可启动后端服务：
    python run.py
或:
    python backend/run.py
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,          # 代码变更自动重启
        log_level="info",
    )
