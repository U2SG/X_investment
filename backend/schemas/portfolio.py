"""
投资组合相关的Pydantic模型
用于API请求和响应的数据验证
"""
from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from pydantic import BaseModel, Field, validator


class AssetBase(BaseModel):
    """
    资产基础模型。
    用于资产相关请求和响应的通用字段。
    """
    code: str = Field(..., description="资产代码")
    name: str = Field(..., description="资产名称")
    asset_type: str = Field(..., description="资产类型：股票、债券、基金等")
    description: Optional[str] = Field(None, description="资产描述")


class AssetCreate(AssetBase):
    """
    创建资产的请求模型。
    继承自AssetBase，无新增字段。
    """
    pass


class AssetResponse(AssetBase):
    """
    资产响应模型。
    用于资产相关API的响应，包含资产ID和时间戳。
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class PortfolioAssetBase(BaseModel):
    """
    投资组合资产关联基础模型。
    用于描述投资组合中的资产及其权重。
    """
    asset_id: int = Field(..., description="资产ID")
    weight: float = Field(..., description="权重百分比")

    @validator('weight')
    def check_weight(cls, v):
        """验证权重是否在有效范围内（0-100）"""
        if v < 0 or v > 100:
            raise ValueError('权重必须在0到100之间')
        return v


class PortfolioAssetCreate(PortfolioAssetBase):
    """
    创建投资组合资产关联的请求模型。
    继承自PortfolioAssetBase，无新增字段。
    """
    pass


class PortfolioAssetResponse(PortfolioAssetBase):
    """
    投资组合资产关联响应模型。
    包含关联ID、投资组合ID、资产详情、时间戳。
    """
    id: int
    portfolio_id: int
    created_at: datetime
    updated_at: datetime
    asset: AssetResponse

    class Config:
        orm_mode = True


class PortfolioBase(BaseModel):
    """
    投资组合基础模型。
    用于投资组合相关请求和响应的通用字段。
    """
    name: str = Field(..., description="投资组合名称")
    description: Optional[str] = Field(None, description="投资组合描述")
    risk_level: int = Field(..., description="风险等级，1-5")

    @validator('risk_level')
    def check_risk_level(cls, v):
        """验证风险等级是否在有效范围内（1-5）"""
        if v < 1 or v > 5:
            raise ValueError('风险等级必须在1到5之间')
        return v


class PortfolioCreate(PortfolioBase):
    """
    创建投资组合的请求模型。
    包含资产列表。
    """
    assets: List[PortfolioAssetCreate] = Field([], description="投资组合中的资产列表")


class PortfolioUpdate(BaseModel):
    """
    更新投资组合的请求模型。
    支持部分字段可选更新。
    """
    name: Optional[str] = Field(None, description="投资组合名称")
    description: Optional[str] = Field(None, description="投资组合描述")
    risk_level: Optional[int] = Field(None, description="风险等级，1-5")
    is_active: Optional[bool] = Field(None, description="是否激活")

    @validator('risk_level')
    def check_risk_level(cls, v):
        """验证风险等级是否在有效范围内（1-5）"""
        if v is not None and (v < 1 or v > 5):
            raise ValueError('风险等级必须在1到5之间')
        return v


class PortfolioResponse(PortfolioBase):
    """
    投资组合响应模型。
    包含投资组合ID、用户ID、资产关联、时间戳等。
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    portfolio_assets: List[PortfolioAssetResponse] = []

    class Config:
        orm_mode = True 