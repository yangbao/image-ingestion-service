import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    应用程序配置管理。从环境变量加载，提供默认值。
    """
    # Core Service Settings
    APP_NAME: str = "Image Ingestion Service"

    # Database Settings: 支持切换 SQLite/PostgreSQL
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./images.db")

    # Storage Settings: 'local' (默认) 或 'oss'
    STORAGE_MODE: str = os.environ.get("STORAGE_MODE", "local")

    # OSS Specific Settings (用于生产环境切换)
    OSS_BUCKET: str = os.environ.get("OSS_BUCKET", "prod-default-bucket")
    OSS_ENDPOINT: str = os.environ.get("OSS_ENDPOINT", "http://oss-cn-beijing.aliyuncs.com")

    # Compliance Settings
    MAX_FILE_SIZE_MB: int = 10


settings = Settings()