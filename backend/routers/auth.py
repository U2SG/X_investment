"""
认证相关的API路由
包括用户登录和令牌获取功能
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import sys
import os
import logging
from datetime import timedelta

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加父目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database import get_db
from models import User
from schemas.auth import Token
from utils.auth import verify_password, create_access_token
from config import ACCESS_TOKEN_EXPIRE_MINUTES

# 创建路由器
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)

# 定义OAuth2密码流
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录获取访问令牌
    
    Args:
        form_data: OAuth2表单数据，包含用户名和密码
        db: 数据库会话
        
    Returns:
        Token: 包含访问令牌和令牌类型的响应
        
    Raises:
        HTTPException: 如果用户名或密码不正确
    """
    try:
        # 查找用户
        user = db.query(User).filter(User.username == form_data.username).first()
        
        # 验证用户存在且密码正确
        if not user or not verify_password(form_data.password, str(user.password_hash)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码不正确",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 验证用户是否激活
        if not bool(user.is_active):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户已被禁用",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"登录时出错: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器内部错误: {str(e)}"
        ) 