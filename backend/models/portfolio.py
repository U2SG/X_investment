"""
投资组合相关模型
包含Portfolio（投资组合）、Asset（资产）和PortfolioAsset（投资组合资产关联）
"""
from __future__ import annotations
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from typing import TYPE_CHECKING

from . import Base
from .asset_tag import Tag, AssetTag

# 文件底部添加类型注解用的User导入，避免循环依赖
if TYPE_CHECKING:
    from .user import User

class Portfolio(Base):
    """
    投资组合模型。
    表示一个用户的投资组合，包含名称、描述、风险等级、所属用户、资产关联等。
    """
    __tablename__ = "portfolios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)  # 投资组合ID
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # 投资组合名称
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # 描述
    risk_level: Mapped[int] = mapped_column(nullable=False)  # 1-5，风险等级
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)  # 所属用户ID
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # 是否激活

    # 关系
    user: Mapped["User"] = relationship("User", back_populates="portfolios")  # 所属用户
    portfolio_assets: Mapped[list["PortfolioAsset"]] = relationship("PortfolioAsset", back_populates="portfolio", cascade="all, delete-orphan")  # 资产关联

    def __repr__(self):
        """字符串表示：<Portfolio 名称>"""
        return f"<Portfolio {self.name}>"


class Asset(Base):
    """
    资产模型。
    表示可投资的金融资产，如股票、基金、债券等。
    """
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)  # 资产ID
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)  # 资产代码
    name: Mapped[str] = mapped_column(String(100), nullable=False)  # 资产名称
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 资产类型
    description: Mapped[str | None] = mapped_column(Text, nullable=True)  # 资产描述
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # 关系
    portfolio_assets: Mapped[list["PortfolioAsset"]] = relationship("PortfolioAsset", back_populates="asset")  # 投资组合关联
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="asset_tags",
        back_populates="assets"
    )  # 资产标签多对多关系

    def __repr__(self):
        """字符串表示：<Asset 代码: 名称>"""
        return f"<Asset {self.code}: {self.name}>"


class PortfolioAsset(Base):
    """
    投资组合资产关联模型。
    表示投资组合与资产的多对多关系及权重。
    """
    __tablename__ = "portfolio_assets"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)  # 关联ID
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"), nullable=False)  # 投资组合ID
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)  # 资产ID
    weight: Mapped[float] = mapped_column(nullable=False)  # 权重百分比
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)  # 创建时间
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间

    # 关系
    portfolio: Mapped["Portfolio"] = relationship("Portfolio", back_populates="portfolio_assets")  # 所属投资组合
    asset: Mapped["Asset"] = relationship("Asset", back_populates="portfolio_assets")  # 关联资产

    def __repr__(self):
        """字符串表示：<PortfolioAsset 投资组合ID-资产ID: 权重%>"""
        return f"<PortfolioAsset {self.portfolio_id}-{self.asset_id}: {self.weight}%>" 