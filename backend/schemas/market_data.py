"""
市场数据Schema
定义API请求和响应的数据结构
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    """资产类型枚举"""
    STOCK = "STOCK"
    BOND = "BOND"
    FUND = "FUND"
    ETF = "ETF"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    FOREX = "FOREX"
    COMMODITY = "COMMODITY"


# MarketData Schemas
class MarketDataBase(BaseModel):
    """市场数据基础Schema"""
    symbol: str = Field(..., min_length=1, max_length=20, description="证券代码")
    name: str = Field(..., min_length=1, max_length=100, description="证券名称")
    asset_type: AssetType = Field(..., description="资产类型")
    exchange: str = Field(..., min_length=1, max_length=20, description="交易所")
    currency: str = Field(default="CNY", min_length=3, max_length=3, description="货币")
    is_active: bool = Field(default=True, description="是否活跃")
    industry: Optional[str] = Field(None, max_length=50, description="行业")
    sector: Optional[str] = Field(None, max_length=50, description="板块")
    market_cap: Optional[float] = Field(None, description="市值")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    dividend_yield: Optional[float] = Field(None, description="股息率")


class MarketDataCreate(MarketDataBase):
    """创建市场数据Schema"""
    pass


class MarketDataUpdate(BaseModel):
    """更新市场数据Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="证券名称")
    asset_type: Optional[AssetType] = Field(None, description="资产类型")
    exchange: Optional[str] = Field(None, min_length=1, max_length=20, description="交易所")
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="货币")
    is_active: Optional[bool] = Field(None, description="是否活跃")
    industry: Optional[str] = Field(None, max_length=50, description="行业")
    sector: Optional[str] = Field(None, max_length=50, description="板块")
    market_cap: Optional[float] = Field(None, description="市值")
    pe_ratio: Optional[float] = Field(None, description="市盈率")
    pb_ratio: Optional[float] = Field(None, description="市净率")
    dividend_yield: Optional[float] = Field(None, description="股息率")


class MarketDataResponse(MarketDataBase):
    """市场数据响应Schema"""
    id: int = Field(..., description="ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


# PriceHistory Schemas
class PriceHistoryBase(BaseModel):
    """价格历史基础Schema"""
    date: datetime = Field(..., description="交易日期")
    open_price: Optional[float] = Field(None, description="开盘价")
    high_price: Optional[float] = Field(None, description="最高价")
    low_price: Optional[float] = Field(None, description="最低价")
    close_price: Optional[float] = Field(None, description="收盘价")
    adjusted_close: Optional[float] = Field(None, description="复权收盘价")
    volume: Optional[float] = Field(None, description="成交量")
    turnover: Optional[float] = Field(None, description="成交额")
    ma5: Optional[float] = Field(None, description="5日均线")
    ma10: Optional[float] = Field(None, description="10日均线")
    ma20: Optional[float] = Field(None, description="20日均线")
    ma60: Optional[float] = Field(None, description="60日均线")


class PriceHistoryCreate(PriceHistoryBase):
    """创建价格历史Schema"""
    pass


class PriceHistoryUpdate(BaseModel):
    """更新价格历史Schema"""
    open_price: Optional[float] = Field(None, description="开盘价")
    high_price: Optional[float] = Field(None, description="最高价")
    low_price: Optional[float] = Field(None, description="最低价")
    close_price: Optional[float] = Field(None, description="收盘价")
    adjusted_close: Optional[float] = Field(None, description="复权收盘价")
    volume: Optional[float] = Field(None, description="成交量")
    turnover: Optional[float] = Field(None, description="成交额")
    ma5: Optional[float] = Field(None, description="5日均线")
    ma10: Optional[float] = Field(None, description="10日均线")
    ma20: Optional[float] = Field(None, description="20日均线")
    ma60: Optional[float] = Field(None, description="60日均线")


class PriceHistoryResponse(PriceHistoryBase):
    """价格历史响应Schema"""
    id: int = Field(..., description="ID")
    market_data_id: int = Field(..., description="市场数据ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# MarketIndex Schemas
class MarketIndexBase(BaseModel):
    """市场指数基础Schema"""
    code: str = Field(..., min_length=1, max_length=20, description="指数代码")
    name: str = Field(..., min_length=1, max_length=100, description="指数名称")
    description: Optional[str] = Field(None, description="指数描述")
    base_date: Optional[datetime] = Field(None, description="基期")
    base_value: Optional[float] = Field(None, description="基期值")
    is_active: bool = Field(default=True, description="是否活跃")


class MarketIndexCreate(MarketIndexBase):
    """创建市场指数Schema"""
    pass


class MarketIndexUpdate(BaseModel):
    """更新市场指数Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="指数名称")
    description: Optional[str] = Field(None, description="指数描述")
    base_date: Optional[datetime] = Field(None, description="基期")
    base_value: Optional[float] = Field(None, description="基期值")
    is_active: Optional[bool] = Field(None, description="是否活跃")


class MarketIndexResponse(MarketIndexBase):
    """市场指数响应Schema"""
    id: int = Field(..., description="ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


# IndexHistory Schemas
class IndexHistoryBase(BaseModel):
    """指数历史基础Schema"""
    date: datetime = Field(..., description="交易日期")
    open_value: Optional[float] = Field(None, description="开盘指数")
    high_value: Optional[float] = Field(None, description="最高指数")
    low_value: Optional[float] = Field(None, description="最低指数")
    close_value: Optional[float] = Field(None, description="收盘指数")
    volume: Optional[float] = Field(None, description="成交量")
    turnover: Optional[float] = Field(None, description="成交额")


class IndexHistoryCreate(IndexHistoryBase):
    """创建指数历史Schema"""
    market_index_id: int = Field(..., description="市场指数ID")


class IndexHistoryUpdate(BaseModel):
    """更新指数历史Schema"""
    open_value: Optional[float] = Field(None, description="开盘指数")
    high_value: Optional[float] = Field(None, description="最高指数")
    low_value: Optional[float] = Field(None, description="最低指数")
    close_value: Optional[float] = Field(None, description="收盘指数")
    volume: Optional[float] = Field(None, description="成交量")
    turnover: Optional[float] = Field(None, description="成交额")


class IndexHistoryResponse(IndexHistoryBase):
    """指数历史响应Schema"""
    id: int = Field(..., description="ID")
    market_index_id: int = Field(..., description="市场指数ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True


# 复合响应Schema
class MarketDataWithPriceHistory(MarketDataResponse):
    """包含价格历史的市场数据响应"""
    price_history: List[PriceHistoryResponse] = Field(default=[], description="价格历史")


class MarketIndexWithHistory(MarketIndexResponse):
    """包含历史数据的市场指数响应"""
    index_history: List[IndexHistoryResponse] = Field(default=[], description="指数历史")


# 查询参数Schema
class MarketDataQuery(BaseModel):
    """市场数据查询参数"""
    asset_type: Optional[AssetType] = Field(None, description="资产类型")
    exchange: Optional[str] = Field(None, description="交易所")
    industry: Optional[str] = Field(None, description="行业")
    sector: Optional[str] = Field(None, description="板块")
    is_active: Optional[bool] = Field(None, description="是否活跃")
    limit: int = Field(default=100, ge=1, le=1000, description="限制数量")
    offset: int = Field(default=0, ge=0, description="偏移量")


class PriceHistoryQuery(BaseModel):
    """价格历史查询参数"""
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    limit: int = Field(default=100, ge=1, le=1000, description="限制数量")
    offset: int = Field(default=0, ge=0, description="偏移量") 