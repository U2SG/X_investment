"""
用户相关的API路由
包括用户注册、获取用户信息等功能
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
import sys
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加父目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database import get_db
from models import User, RiskAssessmentResult
from schemas.user import UserCreate, UserResponse
from utils.auth import hash_password, get_current_active_user

# 创建路由器
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "用户未找到"}},
)

# 简单内存存储（演示用）
RISK_ASSESSMENT_RESULTS = []

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户
    
    Args:
        user: 用户创建请求模型
        db: 数据库会话
        
    Returns:
        UserResponse: 创建的用户信息
        
    Raises:
        HTTPException: 如果用户名或邮箱已存在
    """
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被注册"
        )
    
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户对象，密码进行哈希处理
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hash_password(user.password)
    )
    
    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户信息
    
    Args:
        user_id: 用户ID
        db: 数据库会话
        
    Returns:
        UserResponse: 用户信息
        
    Raises:
        HTTPException: 如果用户不存在
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return db_user

@router.get("/me/", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    获取当前登录用户信息
    
    Args:
        current_user: 当前登录用户，通过依赖注入获取
        
    Returns:
        UserResponse: 当前用户信息
    """
    return current_user 

@router.post("/risk_assessment/submit")
def submit_risk_assessment(
    answers: dict = Body(..., description="风险测评问卷答案"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    提交风险测评问卷答案，写入数据库。
    - 参数: answers (dict): 问卷答案
    - 返回: {"detail": "提交成功"}
    """
    result = RiskAssessmentResult(user_id=current_user.id, answers=answers)
    db.add(result)
    db.commit()
    return {"detail": "提交成功"} 

@router.get("/risk_assessment/latest")
def get_latest_risk_assessment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    查询当前用户最近一次风险测评结果。
    - 返回: {answers: dict, created_at: datetime} 或 404
    """
    result = db.query(RiskAssessmentResult).filter(RiskAssessmentResult.user_id == current_user.id).order_by(RiskAssessmentResult.created_at.desc()).first()
    if not result:
        raise HTTPException(status_code=404, detail="未找到风险测评记录")
    return {"answers": result.answers, "created_at": result.created_at} 