"""
另类数据模型
包含卫星图像、供应链、招聘、舆情等另类数据源
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
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

class AlternativeData(Base):
    """另类数据基础模型"""
    __tablename__ = "alternative_data"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="数据名称")
    data_type = Column(String(50), nullable=False, comment="数据类型")
    source = Column(String(100), nullable=False, comment="数据源")
    description = Column(Text, comment="数据描述")
    
    # 时间相关
    data_date = Column(DateTime, nullable=False, comment="数据日期")
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否活跃")
    is_processed = Column(Boolean, default=False, comment="是否已处理")
    
    # 元数据
    data_metadata = Column(JSON, comment="元数据")
    
    # 关联关系
    satellite_data = relationship("SatelliteData", back_populates="alternative_data", uselist=False)
    supply_chain_data = relationship("SupplyChainData", back_populates="alternative_data", uselist=False)
    recruitment_data = relationship("RecruitmentData", back_populates="alternative_data", uselist=False)
    sentiment_data = relationship("SentimentData", back_populates="alternative_data", uselist=False)

class SatelliteData(Base):
    """卫星图像数据"""
    __tablename__ = "satellite_data"
    
    id = Column(Integer, primary_key=True, index=True)
    alternative_data_id = Column(Integer, ForeignKey("alternative_data.id"), nullable=False)
    
    # 位置信息
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    location_name = Column(String(200), comment="位置名称")
    
    # 图像数据
    image_url = Column(String(500), comment="图像URL")
    image_metadata = Column(JSON, comment="图像元数据")
    
    # 分析结果
    vehicle_count = Column(Integer, comment="车辆数量")
    parking_density = Column(Float, comment="停车密度")
    building_activity = Column(Float, comment="建筑活动指数")
    vegetation_index = Column(Float, comment="植被指数")
    
    # 关联关系
    alternative_data = relationship("AlternativeData", back_populates="satellite_data")

class SupplyChainData(Base):
    """供应链数据"""
    __tablename__ = "supply_chain_data"
    
    id = Column(Integer, primary_key=True, index=True)
    alternative_data_id = Column(Integer, ForeignKey("alternative_data.id"), nullable=False)
    
    # 供应链信息
    company_name = Column(String(200), nullable=False, comment="公司名称")
    industry = Column(String(100), comment="行业")
    supply_chain_level = Column(String(50), comment="供应链层级")
    
    # 指标数据
    inventory_level = Column(Float, comment="库存水平")
    delivery_time = Column(Float, comment="交付时间")
    supplier_count = Column(Integer, comment="供应商数量")
    order_volume = Column(Float, comment="订单量")
    
    # 关联关系
    alternative_data = relationship("AlternativeData", back_populates="supply_chain_data")

class RecruitmentData(Base):
    """招聘数据"""
    __tablename__ = "recruitment_data"
    
    id = Column(Integer, primary_key=True, index=True)
    alternative_data_id = Column(Integer, ForeignKey("alternative_data.id"), nullable=False)
    
    # 招聘信息
    company_name = Column(String(200), nullable=False, comment="公司名称")
    job_title = Column(String(200), comment="职位名称")
    location = Column(String(200), comment="工作地点")
    industry = Column(String(100), comment="行业")
    
    # 招聘指标
    job_count = Column(Integer, comment="职位数量")
    salary_range = Column(String(100), comment="薪资范围")
    experience_level = Column(String(50), comment="经验要求")
    skill_requirements = Column(JSON, comment="技能要求")
    
    # 关联关系
    alternative_data = relationship("AlternativeData", back_populates="recruitment_data")

class SentimentData(Base):
    """舆情数据"""
    __tablename__ = "sentiment_data"
    
    id = Column(Integer, primary_key=True, index=True)
    alternative_data_id = Column(Integer, ForeignKey("alternative_data.id"), nullable=False)
    
    # 舆情信息
    source_type = Column(String(50), nullable=False, comment="来源类型")
    content_type = Column(String(50), comment="内容类型")
    language = Column(String(20), default="zh", comment="语言")
    
    # 情感分析
    sentiment_score = Column(Float, comment="情感得分")
    sentiment_label = Column(String(20), comment="情感标签")
    confidence = Column(Float, comment="置信度")
    
    # 内容分析
    keywords = Column(JSON, comment="关键词")
    entities = Column(JSON, comment="实体")
    topics = Column(JSON, comment="主题")
    
    # 关联关系
    alternative_data = relationship("AlternativeData", back_populates="sentiment_data")

class KnowledgeGraph(Base):
    """知识图谱"""
    __tablename__ = "knowledge_graph"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 实体信息
    entity_type = Column(String(50), nullable=False, comment="实体类型")
    entity_name = Column(String(200), nullable=False, comment="实体名称")
    entity_id = Column(String(100), comment="实体ID")
    
    # 关系信息
    relation_type = Column(String(50), comment="关系类型")
    target_entity_type = Column(String(50), comment="目标实体类型")
    target_entity_name = Column(String(200), comment="目标实体名称")
    target_entity_id = Column(String(100), comment="目标实体ID")
    
    # 关系属性
    relation_properties = Column(JSON, comment="关系属性")
    confidence = Column(Float, comment="置信度")
    
    # 时间信息
    created_at = Column(DateTime, default=func.now(), comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 状态
    is_active = Column(Boolean, default=True, comment="是否活跃") 