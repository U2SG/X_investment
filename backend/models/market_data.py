"""
市场数据模型
定义金融工具的基础数据结构，包括股票、债券、基金等
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class AssetType(enum.Enum):
    """资产类型枚举"""
    STOCK = "STOCK"  # 股票
    BOND = "BOND"    # 债券
    FUND = "FUND"    # 基金
    ETF = "ETF"      # ETF
    FUTURES = "FUTURES"  # 期货
    OPTIONS = "OPTIONS"  # 期权
    FOREX = "FOREX"  # 外汇
    COMMODITY = "COMMODITY"  # 商品


class MarketData(Base):
    """市场数据基础模型"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True, nullable=False, comment="证券代码")
    name = Column(String(100), nullable=False, comment="证券名称")
    asset_type = Column(Enum(AssetType), nullable=False, comment="资产类型")
    exchange = Column(String(20), nullable=False, comment="交易所")
    currency = Column(String(3), default="CNY", comment="货币")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    
    # 基础信息
    industry = Column(String(50), comment="行业")
    sector = Column(String(50), comment="板块")
    market_cap = Column(Float, comment="市值")
    pe_ratio = Column(Float, comment="市盈率")
    pb_ratio = Column(Float, comment="市净率")
    dividend_yield = Column(Float, comment="股息率")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    price_history = relationship("PriceHistory", back_populates="market_data", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MarketData(symbol='{self.symbol}', name='{self.name}', type='{self.asset_type.value}')>"


class PriceHistory(Base):
    """价格历史数据模型"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    market_data_id = Column(Integer, ForeignKey("market_data.id"), nullable=False)
    date = Column(DateTime, nullable=False, comment="交易日期")
    
    # 价格数据
    open_price = Column(Float, comment="开盘价")
    high_price = Column(Float, comment="最高价")
    low_price = Column(Float, comment="最低价")
    close_price = Column(Float, comment="收盘价")
    adjusted_close = Column(Float, comment="复权收盘价")
    
    # 交易数据
    volume = Column(Float, comment="成交量")
    turnover = Column(Float, comment="成交额")
    
    # 技术指标
    ma5 = Column(Float, comment="5日均线")
    ma10 = Column(Float, comment="10日均线")
    ma20 = Column(Float, comment="20日均线")
    ma60 = Column(Float, comment="60日均线")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    market_data = relationship("MarketData", back_populates="price_history")
    
    def __repr__(self):
        return f"<PriceHistory(symbol='{self.market_data.symbol}', date='{self.date}', close='{self.close_price}')>"


class MarketIndex(Base):
    """市场指数模型"""
    __tablename__ = "market_index"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False, comment="指数代码")
    name = Column(String(100), nullable=False, comment="指数名称")
    description = Column(Text, comment="指数描述")
    base_date = Column(DateTime, comment="基期")
    base_value = Column(Float, comment="基期值")
    is_active = Column(Boolean, default=True, comment="是否活跃")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), comment="更新时间")
    
    # 关系
    index_history = relationship("IndexHistory", back_populates="market_index", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MarketIndex(code='{self.code}', name='{self.name}')>"


class IndexHistory(Base):
    """指数历史数据模型"""
    __tablename__ = "index_history"
    
    id = Column(Integer, primary_key=True, index=True)
    market_index_id = Column(Integer, ForeignKey("market_index.id"), nullable=False)
    date = Column(DateTime, nullable=False, comment="交易日期")
    
    # 指数数据
    open_value = Column(Float, comment="开盘指数")
    high_value = Column(Float, comment="最高指数")
    low_value = Column(Float, comment="最低指数")
    close_value = Column(Float, comment="收盘指数")
    
    # 交易数据
    volume = Column(Float, comment="成交量")
    turnover = Column(Float, comment="成交额")
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    # 关系
    market_index = relationship("MarketIndex", back_populates="index_history")
    
    def __repr__(self):
        return f"<IndexHistory(code='{self.market_index.code}', date='{self.date}', close='{self.close_value}')>" 