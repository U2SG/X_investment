"""
市场状态管理模块
提供市场状态的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    MarketRegime
)
from schemas.strategy import (
    MarketRegimeCreate, MarketRegimeUpdate, MarketRegimeResponse
)

router = APIRouter(prefix="", tags=["市场状态管理"])


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