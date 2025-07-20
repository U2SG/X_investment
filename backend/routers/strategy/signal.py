"""
策略信号管理模块
提供策略信号的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    Strategy, StrategySignal, SignalType
)
from models.market_data import MarketData
from schemas.strategy import (
    StrategySignalCreate, StrategySignalUpdate, StrategySignalResponse
)

router = APIRouter(prefix="", tags=["策略信号管理"])


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