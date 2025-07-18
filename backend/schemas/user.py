"""
用户相关的Pydantic模型
用于请求验证和响应序列化
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# 用户创建请求模型
class UserCreate(BaseModel):
    """用户创建请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="电子邮箱")
    password: str = Field(..., min_length=6, description="密码")

# 用户登录请求模型
class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

# 用户响应模型（不包含敏感信息如密码）
class UserResponse(BaseModel):
    """用户信息响应模型"""
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic配置类"""
        from_attributes = True  # 允许从ORM模型创建（替代V1中的orm_mode） 