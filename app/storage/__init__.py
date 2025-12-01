from typing import Annotated
from fastapi import Depends
from ..config import settings
from .base import StorageUploader
from .local import LocalUploader, AlibabaOSS_Uploader

# 存储上传器工厂函数 (Dependency Factory)
def get_storage_uploader() -> StorageUploader:
    """Returns the correct Uploader instance based on the configuration (STORAGE_MODE)."""
    if settings.STORAGE_MODE == "oss":
        return AlibabaOSS_Uploader(
            bucket_name=settings.OSS_BUCKET,
            endpoint=settings.OSS_ENDPOINT
        )
    # default return  LocalUploader
    return LocalUploader()

# 用于 FastAPI 依赖注入的类型别名
Uploader = Annotated[StorageUploader, Depends(get_storage_uploader)]