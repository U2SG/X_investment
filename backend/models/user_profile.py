from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class UserProfile(Base):
    """用户画像模型"""
    __tablename__ = 'user_profiles'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, unique=True)
    
    # 基本信息
    age = Column(Integer, nullable=True)  # 年龄
    gender = Column(String(10), nullable=True)  # 性别
    occupation = Column(String(100), nullable=True)  # 职业
    education_level = Column(String(50), nullable=True)  # 教育程度
    annual_income = Column(Float, nullable=True)  # 年收入
    investment_experience = Column(String(50), nullable=True)  # 投资经验
    
    # 风险偏好
    risk_tolerance_score = Column(Float, nullable=True)  # 风险承受能力评分 (1-10)
    investment_horizon = Column(String(50), nullable=True)  # 投资期限
    liquidity_needs = Column(String(50), nullable=True)  # 流动性需求
    
    # 投资目标
    primary_goal = Column(String(100), nullable=True)  # 主要投资目标
    secondary_goal = Column(String(100), nullable=True)  # 次要投资目标
    target_return = Column(Float, nullable=True)  # 目标收益率
    max_drawdown_tolerance = Column(Float, nullable=True)  # 最大回撤容忍度
    
    # 行为金融学特征
    loss_aversion_score = Column(Float, nullable=True)  # 损失厌恶程度
    disposition_effect_score = Column(Float, nullable=True)  # 处置效应程度
    overconfidence_score = Column(Float, nullable=True)  # 过度自信程度
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联关系
    user = relationship("User", back_populates="profile")
    
    def __repr__(self):
        return f"<UserProfile(user_id={self.user_id}, risk_score={self.risk_tolerance_score})>"


class RiskAssessment(Base):
    """风险测评记录模型"""
    __tablename__ = 'risk_assessments'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # 测评结果
    total_score = Column(Integer, nullable=False)  # 总分
    risk_level = Column(String(20), nullable=False)  # 风险等级 (保守/稳健/积极/激进)
    risk_tolerance = Column(Float, nullable=False)  # 风险承受能力 (1-10)
    
    # 各维度得分
    investment_knowledge_score = Column(Integer, nullable=True)  # 投资知识得分
    investment_experience_score = Column(Integer, nullable=True)  # 投资经验得分
    financial_situation_score = Column(Integer, nullable=True)  # 财务状况得分
    risk_attitude_score = Column(Integer, nullable=True)  # 风险态度得分
    investment_horizon_score = Column(Integer, nullable=True)  # 投资期限得分
    
    # 测评详情
    answers = Column(Text, nullable=True)  # 问卷答案 (JSON格式)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<RiskAssessment(user_id={self.user_id}, risk_level={self.risk_level})>"


class InvestmentGoal(Base):
    """投资目标模型"""
    __tablename__ = 'investment_goals'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # 目标信息
    goal_name = Column(String(100), nullable=False)  # 目标名称
    goal_type = Column(String(50), nullable=False)  # 目标类型 (退休/购房/教育/其他)
    target_amount = Column(Float, nullable=True)  # 目标金额
    target_date = Column(DateTime, nullable=True)  # 目标日期
    priority = Column(Integer, default=1)  # 优先级 (1-5)
    
    # 目标状态
    is_active = Column(Boolean, default=True)  # 是否激活
    progress = Column(Float, default=0.0)  # 完成进度 (0-100%)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<InvestmentGoal(user_id={self.user_id}, goal_name={self.goal_name})>" 