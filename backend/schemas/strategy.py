"""
AI投资策略引擎Schema
定义API请求和响应的数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class StrategyType(str, Enum):
    """策略类型枚举"""
    MACRO_TIMING = "MACRO_TIMING"
    SECTOR_ROTATION = "SECTOR_ROTATION"
    MULTI_FACTOR = "MULTI_FACTOR"
    MOMENTUM = "MOMENTUM"
    MEAN_REVERSION = "MEAN_REVERSION"
    ARBITRAGE = "ARBITRAGE"
    CUSTOM = "CUSTOM"


class SignalType(str, Enum):
    """信号类型枚举"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    OVERWEIGHT = "OVERWEIGHT"
    UNDERWEIGHT = "UNDERWEIGHT"


class AssetClass(str, Enum):
    """资产类别枚举"""
    STOCK = "STOCK"
    BOND = "BOND"
    COMMODITY = "COMMODITY"
    CASH = "CASH"
    REAL_ESTATE = "REAL_ESTATE"
    ALTERNATIVE = "ALTERNATIVE"


# Strategy Schemas
class StrategyBase(BaseModel):
    """策略基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    strategy_type: StrategyType = Field(..., description="策略类型")
    asset_class: AssetClass = Field(..., description="目标资产类别")
    parameters: Optional[Dict[str, Any]] = Field(None, description="策略参数配置")
    risk_level: int = Field(default=3, ge=1, le=5, description="风险等级(1-5)")
    expected_return: Optional[float] = Field(None, description="预期年化收益率")
    max_drawdown: Optional[float] = Field(None, description="最大回撤限制")


class StrategyCreate(StrategyBase):
    """创建策略Schema"""
    pass


class StrategyUpdate(BaseModel):
    """更新策略Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    strategy_type: Optional[StrategyType] = Field(None, description="策略类型")
    asset_class: Optional[AssetClass] = Field(None, description="目标资产类别")
    parameters: Optional[Dict[str, Any]] = Field(None, description="策略参数配置")
    risk_level: Optional[int] = Field(None, ge=1, le=5, description="风险等级(1-5)")
    expected_return: Optional[float] = Field(None, description="预期年化收益率")
    max_drawdown: Optional[float] = Field(None, description="最大回撤限制")
    is_active: Optional[bool] = Field(None, description="是否活跃")


class StrategyResponse(StrategyBase):
    """策略响应Schema"""
    id: int = Field(..., description="策略ID")
    is_active: bool = Field(..., description="是否活跃")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


# StrategySignal Schemas
class StrategySignalBase(BaseModel):
    """策略信号基础Schema"""
    signal_type: SignalType = Field(..., description="信号类型")
    signal_strength: float = Field(default=1.0, ge=0.0, le=1.0, description="信号强度(0-1)")
    target_weight: Optional[float] = Field(None, description="目标权重")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="置信度分数")
    reasoning: Optional[str] = Field(None, description="信号推理过程")
    factors: Optional[Dict[str, Any]] = Field(None, description="影响因子")
    signal_date: datetime = Field(..., description="信号日期")


class StrategySignalCreate(StrategySignalBase):
    """创建策略信号Schema"""
    strategy_id: int = Field(..., description="策略ID")
    market_data_id: int = Field(..., description="市场数据ID")


class StrategySignalUpdate(BaseModel):
    """更新策略信号Schema"""
    signal_type: Optional[SignalType] = Field(None, description="信号类型")
    signal_strength: Optional[float] = Field(None, ge=0.0, le=1.0, description="信号强度(0-1)")
    target_weight: Optional[float] = Field(None, description="目标权重")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="置信度分数")
    reasoning: Optional[str] = Field(None, description="信号推理过程")
    factors: Optional[Dict[str, Any]] = Field(None, description="影响因子")


class StrategySignalResponse(StrategySignalBase):
    """策略信号响应Schema"""
    id: int = Field(..., description="信号ID")
    strategy_id: int = Field(..., description="策略ID")
    market_data_id: int = Field(..., description="市场数据ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# BacktestResult Schemas
class BacktestResultBase(BaseModel):
    """回测结果基础Schema"""
    start_date: datetime = Field(..., description="回测开始日期")
    end_date: datetime = Field(..., description="回测结束日期")
    initial_capital: float = Field(..., gt=0, description="初始资金")


class BacktestResultCreate(BacktestResultBase):
    """创建回测结果Schema"""
    strategy_id: int = Field(..., description="策略ID")
    total_return: Optional[float] = Field(None, description="总收益率")
    annualized_return: Optional[float] = Field(None, description="年化收益率")
    volatility: Optional[float] = Field(None, description="波动率")
    sharpe_ratio: Optional[float] = Field(None, description="夏普比率")
    sortino_ratio: Optional[float] = Field(None, description="索提诺比率")
    max_drawdown: Optional[float] = Field(None, description="最大回撤")
    calmar_ratio: Optional[float] = Field(None, description="卡玛比率")
    var_95: Optional[float] = Field(None, description="95%置信度VaR")
    cvar_95: Optional[float] = Field(None, description="95%置信度CVaR")
    beta: Optional[float] = Field(None, description="贝塔系数")
    alpha: Optional[float] = Field(None, description="阿尔法系数")
    total_trades: Optional[int] = Field(None, description="总交易次数")
    winning_trades: Optional[int] = Field(None, description="盈利交易次数")
    losing_trades: Optional[int] = Field(None, description="亏损交易次数")
    win_rate: Optional[float] = Field(None, description="胜率")
    avg_win: Optional[float] = Field(None, description="平均盈利")
    avg_loss: Optional[float] = Field(None, description="平均亏损")
    profit_factor: Optional[float] = Field(None, description="盈亏比")
    performance_data: Optional[Dict[str, Any]] = Field(None, description="绩效数据")
    trade_log: Optional[Dict[str, Any]] = Field(None, description="交易记录")
    factor_analysis: Optional[Dict[str, Any]] = Field(None, description="因子分析结果")


class BacktestResultUpdate(BaseModel):
    """更新回测结果Schema"""
    total_return: Optional[float] = Field(None, description="总收益率")
    annualized_return: Optional[float] = Field(None, description="年化收益率")
    volatility: Optional[float] = Field(None, description="波动率")
    sharpe_ratio: Optional[float] = Field(None, description="夏普比率")
    sortino_ratio: Optional[float] = Field(None, description="索提诺比率")
    max_drawdown: Optional[float] = Field(None, description="最大回撤")
    calmar_ratio: Optional[float] = Field(None, description="卡玛比率")
    var_95: Optional[float] = Field(None, description="95%置信度VaR")
    cvar_95: Optional[float] = Field(None, description="95%置信度CVaR")
    beta: Optional[float] = Field(None, description="贝塔系数")
    alpha: Optional[float] = Field(None, description="阿尔法系数")
    total_trades: Optional[int] = Field(None, description="总交易次数")
    winning_trades: Optional[int] = Field(None, description="盈利交易次数")
    losing_trades: Optional[int] = Field(None, description="亏损交易次数")
    win_rate: Optional[float] = Field(None, description="胜率")
    avg_win: Optional[float] = Field(None, description="平均盈利")
    avg_loss: Optional[float] = Field(None, description="平均亏损")
    profit_factor: Optional[float] = Field(None, description="盈亏比")
    performance_data: Optional[Dict[str, Any]] = Field(None, description="绩效数据")
    trade_log: Optional[Dict[str, Any]] = Field(None, description="交易记录")
    factor_analysis: Optional[Dict[str, Any]] = Field(None, description="因子分析结果")


class BacktestResultResponse(BacktestResultBase):
    """回测结果响应Schema"""
    id: int = Field(..., description="回测结果ID")
    strategy_id: int = Field(..., description="策略ID")
    total_return: Optional[float] = Field(None, description="总收益率")
    annualized_return: Optional[float] = Field(None, description="年化收益率")
    volatility: Optional[float] = Field(None, description="波动率")
    sharpe_ratio: Optional[float] = Field(None, description="夏普比率")
    sortino_ratio: Optional[float] = Field(None, description="索提诺比率")
    max_drawdown: Optional[float] = Field(None, description="最大回撤")
    calmar_ratio: Optional[float] = Field(None, description="卡玛比率")
    var_95: Optional[float] = Field(None, description="95%置信度VaR")
    cvar_95: Optional[float] = Field(None, description="95%置信度CVaR")
    beta: Optional[float] = Field(None, description="贝塔系数")
    alpha: Optional[float] = Field(None, description="阿尔法系数")
    total_trades: Optional[int] = Field(None, description="总交易次数")
    winning_trades: Optional[int] = Field(None, description="盈利交易次数")
    losing_trades: Optional[int] = Field(None, description="亏损交易次数")
    win_rate: Optional[float] = Field(None, description="胜率")
    avg_win: Optional[float] = Field(None, description="平均盈利")
    avg_loss: Optional[float] = Field(None, description="平均亏损")
    profit_factor: Optional[float] = Field(None, description="盈亏比")
    performance_data: Optional[Dict[str, Any]] = Field(None, description="绩效数据")
    trade_log: Optional[Dict[str, Any]] = Field(None, description="交易记录")
    factor_analysis: Optional[Dict[str, Any]] = Field(None, description="因子分析结果")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# PortfolioAllocation Schemas
class PortfolioAllocationBase(BaseModel):
    """投资组合配置基础Schema"""
    allocation_date: datetime = Field(..., description="配置日期")
    target_weights: Dict[str, float] = Field(..., description="目标权重配置")
    actual_weights: Optional[Dict[str, float]] = Field(None, description="实际权重配置")
    rebalance_reason: Optional[str] = Field(None, description="调仓原因")
    risk_metrics: Optional[Dict[str, Any]] = Field(None, description="风险指标")
    expected_return: Optional[float] = Field(None, description="预期收益")


class PortfolioAllocationCreate(PortfolioAllocationBase):
    """创建投资组合配置Schema"""
    strategy_id: int = Field(..., description="策略ID")
    portfolio_id: int = Field(..., description="投资组合ID")


class PortfolioAllocationUpdate(BaseModel):
    """更新投资组合配置Schema"""
    target_weights: Optional[Dict[str, float]] = Field(None, description="目标权重配置")
    actual_weights: Optional[Dict[str, float]] = Field(None, description="实际权重配置")
    rebalance_reason: Optional[str] = Field(None, description="调仓原因")
    risk_metrics: Optional[Dict[str, Any]] = Field(None, description="风险指标")
    expected_return: Optional[float] = Field(None, description="预期收益")
    is_executed: Optional[bool] = Field(None, description="是否已执行")
    execution_date: Optional[datetime] = Field(None, description="执行日期")


class PortfolioAllocationResponse(PortfolioAllocationBase):
    """投资组合配置响应Schema"""
    id: int = Field(..., description="配置ID")
    strategy_id: int = Field(..., description="策略ID")
    portfolio_id: int = Field(..., description="投资组合ID")
    is_executed: bool = Field(..., description="是否已执行")
    execution_date: Optional[datetime] = Field(None, description="执行日期")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# FactorModel Schemas
class FactorModelBase(BaseModel):
    """因子模型基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="因子模型名称")
    description: Optional[str] = Field(None, description="因子模型描述")
    factors: List[str] = Field(..., description="因子列表")
    factor_weights: Dict[str, float] = Field(..., description="因子权重")
    model_parameters: Optional[Dict[str, Any]] = Field(None, description="模型参数")


class FactorModelCreate(FactorModelBase):
    """创建因子模型Schema"""
    pass


class FactorModelUpdate(BaseModel):
    """更新因子模型Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="因子模型名称")
    description: Optional[str] = Field(None, description="因子模型描述")
    factors: Optional[List[str]] = Field(None, description="因子列表")
    factor_weights: Optional[Dict[str, float]] = Field(None, description="因子权重")
    model_parameters: Optional[Dict[str, Any]] = Field(None, description="模型参数")
    is_active: Optional[bool] = Field(None, description="是否活跃")


class FactorModelResponse(FactorModelBase):
    """因子模型响应Schema"""
    id: int = Field(..., description="因子模型ID")
    is_active: bool = Field(..., description="是否活跃")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# MarketRegime Schemas
class MarketRegimeBase(BaseModel):
    """市场状态基础Schema"""
    regime_name: str = Field(..., min_length=1, max_length=50, description="状态名称")
    description: Optional[str] = Field(None, description="状态描述")
    economic_cycle: Optional[str] = Field(None, description="经济周期")
    market_sentiment: Optional[str] = Field(None, description="市场情绪")
    volatility_regime: Optional[str] = Field(None, description="波动率状态")
    regime_indicators: Optional[Dict[str, Any]] = Field(None, description="状态指标")
    transition_probabilities: Optional[Dict[str, float]] = Field(None, description="转移概率")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")


class MarketRegimeCreate(MarketRegimeBase):
    """创建市场状态Schema"""
    pass


class MarketRegimeUpdate(BaseModel):
    """更新市场状态Schema"""
    regime_name: Optional[str] = Field(None, min_length=1, max_length=50, description="状态名称")
    description: Optional[str] = Field(None, description="状态描述")
    economic_cycle: Optional[str] = Field(None, description="经济周期")
    market_sentiment: Optional[str] = Field(None, description="市场情绪")
    volatility_regime: Optional[str] = Field(None, description="波动率状态")
    regime_indicators: Optional[Dict[str, Any]] = Field(None, description="状态指标")
    transition_probabilities: Optional[Dict[str, float]] = Field(None, description="转移概率")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")


class MarketRegimeResponse(MarketRegimeBase):
    """市场状态响应Schema"""
    id: int = Field(..., description="市场状态ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# 复合响应Schema
class StrategyWithSignals(StrategyResponse):
    """包含信号的策略响应"""
    signals: List[StrategySignalResponse] = Field(default=[], description="策略信号")


class StrategyWithBacktest(StrategyResponse):
    """包含回测结果的策略响应"""
    backtest_results: List[BacktestResultResponse] = Field(default=[], description="回测结果")


class StrategyWithAllocations(StrategyResponse):
    """包含配置的策略响应"""
    portfolio_allocations: List[PortfolioAllocationResponse] = Field(default=[], description="投资组合配置")


# 查询参数Schema
class StrategyQuery(BaseModel):
    """策略查询参数"""
    strategy_type: Optional[StrategyType] = Field(None, description="策略类型")
    asset_class: Optional[AssetClass] = Field(None, description="资产类别")
    risk_level: Optional[int] = Field(None, ge=1, le=5, description="风险等级")
    is_active: Optional[bool] = Field(None, description="是否活跃")
    limit: int = Field(default=100, ge=1, le=1000, description="限制数量")
    offset: int = Field(default=0, ge=0, description="偏移量")


class SignalQuery(BaseModel):
    """信号查询参数"""
    strategy_id: Optional[int] = Field(None, description="策略ID")
    signal_type: Optional[SignalType] = Field(None, description="信号类型")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    limit: int = Field(default=100, ge=1, le=1000, description="限制数量")
    offset: int = Field(default=0, ge=0, description="偏移量")


class BacktestQuery(BaseModel):
    """回测查询参数"""
    strategy_id: Optional[int] = Field(None, description="策略ID")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    limit: int = Field(default=100, ge=1, le=1000, description="限制数量")
    offset: int = Field(default=0, ge=0, description="偏移量") 