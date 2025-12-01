import os
from fastapi import UploadFile
from .config import settings


def validate_content(file: UploadFile) -> bool:
    """
    # 示例：只做大小检查，后续可扩展色情/涉政检测等
    # Example: Only size checks are performed, and subsequent *graphic/political-related testing can be extended
    """
    MAX_SIZE_BYTES = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    # 获取文件大小，同时重置文件指针
    file.file.seek(0, os.SEEK_END)
    size = file.file.tell()
    file.file.seek(0)

    if size > MAX_SIZE_BYTES:
        print(f"Validation Failed: File size {size / (1024 * 1024):.2f}MB exceeds {settings.MAX_FILE_SIZE_MB}MB limit.")
        return False

    # ----------------------------------------------------
    # 2. Reset File Pointer for Uploader
    # ----------------------------------------------------

    return True