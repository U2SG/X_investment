"""
策略基础管理模块
提供策略的增删改查和统计功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    Strategy, StrategyType, AssetClass
)
from schemas.strategy import (
    StrategyCreate, StrategyUpdate, StrategyResponse, StrategyWithSignals,
    StrategyQuery
)

router = APIRouter(prefix="", tags=["策略基础管理"])


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
    
    return {
        "strategies": {
            "total": total_strategies,
            "active": active_strategies,
            "by_type": strategy_type_counts,
            "by_asset_class": asset_class_counts
        }
    } 