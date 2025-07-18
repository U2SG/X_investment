"""
投资组合相关API路由
实现投资组合的创建和查询（仅限当前登录用户）
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
import sys
import os
import logging
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from database import get_db
from models import Portfolio, PortfolioAsset, Asset
from schemas.portfolio import PortfolioCreate, PortfolioResponse, PortfolioUpdate, PortfolioAssetCreate
from utils.auth import get_current_active_user
from models import User

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加父目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

router = APIRouter(
    prefix="/portfolios",
    tags=["portfolios"],
    responses={404: {"description": "未找到投资组合"}},
)

@router.post("/", response_model=PortfolioResponse, status_code=status.HTTP_201_CREATED)
def create_portfolio(
    portfolio_in: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新的投资组合（当前登录用户），支持同时添加资产及权重。
    - 参数: portfolio_in (PortfolioCreate): 投资组合创建请求体
    - 返回: PortfolioResponse 新建投资组合详情
    - 异常: 资产ID不存在时返回400
    """
    # 创建投资组合对象
    portfolio = Portfolio(
        name=portfolio_in.name,
        description=portfolio_in.description,
        risk_level=portfolio_in.risk_level,
        user_id=current_user.id
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)

    # 添加资产及权重
    for asset_item in portfolio_in.assets:
        # 检查资产是否存在
        asset = db.query(Asset).filter(Asset.id == asset_item.asset_id).first()
        if not asset:
            raise HTTPException(status_code=400, detail=f"资产ID {asset_item.asset_id} 不存在")
        portfolio_asset = PortfolioAsset(
            portfolio_id=portfolio.id,
            asset_id=asset.id,
            weight=asset_item.weight
        )
        db.add(portfolio_asset)
    db.commit()
    db.refresh(portfolio)
    return portfolio

@router.get("/me", response_model=List[PortfolioResponse])
def get_my_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的所有投资组合。
    - 返回: List[PortfolioResponse] 当前用户的投资组合列表
    """
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
    return portfolios

@router.get("/{portfolio_id}", response_model=PortfolioResponse)
def get_portfolio_detail(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取指定投资组合详情（仅限当前用户）
    """
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在或无权限访问")
    return portfolio

@router.put("/{portfolio_id}", response_model=PortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    portfolio_in: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新指定投资组合基础信息（仅限当前用户）
    """
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在或无权限访问")
    # 只更新基础字段
    if portfolio_in.name is not None:
        portfolio.name = portfolio_in.name
    if portfolio_in.description is not None:
        portfolio.description = portfolio_in.description
    if portfolio_in.risk_level is not None:
        portfolio.risk_level = portfolio_in.risk_level
    if portfolio_in.is_active is not None:
        portfolio.is_active = portfolio_in.is_active
    db.commit()
    db.refresh(portfolio)
    return portfolio

@router.put("/{portfolio_id}/assets", response_model=PortfolioResponse)
def update_portfolio_assets(
    portfolio_id: int,
    assets: list[PortfolioAssetCreate] = Body(..., description="资产及权重列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新指定投资组合的资产及权重（仅限当前用户）
    """
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在或无权限访问")
    # 删除原有资产关联
    db.query(PortfolioAsset).filter(PortfolioAsset.portfolio_id == portfolio_id).delete()
    # 添加新资产关联
    for asset_item in assets:
        asset = db.query(Asset).filter(Asset.id == asset_item.asset_id).first()
        if not asset:
            raise HTTPException(status_code=400, detail=f"资产ID {asset_item.asset_id} 不存在")
        portfolio_asset = PortfolioAsset(
            portfolio_id=portfolio_id,
            asset_id=asset.id,
            weight=asset_item.weight
        )
        db.add(portfolio_asset)
    db.commit()
    db.refresh(portfolio)
    return portfolio

@router.delete("/{portfolio_id}", status_code=200)
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除指定投资组合（仅限当前用户）
    """
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在或无权限访问")
    db.delete(portfolio)
    db.commit()
    return {"detail": "删除成功"} 