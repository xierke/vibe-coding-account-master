"""
SQLAlchemy ORM 基础声明。
所有模型继承 Base，使用 async 引擎。
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """ORM 声明基类 — 所有模型继承此类。"""
    pass
