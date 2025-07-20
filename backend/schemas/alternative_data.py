"""
另类数据Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class AlternativeDataType(str, Enum):
    """另类数据类型枚举"""
    SATELLITE = "卫星图像"
    SUPPLY_CHAIN = "供应链"
    RECRUITMENT = "招聘"
    SENTIMENT = "舆情"
    SOCIAL_MEDIA = "社交媒体"
    NEWS = "新闻"
    WEATHER = "天气"
    TRANSPORT = "交通"
    ENERGY = "能源"
    OTHER = "其他"

# 基础模型
class AlternativeDataBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="数据名称")
    data_type: str = Field(..., description="数据类型")
    source: str = Field(..., min_length=1, max_length=100, description="数据源")
    description: Optional[str] = Field(None, description="数据描述")
    data_date: datetime = Field(..., description="数据日期")
    is_active: bool = Field(default=True, description="是否活跃")
    data_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class AlternativeDataCreate(AlternativeDataBase):
    pass

class AlternativeDataUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="数据名称")
    data_type: Optional[str] = Field(None, description="数据类型")
    source: Optional[str] = Field(None, min_length=1, max_length=100, description="数据源")
    description: Optional[str] = Field(None, description="数据描述")
    data_date: Optional[datetime] = Field(None, description="数据日期")
    is_active: Optional[bool] = Field(None, description="是否活跃")
    is_processed: Optional[bool] = Field(None, description="是否已处理")
    data_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class AlternativeDataResponse(AlternativeDataBase):
    id: int
    is_processed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 卫星图像数据
class SatelliteDataBase(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="纬度")
    longitude: float = Field(..., ge=-180, le=180, description="经度")
    location_name: Optional[str] = Field(None, max_length=200, description="位置名称")
    image_url: Optional[str] = Field(None, max_length=500, description="图像URL")
    image_metadata: Optional[Dict[str, Any]] = Field(None, description="图像元数据")
    vehicle_count: Optional[int] = Field(None, ge=0, description="车辆数量")
    parking_density: Optional[float] = Field(None, ge=0, description="停车密度")
    building_activity: Optional[float] = Field(None, description="建筑活动指数")
    vegetation_index: Optional[float] = Field(None, ge=0, le=1, description="植被指数")

class SatelliteDataCreate(SatelliteDataBase):
    alternative_data_id: int

class SatelliteDataUpdate(BaseModel):
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="纬度")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="经度")
    location_name: Optional[str] = Field(None, max_length=200, description="位置名称")
    image_url: Optional[str] = Field(None, max_length=500, description="图像URL")
    image_metadata: Optional[Dict[str, Any]] = Field(None, description="图像元数据")
    vehicle_count: Optional[int] = Field(None, ge=0, description="车辆数量")
    parking_density: Optional[float] = Field(None, ge=0, description="停车密度")
    building_activity: Optional[float] = Field(None, description="建筑活动指数")
    vegetation_index: Optional[float] = Field(None, ge=0, le=1, description="植被指数")

class SatelliteDataResponse(SatelliteDataBase):
    id: int
    alternative_data_id: int

    class Config:
        from_attributes = True

# 供应链数据
class SupplyChainDataBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200, description="公司名称")
    industry: Optional[str] = Field(None, max_length=100, description="行业")
    supply_chain_level: Optional[str] = Field(None, max_length=50, description="供应链层级")
    inventory_level: Optional[float] = Field(None, description="库存水平")
    delivery_time: Optional[float] = Field(None, ge=0, description="交付时间")
    supplier_count: Optional[int] = Field(None, ge=0, description="供应商数量")
    order_volume: Optional[float] = Field(None, ge=0, description="订单量")

class SupplyChainDataCreate(SupplyChainDataBase):
    alternative_data_id: int

class SupplyChainDataUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=200, description="公司名称")
    industry: Optional[str] = Field(None, max_length=100, description="行业")
    supply_chain_level: Optional[str] = Field(None, max_length=50, description="供应链层级")
    inventory_level: Optional[float] = Field(None, description="库存水平")
    delivery_time: Optional[float] = Field(None, ge=0, description="交付时间")
    supplier_count: Optional[int] = Field(None, ge=0, description="供应商数量")
    order_volume: Optional[float] = Field(None, ge=0, description="订单量")

class SupplyChainDataResponse(SupplyChainDataBase):
    id: int
    alternative_data_id: int

    class Config:
        from_attributes = True

# 招聘数据
class RecruitmentDataBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=200, description="公司名称")
    job_title: Optional[str] = Field(None, max_length=200, description="职位名称")
    location: Optional[str] = Field(None, max_length=200, description="工作地点")
    industry: Optional[str] = Field(None, max_length=100, description="行业")
    job_count: Optional[int] = Field(None, ge=0, description="职位数量")
    salary_range: Optional[str] = Field(None, max_length=100, description="薪资范围")
    experience_level: Optional[str] = Field(None, max_length=50, description="经验要求")
    skill_requirements: Optional[List[str]] = Field(None, description="技能要求")

class RecruitmentDataCreate(RecruitmentDataBase):
    alternative_data_id: int

class RecruitmentDataUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=200, description="公司名称")
    job_title: Optional[str] = Field(None, max_length=200, description="职位名称")
    location: Optional[str] = Field(None, max_length=200, description="工作地点")
    industry: Optional[str] = Field(None, max_length=100, description="行业")
    job_count: Optional[int] = Field(None, ge=0, description="职位数量")
    salary_range: Optional[str] = Field(None, max_length=100, description="薪资范围")
    experience_level: Optional[str] = Field(None, max_length=50, description="经验要求")
    skill_requirements: Optional[List[str]] = Field(None, description="技能要求")

class RecruitmentDataResponse(RecruitmentDataBase):
    id: int
    alternative_data_id: int

    class Config:
        from_attributes = True

# 舆情数据
class SentimentDataBase(BaseModel):
    source_type: str = Field(..., max_length=50, description="来源类型")
    content_type: Optional[str] = Field(None, max_length=50, description="内容类型")
    language: str = Field(default="zh", max_length=20, description="语言")
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="情感得分")
    sentiment_label: Optional[str] = Field(None, max_length=20, description="情感标签")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="置信度")
    keywords: Optional[List[str]] = Field(None, description="关键词")
    entities: Optional[List[Dict[str, Any]]] = Field(None, description="实体")
    topics: Optional[List[str]] = Field(None, description="主题")

class SentimentDataCreate(SentimentDataBase):
    alternative_data_id: int

class SentimentDataUpdate(BaseModel):
    source_type: Optional[str] = Field(None, max_length=50, description="来源类型")
    content_type: Optional[str] = Field(None, max_length=50, description="内容类型")
    language: Optional[str] = Field(None, max_length=20, description="语言")
    sentiment_score: Optional[float] = Field(None, ge=-1, le=1, description="情感得分")
    sentiment_label: Optional[str] = Field(None, max_length=20, description="情感标签")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="置信度")
    keywords: Optional[List[str]] = Field(None, description="关键词")
    entities: Optional[List[Dict[str, Any]]] = Field(None, description="实体")
    topics: Optional[List[str]] = Field(None, description="主题")

class SentimentDataResponse(SentimentDataBase):
    id: int
    alternative_data_id: int

    class Config:
        from_attributes = True

# 知识图谱
class KnowledgeGraphBase(BaseModel):
    entity_type: str = Field(..., max_length=50, description="实体类型")
    entity_name: str = Field(..., min_length=1, max_length=200, description="实体名称")
    entity_id: Optional[str] = Field(None, max_length=100, description="实体ID")
    relation_type: Optional[str] = Field(None, max_length=50, description="关系类型")
    target_entity_type: Optional[str] = Field(None, max_length=50, description="目标实体类型")
    target_entity_name: Optional[str] = Field(None, max_length=200, description="目标实体名称")
    target_entity_id: Optional[str] = Field(None, max_length=100, description="目标实体ID")
    relation_properties: Optional[Dict[str, Any]] = Field(None, description="关系属性")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="置信度")
    is_active: bool = Field(default=True, description="是否活跃")

class KnowledgeGraphCreate(KnowledgeGraphBase):
    pass

class KnowledgeGraphUpdate(BaseModel):
    entity_type: Optional[str] = Field(None, max_length=50, description="实体类型")
    entity_name: Optional[str] = Field(None, min_length=1, max_length=200, description="实体名称")
    entity_id: Optional[str] = Field(None, max_length=100, description="实体ID")
    relation_type: Optional[str] = Field(None, max_length=50, description="关系类型")
    target_entity_type: Optional[str] = Field(None, max_length=50, description="目标实体类型")
    target_entity_name: Optional[str] = Field(None, max_length=200, description="目标实体名称")
    target_entity_id: Optional[str] = Field(None, max_length=100, description="目标实体ID")
    relation_properties: Optional[Dict[str, Any]] = Field(None, description="关系属性")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="置信度")
    is_active: Optional[bool] = Field(None, description="是否活跃")

class KnowledgeGraphResponse(KnowledgeGraphBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 复合响应模型
class AlternativeDataWithDetails(AlternativeDataResponse):
    satellite_data: Optional[SatelliteDataResponse] = None
    supply_chain_data: Optional[SupplyChainDataResponse] = None
    recruitment_data: Optional[RecruitmentDataResponse] = None
    sentiment_data: Optional[SentimentDataResponse] = None 