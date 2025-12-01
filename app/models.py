from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from .database import Base

class Image(Base):
    """数据库模型：图片元数据表"""
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    original_filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False) # 本地路径或 OSS Key/URL
    upload_timestamp = Column(DateTime, default=datetime.utcnow)
    validation_status = Column(String, default="Pending")