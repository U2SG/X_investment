"""
认证工具模块
提供密码哈希和验证功能，以及JWT令牌生成和验证功能
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Union, cast
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import get_db
from models import User
from schemas.auth import TokenData

# 创建密码哈希上下文，使用bcrypt算法
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 定义OAuth2密码流，tokenUrl必须与路由中的一致
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def hash_password(password: str) -> str:
    """
    对密码进行哈希处理
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否正确
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希后的密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 令牌过期时间增量，如不指定则使用默认值
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 添加过期时间
    to_encode.update({"exp": expire})
    
    # 使用密钥和算法生成JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    获取当前用户的依赖函数
    
    Args:
        token: JWT令牌
        db: 数据库会话
        
    Returns:
        User: 当前用户对象
        
    Raises:
        HTTPException: 如果令牌无效或用户不存在
    """
    # 定义认证失败的异常
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 解码JWT令牌
        if not token:
            logging.error("未提供token")
            raise credentials_exception
        # print("token:", token)
        if not SECRET_KEY:
            logging.error("SECRET_KEY未配置，无法校验token")
            raise credentials_exception
        # print("SECRET_KEY:", SECRET_KEY)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Union[str, None] = payload.get("sub")
        if not username:
            logging.error(f"JWT payload中未找到sub字段: {payload}")
            raise credentials_exception
        # 确保username是字符串类型
        username_str = cast(str, username)
        token_data = TokenData(username=username_str)
    except JWTError as e:
        logging.error(f"JWT解码失败: {e}")
        raise credentials_exception
    except Exception as e:
        logging.error(f"认证流程异常: {e}")
        raise credentials_exception

    # 从数据库获取用户
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        logging.error(f"数据库未找到用户: {token_data.username}")
        raise credentials_exception
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    获取当前活跃用户的依赖函数
    
    Args:
        current_user: 当前用户对象
        
    Returns:
        User: 当前活跃用户对象
        
    Raises:
        HTTPException: 如果用户已被禁用
    """
    if not bool(current_user.is_active):
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return current_user