"""
应用入口 — 使 backend/ 目录可直接运行 `uvicorn app.main:app`。
"""
from app.main import app

__all__ = ["app"]
