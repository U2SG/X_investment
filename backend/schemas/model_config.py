"""
模型参数配置Schema
"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class ModelParameter(BaseModel):
    """模型参数"""
    name: str = Field(..., description="参数名称")
    value: Any = Field(..., description="参数值")
    type: str = Field(..., description="参数类型")
    description: Optional[str] = Field(None, description="参数描述")
    min_value: Optional[float] = Field(None, description="最小值")
    max_value: Optional[float] = Field(None, description="最大值")
    step: Optional[float] = Field(None, description="步长")


class ModelConfig(BaseModel):
    """模型配置"""
    model_name: str = Field(..., description="模型名称")
    model_version: str = Field(..., description="模型版本")
    parameters: Dict[str, ModelParameter] = Field(..., description="模型参数")
    description: Optional[str] = Field(None, description="模型描述")
    is_active: bool = Field(True, description="是否激活")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ModelConfigCreate(BaseModel):
    """创建模型配置"""
    model_name: str = Field(..., description="模型名称")
    model_version: str = Field(..., description="模型版本")
    parameters: Dict[str, Any] = Field(..., description="模型参数")
    description: Optional[str] = Field(None, description="模型描述")
    is_active: bool = Field(True, description="是否激活")


class ModelConfigUpdate(BaseModel):
    """更新模型配置"""
    parameters: Optional[Dict[str, Any]] = Field(None, description="模型参数")
    description: Optional[str] = Field(None, description="模型描述")
    is_active: Optional[bool] = Field(None, description="是否激活")


class ModelConfigResponse(BaseModel):
    """模型配置响应"""
    id: int
    model_name: str
    model_version: str
    parameters: Dict[str, Any]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class MacroTimingConfig(BaseModel):
    """宏观择时模型配置"""
    # 经济周期权重
    economic_cycle_weight: float = Field(0.4, ge=0.0, le=1.0, description="经济周期权重")
    sentiment_weight: float = Field(0.4, ge=0.0, le=1.0, description="市场情绪权重")
    factors_weight: float = Field(0.2, ge=0.0, le=1.0, description="额外因素权重")
    
    # 配置阈值
    aggressive_threshold: float = Field(0.7, ge=0.5, le=0.9, description="积极配置阈值")
    balanced_threshold: float = Field(0.5, ge=0.3, le=0.7, description="均衡配置阈值")
    defensive_threshold: float = Field(0.3, ge=0.1, le=0.5, description="防御配置阈值")
    
    # 利率调整参数
    high_interest_rate_threshold: float = Field(5.0, ge=3.0, le=8.0, description="高利率阈值")
    low_interest_rate_threshold: float = Field(2.0, ge=0.0, le=4.0, description="低利率阈值")
    
    # 通胀调整参数
    high_inflation_threshold: float = Field(4.0, ge=2.0, le=6.0, description="高通胀阈值")
    low_inflation_threshold: float = Field(2.0, ge=0.0, le=4.0, description="低通胀阈值")
    
    # 地缘政治风险阈值
    geopolitical_risk_threshold: float = Field(0.7, ge=0.5, le=0.9, description="地缘政治风险阈值")


class SectorRotationConfig(BaseModel):
    """行业轮动模型配置"""
    # 行业配置权重
    top_industry_weight: float = Field(0.4, ge=0.2, le=0.6, description="第一行业权重")
    second_industry_weight: float = Field(0.3, ge=0.1, le=0.5, description="第二行业权重")
    third_industry_weight: float = Field(0.2, ge=0.05, le=0.4, description="第三行业权重")
    
    # 资金流向调整参数
    fund_flow_adjustment_factor: float = Field(0.1, ge=0.05, le=0.2, description="资金流向调整因子")
    max_fund_flow_adjustment: float = Field(0.2, ge=0.1, le=0.3, description="最大资金流向调整幅度")
    
    # 政策支持调整参数
    policy_support_multiplier: float = Field(1.2, ge=1.0, le=1.5, description="政策支持倍数")
    max_policy_adjustment: float = Field(0.5, ge=0.3, le=0.7, description="最大政策调整幅度")


class MultiFactorConfig(BaseModel):
    """多因子模型配置"""
    # 默认因子权重
    default_value_weight: float = Field(0.3, ge=0.1, le=0.5, description="价值因子默认权重")
    default_growth_weight: float = Field(0.3, ge=0.1, le=0.5, description="成长因子默认权重")
    default_quality_weight: float = Field(0.2, ge=0.1, le=0.4, description="质量因子默认权重")
    default_momentum_weight: float = Field(0.2, ge=0.1, le=0.4, description="动量因子默认权重")
    
    # 市场状态调整参数
    bull_market_momentum_multiplier: float = Field(1.3, ge=1.1, le=1.5, description="牛市动量因子倍数")
    bull_market_growth_multiplier: float = Field(1.2, ge=1.0, le=1.4, description="牛市成长因子倍数")
    bear_market_value_multiplier: float = Field(1.3, ge=1.1, le=1.5, description="熊市价值因子倍数")
    bear_market_quality_multiplier: float = Field(1.2, ge=1.0, le=1.4, description="熊市质量因子倍数")
    
    # 因子挖掘参数
    min_stocks_for_discovery: int = Field(10, ge=5, le=50, description="因子挖掘最小股票数量")
    industry_score_threshold: float = Field(0.15, ge=0.05, le=0.25, description="行业景气度阈值")
    market_cap_factor_scale: float = Field(1e8, ge=1e7, le=1e9, description="市值因子缩放系数")
    volatility_factor_scale: float = Field(0.3, ge=0.1, le=0.5, description="波动率因子缩放系数")


class ModelConfigTemplate(BaseModel):
    """模型配置模板"""
    macro_timing: MacroTimingConfig = Field(default_factory=MacroTimingConfig, description="宏观择时模型配置")
    sector_rotation: SectorRotationConfig = Field(default_factory=SectorRotationConfig, description="行业轮动模型配置")
    multi_factor: MultiFactorConfig = Field(default_factory=MultiFactorConfig, description="多因子模型配置") 