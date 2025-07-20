"""
AI投资策略引擎模型
定义投资策略、信号、回测结果等数据结构
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class StrategyType(enum.Enum):
    """策略类型枚举"""
    MACRO_TIMING = "MACRO_TIMING"  # 宏观择时
    SECTOR_ROTATION = "SECTOR_ROTATION"  # 行业轮动
    MULTI_FACTOR = "MULTI_FACTOR"  # 多因子模型
    MOMENTUM = "MOMENTUM"  # 动量策略
    MEAN_REVERSION = "MEAN_REVERSION"  # 均值回归
    ARBITRAGE = "ARBITRAGE"  # 套利策略
    CUSTOM = "CUSTOM"  # 自定义策略


class SignalType(enum.Enum):
    """信号类型枚举"""
    BUY = "BUY"  # 买入信号
    SELL = "SELL"  # 卖出信号
    HOLD = "HOLD"  # 持有信号
    OVERWEIGHT = "OVERWEIGHT"  # 超配信号
    UNDERWEIGHT = "UNDERWEIGHT"  # 低配信号


class AssetClass(enum.Enum):
    """资产类别枚举"""
    STOCK = "STOCK"  # 股票
    BOND = "BOND"  # 债券
    COMMODITY = "COMMODITY"  # 商品
    CASH = "CASH"  # 现金
    REAL_ESTATE = "REAL_ESTATE"  # 房地产
    ALTERNATIVE = "ALTERNATIVE"  # 另类投资


class Strategy(Base):
    """投资策略模型"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="策略名称")
    description = Column(Text, comment="策略描述")
    strategy_type = Column(Enum(StrategyType), nullable=False, comment="策略类型")
    asset_class = Column(Enum(AssetClass), nullable=False, comment="目标资产类别")
    
    # 策略参数
    parameters = Column(JSON, comment="策略参数配置")
    risk_level = Column(Integer, default=3, comment="风险等级(1-5)")
    expected_return = Column(Float, comment="预期年化收益率")
    max_drawdown = Column(Float, comment="最大回撤限制")
    
    # 状态管理
    is_active = Column(Boolean, default=True, comment="是否活跃")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关联关系
    signals = relationship("StrategySignal", back_populates="strategy")
    backtest_results = relationship("BacktestResult", back_populates="strategy")
    portfolio_allocations = relationship("PortfolioAllocation", back_populates="strategy")


class StrategySignal(Base):
    """策略信号模型"""
    __tablename__ = "strategy_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, comment="策略ID")
    market_data_id = Column(Integer, ForeignKey("market_data.id"), nullable=False, comment="市场数据ID")
    
    # 信号信息
    signal_type = Column(Enum(SignalType), nullable=False, comment="信号类型")
    signal_strength = Column(Float, default=1.0, comment="信号强度(0-1)")
    target_weight = Column(Float, comment="目标权重")
    confidence_score = Column(Float, comment="置信度分数")
    
    # 信号详情
    reasoning = Column(Text, comment="信号推理过程")
    factors = Column(JSON, comment="影响因子")
    
    # 时间信息
    signal_date = Column(DateTime, nullable=False, comment="信号日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关联关系
    strategy = relationship("Strategy", back_populates="signals")
    market_data = relationship("MarketData")


class BacktestResult(Base):
    """回测结果模型"""
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, comment="策略ID")
    
    # 回测参数
    start_date = Column(DateTime, nullable=False, comment="回测开始日期")
    end_date = Column(DateTime, nullable=False, comment="回测结束日期")
    initial_capital = Column(Float, nullable=False, comment="初始资金")
    
    # 绩效指标
    total_return = Column(Float, comment="总收益率")
    annualized_return = Column(Float, comment="年化收益率")
    volatility = Column(Float, comment="波动率")
    sharpe_ratio = Column(Float, comment="夏普比率")
    sortino_ratio = Column(Float, comment="索提诺比率")
    max_drawdown = Column(Float, comment="最大回撤")
    calmar_ratio = Column(Float, comment="卡玛比率")
    
    # 风险指标
    var_95 = Column(Float, comment="95%置信度VaR")
    cvar_95 = Column(Float, comment="95%置信度CVaR")
    beta = Column(Float, comment="贝塔系数")
    alpha = Column(Float, comment="阿尔法系数")
    
    # 交易统计
    total_trades = Column(Integer, comment="总交易次数")
    winning_trades = Column(Integer, comment="盈利交易次数")
    losing_trades = Column(Integer, comment="亏损交易次数")
    win_rate = Column(Float, comment="胜率")
    avg_win = Column(Float, comment="平均盈利")
    avg_loss = Column(Float, comment="平均亏损")
    profit_factor = Column(Float, comment="盈亏比")
    
    # 回测详情
    performance_data = Column(JSON, comment="绩效数据(净值曲线等)")
    trade_log = Column(JSON, comment="交易记录")
    factor_analysis = Column(JSON, comment="因子分析结果")
    
    # 时间信息
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关联关系
    strategy = relationship("Strategy", back_populates="backtest_results")


class PortfolioAllocation(Base):
    """投资组合配置模型"""
    __tablename__ = "portfolio_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False, comment="策略ID")
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, comment="投资组合ID")
    
    # 配置信息
    allocation_date = Column(DateTime, nullable=False, comment="配置日期")
    target_weights = Column(JSON, comment="目标权重配置")
    actual_weights = Column(JSON, comment="实际权重配置")
    
    # 配置详情
    rebalance_reason = Column(Text, comment="调仓原因")
    risk_metrics = Column(JSON, comment="风险指标")
    expected_return = Column(Float, comment="预期收益")
    
    # 状态管理
    is_executed = Column(Boolean, default=False, comment="是否已执行")
    execution_date = Column(DateTime, comment="执行日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关联关系
    strategy = relationship("Strategy", back_populates="portfolio_allocations")
    portfolio = relationship("Portfolio")


class FactorModel(Base):
    """因子模型"""
    __tablename__ = "factor_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="因子模型名称")
    description = Column(Text, comment="因子模型描述")
    
    # 因子配置
    factors = Column(JSON, comment="因子列表")
    factor_weights = Column(JSON, comment="因子权重")
    model_parameters = Column(JSON, comment="模型参数")
    
    # 模型状态
    is_active = Column(Boolean, default=True, comment="是否活跃")
    last_updated = Column(DateTime, comment="最后更新时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


class MarketRegime(Base):
    """市场状态模型"""
    __tablename__ = "market_regimes"
    
    id = Column(Integer, primary_key=True, index=True)
    regime_name = Column(String(50), nullable=False, comment="状态名称")
    description = Column(Text, comment="状态描述")
    
    # 状态特征
    economic_cycle = Column(String(20), comment="经济周期")
    market_sentiment = Column(String(20), comment="市场情绪")
    volatility_regime = Column(String(20), comment="波动率状态")
    
    # 状态指标
    regime_indicators = Column(JSON, comment="状态指标")
    transition_probabilities = Column(JSON, comment="转移概率")
    
    # 时间信息
    start_date = Column(DateTime, comment="开始日期")
    end_date = Column(DateTime, comment="结束日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")


# === 宏观择时模型相关模型 ===
class MacroTimingSignal(Base):
    """宏观择时信号模型"""
    __tablename__ = "macro_timing_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True, comment="关联策略ID")
    
    # 输入参数
    economic_cycle = Column(String(20), nullable=False, comment="经济周期阶段")
    market_sentiment = Column(String(20), nullable=False, comment="市场情绪")
    additional_factors = Column(JSON, comment="其他影响因子")
    
    # 输出结果
    recommended_allocation = Column(JSON, nullable=False, comment="各类资产建议权重")
    reasoning = Column(Text, comment="推荐理由")
    
    # 信号元数据
    confidence_score = Column(Float, comment="置信度评分")
    model_version = Column(String(20), comment="模型版本")
    signal_date = Column(DateTime, nullable=False, comment="信号生成日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关联关系
    strategy = relationship("Strategy", backref="macro_timing_signals")
    
    # 可选：关联到由此信号生成的策略信号
    derived_signal_id = Column(Integer, ForeignKey("strategy_signals.id"), comment="派生的策略信号ID")
    derived_signal = relationship("StrategySignal", foreign_keys=[derived_signal_id])


# === 行业轮动模型相关模型 ===
class SectorRotationSignal(Base):
    """行业轮动信号模型"""
    __tablename__ = "sector_rotation_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True, comment="关联策略ID")
    
    # 输入参数
    industry_scores = Column(JSON, nullable=False, comment="各行业景气度评分")
    fund_flows = Column(JSON, comment="各行业资金流向")
    additional_factors = Column(JSON, comment="其他影响因子")
    
    # 输出结果
    recommended_industry_allocation = Column(JSON, nullable=False, comment="各行业建议权重")
    reasoning = Column(Text, comment="推荐理由")
    
    # 信号元数据
    confidence_score = Column(Float, comment="置信度评分")
    model_version = Column(String(20), comment="模型版本")
    signal_date = Column(DateTime, nullable=False, comment="信号生成日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关联关系
    strategy = relationship("Strategy", backref="sector_rotation_signals")
    
    # 可选：关联到由此信号生成的策略信号
    derived_signal_id = Column(Integer, ForeignKey("strategy_signals.id"), comment="派生的策略信号ID")
    derived_signal = relationship("StrategySignal", foreign_keys=[derived_signal_id])


# === 多因子模型PLUS相关模型 ===
class MultiFactorScore(Base):
    """多因子评分模型"""
    __tablename__ = "multi_factor_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=True, comment="关联策略ID")
    
    # 输入参数
    stocks_data = Column(JSON, nullable=False, comment="股票因子数据")
    factor_weights = Column(JSON, comment="因子权重")
    market_regime = Column(String(20), comment="市场状态")
    auto_discover = Column(Boolean, default=False, comment="是否启用因子挖掘")
    
    # 输出结果
    stock_scores = Column(JSON, nullable=False, comment="股票评分列表")
    adjusted_weights = Column(JSON, nullable=False, comment="调整后的因子权重")
    discovered_factors = Column(JSON, comment="新发现的因子及其权重")
    reasoning = Column(Text, comment="模型推理过程")
    
    # 元数据
    model_version = Column(String(20), comment="模型版本")
    signal_date = Column(DateTime, nullable=False, comment="信号生成日期")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关联关系
    strategy = relationship("Strategy", backref="multi_factor_scores")
    
    # 可选：关联到由此信号生成的策略信号
    derived_signal_id = Column(Integer, ForeignKey("strategy_signals.id"), comment="派生的策略信号ID")
    derived_signal = relationship("StrategySignal", foreign_keys=[derived_signal_id]) 