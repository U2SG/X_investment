"""
模型配置数据库模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from database import Base


class ModelConfig(Base):
    """模型配置表"""
    __tablename__ = "model_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True, comment="模型名称")
    model_version = Column(String(50), nullable=False, comment="模型版本")
    parameters = Column(JSON, nullable=False, comment="模型参数")
    description = Column(Text, nullable=True, comment="模型描述")
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<ModelConfig(id={self.id}, model_name='{self.model_name}', version='{self.model_version}')>" 