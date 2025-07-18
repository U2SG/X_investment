"""
AI投资策略引擎API路由
提供策略管理、信号生成、回测分析等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    Strategy, StrategySignal, BacktestResult, PortfolioAllocation,
    FactorModel, MarketRegime, StrategyType, SignalType, AssetClass
)
from models.market_data import MarketData
from schemas.strategy import (
    StrategyCreate, StrategyUpdate, StrategyResponse, StrategyWithSignals,
    StrategySignalCreate, StrategySignalUpdate, StrategySignalResponse,
    BacktestResultCreate, BacktestResultUpdate, BacktestResultResponse,
    PortfolioAllocationCreate, PortfolioAllocationUpdate, PortfolioAllocationResponse,
    FactorModelCreate, FactorModelUpdate, FactorModelResponse,
    MarketRegimeCreate, MarketRegimeUpdate, MarketRegimeResponse,
    StrategyQuery, SignalQuery, BacktestQuery
)

router = APIRouter(prefix="/strategy", tags=["AI投资策略引擎"])


# ==================== 策略管理 ====================

@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
def create_strategy(
    strategy: StrategyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建投资策略"""
    db_strategy = Strategy(**strategy.model_dump())
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.get("/", response_model=List[StrategyResponse])
def get_strategies(
    strategy_type: Optional[str] = Query(None, description="策略类型"),
    asset_class: Optional[str] = Query(None, description="资产类别"),
    risk_level: Optional[int] = Query(None, ge=1, le=5, description="风险等级"),
    is_active: Optional[bool] = Query(None, description="是否活跃"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取策略列表"""
    query = db.query(Strategy)
    
    if strategy_type:
        try:
            strategy_type_enum = StrategyType(strategy_type)
            query = query.filter(Strategy.strategy_type == strategy_type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的策略类型: {strategy_type}")
    if asset_class:
        try:
            asset_class_enum = AssetClass(asset_class)
            query = query.filter(Strategy.asset_class == asset_class_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的资产类别: {asset_class}")
    if risk_level:
        query = query.filter(Strategy.risk_level == risk_level)
    if is_active is not None:
        query = query.filter(Strategy.is_active == is_active)
    
    strategies = query.offset(offset).limit(limit).all()
    return strategies


# ==================== 策略信号管理 ====================

@router.post("/signals", response_model=StrategySignalResponse, status_code=status.HTTP_201_CREATED)
def create_strategy_signal(
    signal: StrategySignalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建策略信号"""
    # 验证策略是否存在
    strategy = db.query(Strategy).filter(Strategy.id == signal.strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    # 验证市场数据是否存在
    market_data = db.query(MarketData).filter(MarketData.id == signal.market_data_id).first()
    if not market_data:
        raise HTTPException(status_code=404, detail="市场数据不存在")
    
    db_signal = StrategySignal(**signal.model_dump())
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal


@router.get("/signals", response_model=List[StrategySignalResponse])
def get_strategy_signals(
    strategy_id: Optional[int] = Query(None, description="策略ID"),
    signal_type: Optional[str] = Query(None, description="信号类型"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取策略信号列表"""
    query = db.query(StrategySignal)
    
    if strategy_id:
        query = query.filter(StrategySignal.strategy_id == strategy_id)
    if signal_type:
        try:
            signal_type_enum = SignalType(signal_type)
            query = query.filter(StrategySignal.signal_type == signal_type_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"无效的信号类型: {signal_type}")
    if start_date:
        query = query.filter(StrategySignal.signal_date >= start_date)
    if end_date:
        query = query.filter(StrategySignal.signal_date <= end_date)
    
    signals = query.order_by(StrategySignal.signal_date.desc()).offset(offset).limit(limit).all()
    return signals


@router.get("/signals/{signal_id}", response_model=StrategySignalResponse)
def get_strategy_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个策略信号"""
    signal = db.query(StrategySignal).filter(StrategySignal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="信号不存在")
    return signal


@router.put("/signals/{signal_id}", response_model=StrategySignalResponse)
def update_strategy_signal(
    signal_id: int,
    signal_update: StrategySignalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新策略信号"""
    db_signal = db.query(StrategySignal).filter(StrategySignal.id == signal_id).first()
    if not db_signal:
        raise HTTPException(status_code=404, detail="信号不存在")
    
    update_data = signal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_signal, field, value)
    
    db.commit()
    db.refresh(db_signal)
    return db_signal


@router.delete("/signals/{signal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除策略信号"""
    db_signal = db.query(StrategySignal).filter(StrategySignal.id == signal_id).first()
    if not db_signal:
        raise HTTPException(status_code=404, detail="信号不存在")
    
    db.delete(db_signal)
    db.commit()


# ==================== 回测结果管理 ====================

@router.post("/backtest", response_model=BacktestResultResponse, status_code=status.HTTP_201_CREATED)
def create_backtest_result(
    backtest: BacktestResultCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建回测结果"""
    # 验证策略是否存在
    strategy = db.query(Strategy).filter(Strategy.id == backtest.strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    db_backtest = BacktestResult(**backtest.model_dump())
    db.add(db_backtest)
    db.commit()
    db.refresh(db_backtest)
    return db_backtest


@router.get("/backtest", response_model=List[BacktestResultResponse])
def get_backtest_results(
    strategy_id: Optional[int] = Query(None, description="策略ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取回测结果列表"""
    query = db.query(BacktestResult)
    
    if strategy_id:
        query = query.filter(BacktestResult.strategy_id == strategy_id)
    if start_date:
        query = query.filter(BacktestResult.start_date >= start_date)
    if end_date:
        query = query.filter(BacktestResult.end_date <= end_date)
    
    backtest_results = query.order_by(BacktestResult.created_at.desc()).offset(offset).limit(limit).all()
    return backtest_results


@router.get("/backtest/{backtest_id}", response_model=BacktestResultResponse)
def get_backtest_result(
    backtest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个回测结果"""
    backtest = db.query(BacktestResult).filter(BacktestResult.id == backtest_id).first()
    if not backtest:
        raise HTTPException(status_code=404, detail="回测结果不存在")
    return backtest


@router.put("/backtest/{backtest_id}", response_model=BacktestResultResponse)
def update_backtest_result(
    backtest_id: int,
    backtest_update: BacktestResultUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新回测结果"""
    db_backtest = db.query(BacktestResult).filter(BacktestResult.id == backtest_id).first()
    if not db_backtest:
        raise HTTPException(status_code=404, detail="回测结果不存在")
    
    update_data = backtest_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_backtest, field, value)
    
    db.commit()
    db.refresh(db_backtest)
    return db_backtest


@router.delete("/backtest/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_backtest_result(
    backtest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除回测结果"""
    db_backtest = db.query(BacktestResult).filter(BacktestResult.id == backtest_id).first()
    if not db_backtest:
        raise HTTPException(status_code=404, detail="回测结果不存在")
    
    db.delete(db_backtest)
    db.commit()


# ==================== 投资组合配置管理 ====================

@router.post("/allocations", response_model=PortfolioAllocationResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio_allocation(
    allocation: PortfolioAllocationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建投资组合配置"""
    # 验证策略是否存在
    strategy = db.query(Strategy).filter(Strategy.id == allocation.strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    # TODO: 验证投资组合是否存在 (需要先实现Portfolio模型)
    # portfolio = db.query(Portfolio).filter(Portfolio.id == allocation.portfolio_id).first()
    # if not portfolio:
    #     raise HTTPException(status_code=404, detail="投资组合不存在")
    
    db_allocation = PortfolioAllocation(**allocation.model_dump())
    db.add(db_allocation)
    db.commit()
    db.refresh(db_allocation)
    return db_allocation


@router.get("/allocations", response_model=List[PortfolioAllocationResponse])
def get_portfolio_allocations(
    strategy_id: Optional[int] = Query(None, description="策略ID"),
    portfolio_id: Optional[int] = Query(None, description="投资组合ID"),
    is_executed: Optional[bool] = Query(None, description="是否已执行"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取投资组合配置列表"""
    query = db.query(PortfolioAllocation)
    
    if strategy_id:
        query = query.filter(PortfolioAllocation.strategy_id == strategy_id)
    if portfolio_id:
        query = query.filter(PortfolioAllocation.portfolio_id == portfolio_id)
    if is_executed is not None:
        query = query.filter(PortfolioAllocation.is_executed == is_executed)
    
    allocations = query.order_by(PortfolioAllocation.allocation_date.desc()).offset(offset).limit(limit).all()
    return allocations


@router.get("/allocations/{allocation_id}", response_model=PortfolioAllocationResponse)
def get_portfolio_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个投资组合配置"""
    allocation = db.query(PortfolioAllocation).filter(PortfolioAllocation.id == allocation_id).first()
    if not allocation:
        raise HTTPException(status_code=404, detail="投资组合配置不存在")
    return allocation


@router.put("/allocations/{allocation_id}", response_model=PortfolioAllocationResponse)
def update_portfolio_allocation(
    allocation_id: int,
    allocation_update: PortfolioAllocationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新投资组合配置"""
    db_allocation = db.query(PortfolioAllocation).filter(PortfolioAllocation.id == allocation_id).first()
    if not db_allocation:
        raise HTTPException(status_code=404, detail="投资组合配置不存在")
    
    update_data = allocation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_allocation, field, value)
    
    db.commit()
    db.refresh(db_allocation)
    return db_allocation


@router.delete("/allocations/{allocation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_allocation(
    allocation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除投资组合配置"""
    db_allocation = db.query(PortfolioAllocation).filter(PortfolioAllocation.id == allocation_id).first()
    if not db_allocation:
        raise HTTPException(status_code=404, detail="投资组合配置不存在")
    
    db.delete(db_allocation)
    db.commit()


# ==================== 因子模型管理 ====================

@router.post("/factors", response_model=FactorModelResponse, status_code=status.HTTP_201_CREATED)
def create_factor_model(
    factor_model: FactorModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建因子模型"""
    db_factor_model = FactorModel(**factor_model.model_dump())
    db.add(db_factor_model)
    db.commit()
    db.refresh(db_factor_model)
    return db_factor_model


@router.get("/factors", response_model=List[FactorModelResponse])
def get_factor_models(
    is_active: Optional[bool] = Query(None, description="是否活跃"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取因子模型列表"""
    query = db.query(FactorModel)
    
    if is_active is not None:
        query = query.filter(FactorModel.is_active == is_active)
    
    factor_models = query.offset(offset).limit(limit).all()
    return factor_models


@router.get("/factors/{factor_model_id}", response_model=FactorModelResponse)
def get_factor_model(
    factor_model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个因子模型"""
    factor_model = db.query(FactorModel).filter(FactorModel.id == factor_model_id).first()
    if not factor_model:
        raise HTTPException(status_code=404, detail="因子模型不存在")
    return factor_model


@router.put("/factors/{factor_model_id}", response_model=FactorModelResponse)
def update_factor_model(
    factor_model_id: int,
    factor_model_update: FactorModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新因子模型"""
    db_factor_model = db.query(FactorModel).filter(FactorModel.id == factor_model_id).first()
    if not db_factor_model:
        raise HTTPException(status_code=404, detail="因子模型不存在")
    
    update_data = factor_model_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_factor_model, field, value)
    
    db.commit()
    db.refresh(db_factor_model)
    return db_factor_model


@router.delete("/factors/{factor_model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_factor_model(
    factor_model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除因子模型"""
    db_factor_model = db.query(FactorModel).filter(FactorModel.id == factor_model_id).first()
    if not db_factor_model:
        raise HTTPException(status_code=404, detail="因子模型不存在")
    
    db.delete(db_factor_model)
    db.commit()


# ==================== 市场状态管理 ====================

@router.post("/regimes", response_model=MarketRegimeResponse, status_code=status.HTTP_201_CREATED)
def create_market_regime(
    regime: MarketRegimeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建市场状态"""
    db_regime = MarketRegime(**regime.model_dump())
    db.add(db_regime)
    db.commit()
    db.refresh(db_regime)
    return db_regime


@router.get("/regimes", response_model=List[MarketRegimeResponse])
def get_market_regimes(
    economic_cycle: Optional[str] = Query(None, description="经济周期"),
    market_sentiment: Optional[str] = Query(None, description="市场情绪"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取市场状态列表"""
    query = db.query(MarketRegime)
    
    if economic_cycle:
        query = query.filter(MarketRegime.economic_cycle == economic_cycle)
    if market_sentiment:
        query = query.filter(MarketRegime.market_sentiment == market_sentiment)
    
    regimes = query.offset(offset).limit(limit).all()
    return regimes


@router.get("/regimes/{regime_id}", response_model=MarketRegimeResponse)
def get_market_regime(
    regime_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个市场状态"""
    regime = db.query(MarketRegime).filter(MarketRegime.id == regime_id).first()
    if not regime:
        raise HTTPException(status_code=404, detail="市场状态不存在")
    return regime


@router.put("/regimes/{regime_id}", response_model=MarketRegimeResponse)
def update_market_regime(
    regime_id: int,
    regime_update: MarketRegimeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新市场状态"""
    db_regime = db.query(MarketRegime).filter(MarketRegime.id == regime_id).first()
    if not db_regime:
        raise HTTPException(status_code=404, detail="市场状态不存在")
    
    update_data = regime_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_regime, field, value)
    
    db.commit()
    db.refresh(db_regime)
    return db_regime


@router.delete("/regimes/{regime_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_market_regime(
    regime_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除市场状态"""
    db_regime = db.query(MarketRegime).filter(MarketRegime.id == regime_id).first()
    if not db_regime:
        raise HTTPException(status_code=404, detail="市场状态不存在")
    
    db.delete(db_regime)
    db.commit()


# ==================== 统计分析 ====================

@router.get("/statistics/overview")
def get_strategy_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取策略统计概览"""
    # 策略统计
    total_strategies = db.query(Strategy).count()
    active_strategies = db.query(Strategy).filter(Strategy.is_active == True).count()
    
    # 按类型统计
    strategy_type_counts = {}
    for strategy_type in StrategyType:
        count = db.query(Strategy).filter(Strategy.strategy_type == strategy_type).count()
        strategy_type_counts[str(strategy_type.value)] = count
    
    # 按资产类别统计
    asset_class_counts = {}
    for asset_class in AssetClass:
        count = db.query(Strategy).filter(Strategy.asset_class == asset_class).count()
        asset_class_counts[str(asset_class.value)] = count
    
    # 信号统计
    total_signals = db.query(StrategySignal).count()
    recent_signals = db.query(StrategySignal).filter(
        StrategySignal.signal_date >= datetime.now() - timedelta(days=7)
    ).count()
    
    # 回测统计
    total_backtests = db.query(BacktestResult).count()
    
    return {
        "strategies": {
            "total": total_strategies,
            "active": active_strategies,
            "by_type": strategy_type_counts,
            "by_asset_class": asset_class_counts
        },
        "signals": {
            "total": total_signals,
            "recent_7_days": recent_signals
        },
        "backtests": {
            "total": total_backtests
        }
    }


# ==================== 单个策略管理 ====================

@router.get("/{strategy_id}", response_model=StrategyResponse)
def get_strategy(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个策略"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    return strategy


@router.put("/{strategy_id}", response_model=StrategyResponse)
def update_strategy(
    strategy_id: int,
    strategy_update: StrategyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新策略"""
    db_strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    update_data = strategy_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_strategy, field, value)
    
    db.commit()
    db.refresh(db_strategy)
    return db_strategy


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_strategy(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除策略"""
    db_strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not db_strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    db.delete(db_strategy)
    db.commit()


@router.get("/{strategy_id}/with-signals", response_model=StrategyWithSignals)
def get_strategy_with_signals(
    strategy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取策略及其信号"""
    strategy = db.query(Strategy).filter(Strategy.id == strategy_id).first()
    if not strategy:
        raise HTTPException(status_code=404, detail="策略不存在")
    
    return strategy 