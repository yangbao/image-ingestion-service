from pydantic import BaseModel
from datetime import datetime

class UploadResponse(BaseModel):
    """Pydantic Schema"""
    message: str
    id: int
    filename: str
    path: str
    status: str
    upload_timestamp: datetime

    class Config:
        # 允许 ORM 模型实例直接转换为 Pydantic Schema
        from_attributes = True