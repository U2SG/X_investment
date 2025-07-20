"""
数据模型包
定义应用中使用的数据库模型
"""
# 导入SQLAlchemy组件
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship

# 从database模块导入Base类
from database import Base

# 导入用户模型
from .user import User
from .user_profile import UserProfile, RiskAssessment, InvestmentGoal

# 导入投资组合模型
from .portfolio import Portfolio, Asset, PortfolioAsset
from .asset_tag import Tag, AssetTag
from .risk import RiskAssessmentResult

# 导入市场数据模型
from .market_data import MarketData, PriceHistory, MarketIndex, IndexHistory

# 导入特征模型
from .feature import Feature
from .feature_lineage import FeatureLineage

# 导入策略模型
from .strategy import (
    Strategy, StrategySignal, BacktestResult, PortfolioAllocation,
    FactorModel, MarketRegime, StrategyType, SignalType, AssetClass,
    MacroTimingSignal, SectorRotationSignal, MultiFactorScore
)

# 导入另类数据模型
from .alternative_data import (
    AlternativeData, SatelliteData, SupplyChainData, 
    RecruitmentData, SentimentData, KnowledgeGraph, AlternativeDataType
)

# 导出所有模型
__all__ = [
    'Base',
    'User',
    'UserProfile',
    'RiskAssessment',
    'InvestmentGoal',
    # 'Portfolio',
    # 'Asset',
    'RiskAssessmentResult',
    'MarketData',
    'PriceHistory', 
    'MarketIndex',
    'IndexHistory',
    'Feature',
    'FeatureLineage',
    'Strategy',
    'StrategySignal',
    'BacktestResult',
    'PortfolioAllocation',
    'FactorModel',
    'MarketRegime',
    'StrategyType',
    'SignalType',
    'AssetClass',
    'MacroTimingSignal',
    'SectorRotationSignal',
    'MultiFactorScore',
    'AlternativeData',
    'SatelliteData',
    'SupplyChainData',
    'RecruitmentData',
    'SentimentData',
    'KnowledgeGraph',
    'AlternativeDataType',
] 