"""
认证相关的Pydantic模型
用于登录请求和令牌响应
"""
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """令牌响应模型"""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """令牌数据模型，用于解码JWT后的数据"""
    username: Optional[str] = None 