from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# 用户画像相关Schema
class UserProfileBase(BaseModel):
    """用户画像基础模型"""
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    occupation: Optional[str] = Field(None, description="职业")
    education_level: Optional[str] = Field(None, description="教育程度")
    annual_income: Optional[float] = Field(None, description="年收入")
    investment_experience: Optional[str] = Field(None, description="投资经验")
    risk_tolerance_score: Optional[float] = Field(None, description="风险承受能力评分 (1-10)")
    investment_horizon: Optional[str] = Field(None, description="投资期限")
    liquidity_needs: Optional[str] = Field(None, description="流动性需求")
    primary_goal: Optional[str] = Field(None, description="主要投资目标")
    secondary_goal: Optional[str] = Field(None, description="次要投资目标")
    target_return: Optional[float] = Field(None, description="目标收益率")
    max_drawdown_tolerance: Optional[float] = Field(None, description="最大回撤容忍度")
    loss_aversion_score: Optional[float] = Field(None, description="损失厌恶程度")
    disposition_effect_score: Optional[float] = Field(None, description="处置效应程度")
    overconfidence_score: Optional[float] = Field(None, description="过度自信程度")

class UserProfileCreate(UserProfileBase):
    """创建用户画像请求模型"""
    user_id: int = Field(..., description="用户ID")

class UserProfileUpdate(BaseModel):
    """更新用户画像请求模型"""
    age: Optional[int] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    education_level: Optional[str] = None
    annual_income: Optional[float] = None
    investment_experience: Optional[str] = None
    risk_tolerance_score: Optional[float] = None
    investment_horizon: Optional[str] = None
    liquidity_needs: Optional[str] = None
    primary_goal: Optional[str] = None
    secondary_goal: Optional[str] = None
    target_return: Optional[float] = None
    max_drawdown_tolerance: Optional[float] = None
    loss_aversion_score: Optional[float] = None
    disposition_effect_score: Optional[float] = None
    overconfidence_score: Optional[float] = None

class UserProfileResponse(UserProfileBase):
    """用户画像响应模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 风险测评相关Schema
class RiskAssessmentBase(BaseModel):
    """风险测评基础模型"""
    total_score: int = Field(..., description="总分")
    investment_knowledge_score: Optional[int] = Field(None, description="投资知识得分")
    investment_experience_score: Optional[int] = Field(None, description="投资经验得分")
    financial_situation_score: Optional[int] = Field(None, description="财务状况得分")
    risk_attitude_score: Optional[int] = Field(None, description="风险态度得分")
    investment_horizon_score: Optional[int] = Field(None, description="投资期限得分")
    answers: Optional[Dict[str, Any]] = Field(None, description="问卷答案")

class RiskAssessmentCreate(RiskAssessmentBase):
    """创建风险测评请求模型"""
    user_id: int = Field(..., description="用户ID")

class RiskAssessmentResponse(RiskAssessmentBase):
    """风险测评响应模型"""
    id: int
    user_id: int
    risk_level: str = Field(..., description="风险等级")
    risk_tolerance: float = Field(..., description="风险承受能力 (1-10)")
    assessment_date: datetime

    class Config:
        from_attributes = True

# 投资目标相关Schema
class InvestmentGoalBase(BaseModel):
    """投资目标基础模型"""
    goal_name: str = Field(..., description="目标名称")
    goal_type: str = Field(..., description="目标类型")
    target_amount: Optional[float] = Field(None, description="目标金额")
    target_date: Optional[datetime] = Field(None, description="目标日期")
    priority: int = Field(1, description="优先级 (1-5)")
    is_active: bool = Field(True, description="是否激活")
    progress: float = Field(0.0, description="完成进度 (0-100%)")

class InvestmentGoalCreate(InvestmentGoalBase):
    """创建投资目标请求模型"""
    user_id: int = Field(..., description="用户ID")

class InvestmentGoalUpdate(BaseModel):
    """更新投资目标请求模型"""
    goal_name: Optional[str] = None
    goal_type: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[datetime] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    progress: Optional[float] = None

class InvestmentGoalResponse(InvestmentGoalBase):
    """投资目标响应模型"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 