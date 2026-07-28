"""
应用配置 — 所有配置从环境变量读取，启动时校验，fail fast。
使用 pydantic-settings 实现类型安全配置。
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置。所有必填项缺省会导致启动失败。"""

    # --- 应用 ---
    app_name: str = "DailyTracker"
    app_version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/v1"

    # --- 数据库 ---
    database_url: str = "mysql+aiomysql://root:wyx4022@127.0.0.1:3306/account"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False  # SQL 日志，开发时可设为 True

    # --- Redis ---
    redis_url: str = "redis://127.0.0.1:6379/0"
    redis_decode_responses: bool = True

    # --- JWT 认证 ---
    jwt_secret: str = "dailytracker-dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # --- 密码安全 ---
    bcrypt_rounds: int = 12
    max_login_attempts: int = 5          # 密码错误上限
    lockout_duration_minutes: int = 15    # 账号锁定时长

    # --- 验证码 ---
    verify_code_length: int = 6           # 验证码位数
    verify_code_ttl_seconds: int = 300    # 验证码有效期 (5 分钟)

    # --- 限流 ---
    rate_limit_per_minute: int = 100      # 用户 API 限流
    login_rate_limit_per_minute: int = 20 # 登录接口 IP 限流

    # --- CORS ---
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
    ]

    # --- 分页 ---
    default_page_size: int = 20
    max_page_size: int = 100

    # --- 日志 ---
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 全局单例 — 模块加载时即校验
settings = Settings()
