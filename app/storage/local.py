import os
import shutil
from fastapi import UploadFile
from .base import StorageUploader
from ..config import settings


# from alibabacloud_oss2 import models as oss2 # 假设这是阿里云 SDK

class LocalUploader(StorageUploader):
    """本地文件系统实现：用于开发和测试环境。"""

    def save(self, file: UploadFile, destination: str = "./uploads") -> str:
        """保存文件到本地目录。"""

        # 创建目标文件夹
        full_path = os.path.join(destination, "ai_platform_images")
        os.makedirs(full_path, exist_ok=True)

        file_path = os.path.join(full_path, file.filename)

        # 将文件流写入本地文件
        file.file.seek(0)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"File saved locally: {file_path}")
        return file_path


# 预留给未来的 alibaba_oss.py 实现
class AlibabaOSS_Uploader(StorageUploader):
    """阿里云 OSS 实现：用于生产环境。"""

    def __init__(self, bucket_name: str, endpoint: str):
        # 实际代码中，此处会使用阿里云 SDK 初始化 OSS 客户端
        # self.oss_client = oss2.Bucket(auth, endpoint, bucket_name)
        self.bucket_name = bucket_name
        self.endpoint = endpoint
        print(f"AlibabaOSS_Uploader initialized for bucket: {bucket_name}")

    def save(self, file: UploadFile, destination: str) -> str:
        """模拟保存文件到阿里云 OSS。"""

        object_key = f"{destination}/{file.filename}"

        # 实际操作：使用 self.oss_client.put_object(object_key, file.file)
        # 此处模拟消费文件流
        _ = file.file.read()

        print(f"Simulating upload to OSS path: {object_key}")
        # 返回 OSS Key 或 URL
        return f"oss://{self.bucket_name}/{object_key}"