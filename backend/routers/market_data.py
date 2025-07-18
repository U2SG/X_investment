"""
市场数据路由
提供市场数据的CRUD操作API
"""
import sys
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from database import get_db
from models.market_data import MarketData, PriceHistory, MarketIndex, IndexHistory, AssetType
from schemas.market_data import (
    MarketDataCreate, MarketDataUpdate, MarketDataResponse,
    PriceHistoryCreate, PriceHistoryUpdate, PriceHistoryResponse,
    MarketIndexCreate, MarketIndexUpdate, MarketIndexResponse,
    IndexHistoryCreate, IndexHistoryUpdate, IndexHistoryResponse,
    MarketDataWithPriceHistory, MarketIndexWithHistory,
    MarketDataQuery, PriceHistoryQuery
)
from utils.auth import get_current_user
from models.user import User

# 创建路由器
router = APIRouter(
    prefix="/market-data",
    tags=["market-data"],
    responses={404: {"description": "Not found"}},
)


# 统计信息路由 - 必须在参数化路由之前
@router.get("/statistics/overview")
def get_market_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取市场数据统计概览
    
    **功能说明:**
    - 提供市场数据的统计信息
    - 包括各类型资产数量、活跃状态等
    
    **权限要求:**
    - 需要用户登录认证
    
    **返回数据:**
    - 市场数据统计信息
    
    **错误处理:**
    - 401: 未授权访问
    """
    # 统计各类型资产数量
    asset_type_stats = {}
    for asset_type in AssetType:
        count = db.query(MarketData).filter(MarketData.asset_type == asset_type).count()
        asset_type_stats[asset_type.value] = count
    
    # 统计活跃状态
    active_count = db.query(MarketData).filter(MarketData.is_active == True).count()
    inactive_count = db.query(MarketData).filter(MarketData.is_active == False).count()
    
    # 统计指数数量
    index_count = db.query(MarketIndex).count()
    active_index_count = db.query(MarketIndex).filter(MarketIndex.is_active == True).count()
    
    return {
        "asset_type_statistics": asset_type_stats,
        "active_assets": active_count,
        "inactive_assets": inactive_count,
        "total_assets": active_count + inactive_count,
        "total_indices": index_count,
        "active_indices": active_index_count
    }


# MarketIndex 路由 - 必须在参数化路由之前
@router.post("/indices", response_model=MarketIndexResponse, status_code=status.HTTP_201_CREATED)
def create_market_index(
    market_index: MarketIndexCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建市场指数
    
    **功能说明:**
    - 创建新的市场指数记录
    - 包含指数基础信息和基期数据
    
    **权限要求:**
    - 需要用户登录认证
    
    **请求体:**
    - 市场指数数据
    
    **返回数据:**
    - 创建成功的市场指数记录
    
    **错误处理:**
    - 400: 指数代码已存在
    - 401: 未授权访问
    - 422: 参数验证失败
    """
    # 检查指数代码是否已存在
    existing_index = db.query(MarketIndex).filter(MarketIndex.code == market_index.code).first()
    if existing_index:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"指数代码 {market_index.code} 已存在"
        )
    
    # 创建市场指数记录
    db_market_index = MarketIndex(**market_index.model_dump())
    db.add(db_market_index)
    db.commit()
    db.refresh(db_market_index)
    
    return db_market_index


@router.get("/indices", response_model=List[MarketIndexResponse])
def get_market_indices(
    is_active: Optional[str] = Query(None, description="是否活跃 (true/false)"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取市场指数列表
    
    **功能说明:**
    - 分页查询市场指数记录
    - 支持活跃状态筛选
    - 按创建时间倒序排列
    
    **权限要求:**
    - 需要用户登录认证
    
    **查询参数:**
    - is_active: 按活跃状态筛选
    - limit: 返回记录数量限制
    - offset: 分页偏移量
    
    **返回数据:**
    - 市场指数记录列表
    
    **错误处理:**
    - 401: 未授权访问
    - 422: 参数验证失败
    """
    query = db.query(MarketIndex)
    
    # 应用筛选条件
    if is_active is not None:
        is_active_bool = is_active.lower() == "true"
        query = query.filter(MarketIndex.is_active == is_active_bool)
    
    # 分页和排序
    market_indices = query.order_by(MarketIndex.created_at.desc()).offset(offset).limit(limit).all()
    
    return market_indices


@router.get("/indices/{index_id}", response_model=MarketIndexResponse)
def get_market_index(
    index_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个市场指数
    
    **功能说明:**
    - 根据ID获取特定的市场指数记录
    - 包含完整的指数信息
    
    **权限要求:**
    - 需要用户登录认证
    
    **路径参数:**
    - index_id: 市场指数ID
    
    **返回数据:**
    - 市场指数记录详情
    
    **错误处理:**
    - 401: 未授权访问
    - 404: 市场指数不存在
    """
    market_index = db.query(MarketIndex).filter(MarketIndex.id == index_id).first()
    if not market_index:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"市场指数ID {index_id} 不存在"
        )
    
    return market_index


# MarketData 路由
@router.post("/", response_model=MarketDataResponse, status_code=status.HTTP_201_CREATED)
def create_market_data(
    market_data: MarketDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建市场数据
    
    **功能说明:**
    - 创建新的金融工具市场数据记录
    - 支持股票、债券、基金、ETF等多种资产类型
    - 包含基础信息和估值指标
    
    **权限要求:**
    - 需要用户登录认证
    
    **参数说明:**
    - symbol: 证券代码，必须唯一
    - name: 证券名称
    - asset_type: 资产类型（stock/bond/fund/etf等）
    - exchange: 交易所
    - currency: 货币（默认CNY）
    - industry: 行业分类
    - sector: 板块分类
    - market_cap: 市值
    - pe_ratio: 市盈率
    - pb_ratio: 市净率
    - dividend_yield: 股息率
    
    **返回数据:**
    - 创建成功的市场数据记录
    
    **错误处理:**
    - 400: 证券代码已存在
    - 401: 未授权访问
    - 422: 参数验证失败
    """
    # 检查证券代码是否已存在
    existing_data = db.query(MarketData).filter(MarketData.symbol == market_data.symbol).first()
    if existing_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"证券代码 {market_data.symbol} 已存在"
        )
    
    # 创建市场数据记录
    db_market_data = MarketData(**market_data.model_dump())
    db.add(db_market_data)
    db.commit()
    db.refresh(db_market_data)
    
    return db_market_data


@router.get("/", response_model=List[MarketDataResponse])
def get_market_data_list(
    asset_type: Optional[str] = Query(None, description="资产类型 (STOCK, BOND, FUND, ETF, FUTURES, OPTIONS, FOREX, COMMODITY)"),
    exchange: Optional[str] = Query(None, description="交易所"),
    industry: Optional[str] = Query(None, description="行业"),
    sector: Optional[str] = Query(None, description="板块"),
    is_active: Optional[bool] = Query(None, description="是否活跃"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取市场数据列表
    
    **功能说明:**
    - 分页查询市场数据记录
    - 支持多种筛选条件
    - 按创建时间倒序排列
    
    **权限要求:**
    - 需要用户登录认证
    
    **查询参数:**
    - asset_type: 按资产类型筛选
    - exchange: 按交易所筛选
    - industry: 按行业筛选
    - sector: 按板块筛选
    - is_active: 按活跃状态筛选
    - limit: 返回记录数量限制
    - offset: 分页偏移量
    
    **返回数据:**
    - 市场数据记录列表
    
    **错误处理:**
    - 401: 未授权访问
    - 422: 参数验证失败
    """
    query = db.query(MarketData)
    
    # 应用筛选条件
    if asset_type:
        try:
            asset_type_enum = AssetType(asset_type)
            query = query.filter(MarketData.asset_type == asset_type_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"无效的资产类型: {asset_type}"
            )
    if exchange:
        query = query.filter(MarketData.exchange == exchange)
    if industry:
        query = query.filter(MarketData.industry == industry)
    if sector:
        query = query.filter(MarketData.sector == sector)
    if is_active is not None:
        query = query.filter(MarketData.is_active == is_active)
    
    # 分页和排序
    market_data_list = query.order_by(MarketData.created_at.desc()).offset(offset).limit(limit).all()
    
    return market_data_list


@router.get("/{market_data_id}", response_model=MarketDataResponse)
def get_market_data(
    market_data_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取单个市场数据
    
    **功能说明:**
    - 根据ID获取特定的市场数据记录
    - 包含完整的市场数据信息
    
    **权限要求:**
    - 需要用户登录认证
    
    **路径参数:**
    - market_data_id: 市场数据ID
    
    **返回数据:**
    - 市场数据记录详情
    
    **错误处理:**
    - 401: 未授权访问
    - 404: 市场数据不存在
    """
    market_data = db.query(MarketData).filter(MarketData.id == market_data_id).first()
    if not market_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"市场数据ID {market_data_id} 不存在"
        )
    
    return market_data


@router.put("/{market_data_id}", response_model=MarketDataResponse)
def update_market_data(
    market_data_id: int,
    market_data_update: MarketDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新市场数据
    
    **功能说明:**
    - 更新指定的市场数据记录
    - 只更新提供的字段
    
    **权限要求:**
    - 需要用户登录认证
    
    **路径参数:**
    - market_data_id: 市场数据ID
    
    **请求体:**
    - 要更新的字段（可选）
    
    **返回数据:**
    - 更新后的市场数据记录
    
    **错误处理:**
    - 401: 未授权访问
    - 404: 市场数据不存在
    - 422: 参数验证失败
    """
    db_market_data = db.query(MarketData).filter(MarketData.id == market_data_id).first()
    if not db_market_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"市场数据ID {market_data_id} 不存在"
        )
    
    # 更新字段
    update_data = market_data_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_market_data, field, value)
    
    db.commit()
    db.refresh(db_market_data)
    
    return db_market_data


@router.delete("/{market_data_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_market_data(
    market_data_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除市场数据
    
    **功能说明:**
    - 删除指定的市场数据记录
    - 同时删除相关的价格历史数据
    
    **权限要求:**
    - 需要用户登录认证
    
    **路径参数:**
    - market_data_id: 市场数据ID
    
    **返回数据:**
    - 无返回内容（204状态码）
    
    **错误处理:**
    - 401: 未授权访问
    - 404: 市场数据不存在
    """
    db_market_data = db.query(MarketData).filter(MarketData.id == market_data_id).first()
    if not db_market_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"市场数据ID {market_data_id} 不存在"
        )
    
    db.delete(db_market_data)
    db.commit()
    
    return None


# PriceHistory 路由
@router.post("/{market_data_id}/price-history", response_model=PriceHistoryResponse, status_code=status.HTTP_201_CREATED)
def create_price_history(
    market_data_id: int,
    price_history: PriceHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建价格历史数据
    
    **功能说明:**
    - 为指定的市场数据添加价格历史记录
    - 包含OHLC价格、成交量、技术指标等
    
    **权限要求:**
    - 需要用户登录认证
    
    **路径参数:**
    - market_data_id: 市场数据ID
    
    **请求体:**
    - 价格历史数据
    
    **返回数据:**
    - 创建成功的价格历史记录
    
    **错误处理:**
    - 400: 市场数据不存在
    - 401: 未授权访问
    - 422: 参数验证失败
    """
    # 检查市场数据是否存在
    market_data = db.query(MarketData).filter(MarketData.id == market_data_id).first()
    if not market_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"市场数据ID {market_data_id} 不存在"
        )
    
    # 创建价格历史记录
    price_history_data = price_history.model_dump()
    price_history_data["market_data_id"] = market_data_id
    
    db_price_history = PriceHistory(**price_history_data)
    db.add(db_price_history)
    db.commit()
    db.refresh(db_price_history)
    
    return db_price_history


@router.get("/{market_data_id}/price-history", response_model=List[PriceHistoryResponse])
def get_price_history(
    market_data_id: int,
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取价格历史数据
    
    **功能说明:**
    - 获取指定市场数据的价格历史记录
    - 支持日期范围筛选
    - 按日期倒序排列
    
    **权限要求:**
    - 需要用户登录认证
    
    **路径参数:**
    - market_data_id: 市场数据ID
    
    **查询参数:**
    - start_date: 开始日期
    - end_date: 结束日期
    - limit: 返回记录数量限制
    - offset: 分页偏移量
    
    **返回数据:**
    - 价格历史记录列表
    
    **错误处理:**
    - 401: 未授权访问
    - 404: 市场数据不存在
    - 422: 参数验证失败
    """
    # 检查市场数据是否存在
    market_data = db.query(MarketData).filter(MarketData.id == market_data_id).first()
    if not market_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"市场数据ID {market_data_id} 不存在"
        )
    
    query = db.query(PriceHistory).filter(PriceHistory.market_data_id == market_data_id)
    
    # 应用日期筛选
    if start_date:
        query = query.filter(PriceHistory.date >= start_date)
    if end_date:
        query = query.filter(PriceHistory.date <= end_date)
    
    # 分页和排序
    price_history_list = query.order_by(PriceHistory.date.desc()).offset(offset).limit(limit).all()
    
    return price_history_list 