from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.user_profile import UserProfile, RiskAssessment, InvestmentGoal
from models.user import User
from schemas.user_profile import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse,
    RiskAssessmentCreate,
    RiskAssessmentResponse,
    InvestmentGoalCreate,
    InvestmentGoalUpdate,
    InvestmentGoalResponse
)
import json

router = APIRouter(prefix="/user-profile", tags=["user-profile"])

@router.post("/", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def create_user_profile(profile: UserProfileCreate, db: Session = Depends(get_db)):
    """创建用户画像"""
    # 验证用户是否存在
    user = db.query(User).filter(User.id == profile.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 检查是否已存在用户画像
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == profile.user_id).first()
    if existing_profile:
        raise HTTPException(status_code=400, detail="用户画像已存在")
    
    # 创建用户画像
    db_profile = UserProfile(**profile.model_dump())
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    
    return UserProfileResponse(
        id=getattr(db_profile, 'id'),
        user_id=getattr(db_profile, 'user_id'),
        age=getattr(db_profile, 'age'),
        gender=getattr(db_profile, 'gender'),
        occupation=getattr(db_profile, 'occupation'),
        education_level=getattr(db_profile, 'education_level'),
        annual_income=getattr(db_profile, 'annual_income'),
        investment_experience=getattr(db_profile, 'investment_experience'),
        risk_tolerance_score=getattr(db_profile, 'risk_tolerance_score'),
        investment_horizon=getattr(db_profile, 'investment_horizon'),
        liquidity_needs=getattr(db_profile, 'liquidity_needs'),
        primary_goal=getattr(db_profile, 'primary_goal'),
        secondary_goal=getattr(db_profile, 'secondary_goal'),
        target_return=getattr(db_profile, 'target_return'),
        max_drawdown_tolerance=getattr(db_profile, 'max_drawdown_tolerance'),
        loss_aversion_score=getattr(db_profile, 'loss_aversion_score'),
        disposition_effect_score=getattr(db_profile, 'disposition_effect_score'),
        overconfidence_score=getattr(db_profile, 'overconfidence_score'),
        created_at=getattr(db_profile, 'created_at'),
        updated_at=getattr(db_profile, 'updated_at')
    )

@router.get("/{user_id}", response_model=UserProfileResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """获取用户画像"""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    return UserProfileResponse(
        id=getattr(profile, 'id'),
        user_id=getattr(profile, 'user_id'),
        age=getattr(profile, 'age'),
        gender=getattr(profile, 'gender'),
        occupation=getattr(profile, 'occupation'),
        education_level=getattr(profile, 'education_level'),
        annual_income=getattr(profile, 'annual_income'),
        investment_experience=getattr(profile, 'investment_experience'),
        risk_tolerance_score=getattr(profile, 'risk_tolerance_score'),
        investment_horizon=getattr(profile, 'investment_horizon'),
        liquidity_needs=getattr(profile, 'liquidity_needs'),
        primary_goal=getattr(profile, 'primary_goal'),
        secondary_goal=getattr(profile, 'secondary_goal'),
        target_return=getattr(profile, 'target_return'),
        max_drawdown_tolerance=getattr(profile, 'max_drawdown_tolerance'),
        loss_aversion_score=getattr(profile, 'loss_aversion_score'),
        disposition_effect_score=getattr(profile, 'disposition_effect_score'),
        overconfidence_score=getattr(profile, 'overconfidence_score'),
        created_at=getattr(profile, 'created_at'),
        updated_at=getattr(profile, 'updated_at')
    )

@router.put("/{user_id}", response_model=UserProfileResponse)
def update_user_profile(user_id: int, profile_update: UserProfileUpdate, db: Session = Depends(get_db)):
    """更新用户画像"""
    db_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    if not db_profile:
        raise HTTPException(status_code=404, detail="用户画像不存在")
    
    # 更新字段
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    db.commit()
    db.refresh(db_profile)
    
    return UserProfileResponse(
        id=getattr(db_profile, 'id'),
        user_id=getattr(db_profile, 'user_id'),
        age=getattr(db_profile, 'age'),
        gender=getattr(db_profile, 'gender'),
        occupation=getattr(db_profile, 'occupation'),
        education_level=getattr(db_profile, 'education_level'),
        annual_income=getattr(db_profile, 'annual_income'),
        investment_experience=getattr(db_profile, 'investment_experience'),
        risk_tolerance_score=getattr(db_profile, 'risk_tolerance_score'),
        investment_horizon=getattr(db_profile, 'investment_horizon'),
        liquidity_needs=getattr(db_profile, 'liquidity_needs'),
        primary_goal=getattr(db_profile, 'primary_goal'),
        secondary_goal=getattr(db_profile, 'secondary_goal'),
        target_return=getattr(db_profile, 'target_return'),
        max_drawdown_tolerance=getattr(db_profile, 'max_drawdown_tolerance'),
        loss_aversion_score=getattr(db_profile, 'loss_aversion_score'),
        disposition_effect_score=getattr(db_profile, 'disposition_effect_score'),
        overconfidence_score=getattr(db_profile, 'overconfidence_score'),
        created_at=getattr(db_profile, 'created_at'),
        updated_at=getattr(db_profile, 'updated_at')
    )

# 风险测评相关接口
@router.post("/risk-assessment", response_model=RiskAssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_risk_assessment(assessment: RiskAssessmentCreate, db: Session = Depends(get_db)):
    """创建风险测评记录"""
    # 验证用户是否存在
    user = db.query(User).filter(User.id == assessment.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 计算风险等级
    risk_level = calculate_risk_level(assessment.total_score)
    risk_tolerance = calculate_risk_tolerance(assessment.total_score)
    
    # 创建风险测评记录
    db_assessment = RiskAssessment(
        user_id=assessment.user_id,
        total_score=assessment.total_score,
        risk_level=risk_level,
        risk_tolerance=risk_tolerance,
        investment_knowledge_score=assessment.investment_knowledge_score,
        investment_experience_score=assessment.investment_experience_score,
        financial_situation_score=assessment.financial_situation_score,
        risk_attitude_score=assessment.risk_attitude_score,
        investment_horizon_score=assessment.investment_horizon_score,
        answers=json.dumps(assessment.answers) if assessment.answers else None
    )
    
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    
    return RiskAssessmentResponse(
        id=getattr(db_assessment, 'id'),
        user_id=getattr(db_assessment, 'user_id'),
        total_score=getattr(db_assessment, 'total_score'),
        risk_level=getattr(db_assessment, 'risk_level'),
        risk_tolerance=getattr(db_assessment, 'risk_tolerance'),
        investment_knowledge_score=getattr(db_assessment, 'investment_knowledge_score'),
        investment_experience_score=getattr(db_assessment, 'investment_experience_score'),
        financial_situation_score=getattr(db_assessment, 'financial_situation_score'),
        risk_attitude_score=getattr(db_assessment, 'risk_attitude_score'),
        investment_horizon_score=getattr(db_assessment, 'investment_horizon_score'),
        answers=json.loads(getattr(db_assessment, 'answers')) if getattr(db_assessment, 'answers') else None,
        assessment_date=getattr(db_assessment, 'assessment_date')
    )

@router.get("/risk-assessment/{user_id}", response_model=List[RiskAssessmentResponse])
def get_user_risk_assessments(user_id: int, db: Session = Depends(get_db)):
    """获取用户的风险测评记录"""
    assessments = db.query(RiskAssessment).filter(RiskAssessment.user_id == user_id).order_by(RiskAssessment.assessment_date.desc()).all()
    
    result = []
    for assessment in assessments:
        result.append(RiskAssessmentResponse(
            id=getattr(assessment, 'id'),
            user_id=getattr(assessment, 'user_id'),
            total_score=getattr(assessment, 'total_score'),
            risk_level=getattr(assessment, 'risk_level'),
            risk_tolerance=getattr(assessment, 'risk_tolerance'),
            investment_knowledge_score=getattr(assessment, 'investment_knowledge_score'),
            investment_experience_score=getattr(assessment, 'investment_experience_score'),
            financial_situation_score=getattr(assessment, 'financial_situation_score'),
            risk_attitude_score=getattr(assessment, 'risk_attitude_score'),
            investment_horizon_score=getattr(assessment, 'investment_horizon_score'),
            answers=json.loads(getattr(assessment, 'answers')) if getattr(assessment, 'answers') else None,
            assessment_date=getattr(assessment, 'assessment_date')
        ))
    
    return result

# 投资目标相关接口
@router.post("/investment-goals", response_model=InvestmentGoalResponse, status_code=status.HTTP_201_CREATED)
def create_investment_goal(goal: InvestmentGoalCreate, db: Session = Depends(get_db)):
    """创建投资目标"""
    # 验证用户是否存在
    user = db.query(User).filter(User.id == goal.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 创建投资目标
    db_goal = InvestmentGoal(**goal.model_dump())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    
    return InvestmentGoalResponse(
        id=getattr(db_goal, 'id'),
        user_id=getattr(db_goal, 'user_id'),
        goal_name=getattr(db_goal, 'goal_name'),
        goal_type=getattr(db_goal, 'goal_type'),
        target_amount=getattr(db_goal, 'target_amount'),
        target_date=getattr(db_goal, 'target_date'),
        priority=getattr(db_goal, 'priority'),
        is_active=getattr(db_goal, 'is_active'),
        progress=getattr(db_goal, 'progress'),
        created_at=getattr(db_goal, 'created_at'),
        updated_at=getattr(db_goal, 'updated_at')
    )

@router.get("/investment-goals/{user_id}", response_model=List[InvestmentGoalResponse])
def get_user_investment_goals(user_id: int, db: Session = Depends(get_db)):
    """获取用户的投资目标"""
    goals = db.query(InvestmentGoal).filter(InvestmentGoal.user_id == user_id).order_by(InvestmentGoal.priority).all()
    
    result = []
    for goal in goals:
        result.append(InvestmentGoalResponse(
            id=getattr(goal, 'id'),
            user_id=getattr(goal, 'user_id'),
            goal_name=getattr(goal, 'goal_name'),
            goal_type=getattr(goal, 'goal_type'),
            target_amount=getattr(goal, 'target_amount'),
            target_date=getattr(goal, 'target_date'),
            priority=getattr(goal, 'priority'),
            is_active=getattr(goal, 'is_active'),
            progress=getattr(goal, 'progress'),
            created_at=getattr(goal, 'created_at'),
            updated_at=getattr(goal, 'updated_at')
        ))
    
    return result

@router.put("/investment-goals/{goal_id}", response_model=InvestmentGoalResponse)
def update_investment_goal(goal_id: int, goal_update: InvestmentGoalUpdate, db: Session = Depends(get_db)):
    """更新投资目标"""
    db_goal = db.query(InvestmentGoal).filter(InvestmentGoal.id == goal_id).first()
    if not db_goal:
        raise HTTPException(status_code=404, detail="投资目标不存在")
    
    # 更新字段
    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_goal, field, value)
    
    db.commit()
    db.refresh(db_goal)
    
    return InvestmentGoalResponse(
        id=getattr(db_goal, 'id'),
        user_id=getattr(db_goal, 'user_id'),
        goal_name=getattr(db_goal, 'goal_name'),
        goal_type=getattr(db_goal, 'goal_type'),
        target_amount=getattr(db_goal, 'target_amount'),
        target_date=getattr(db_goal, 'target_date'),
        priority=getattr(db_goal, 'priority'),
        is_active=getattr(db_goal, 'is_active'),
        progress=getattr(db_goal, 'progress'),
        created_at=getattr(db_goal, 'created_at'),
        updated_at=getattr(db_goal, 'updated_at')
    )

# 辅助函数
def calculate_risk_level(total_score: int) -> str:
    """根据总分计算风险等级"""
    if total_score <= 20:
        return "保守"
    elif total_score <= 40:
        return "稳健"
    elif total_score <= 60:
        return "积极"
    else:
        return "激进"

def calculate_risk_tolerance(total_score: int) -> float:
    """根据总分计算风险承受能力 (1-10)"""
    # 将总分映射到1-10的风险承受能力
    return min(10.0, max(1.0, total_score / 10.0)) 