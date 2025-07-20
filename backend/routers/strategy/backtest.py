"""
回测管理模块
提供回测结果的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    Strategy, BacktestResult
)
from schemas.strategy import (
    BacktestResultCreate, BacktestResultUpdate, BacktestResultResponse
)

router = APIRouter(prefix="", tags=["回测管理"])


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