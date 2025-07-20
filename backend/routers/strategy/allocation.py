"""
投资组合配置管理模块
提供投资组合配置的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    Strategy, PortfolioAllocation
)
from schemas.strategy import (
    PortfolioAllocationCreate, PortfolioAllocationUpdate, PortfolioAllocationResponse
)

router = APIRouter(prefix="", tags=["投资组合配置管理"])


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