"""
另类数据路由
提供另类数据的CRUD操作API
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.alternative_data import (
    AlternativeData, SatelliteData, SupplyChainData, 
    RecruitmentData, SentimentData, KnowledgeGraph
)
from schemas.alternative_data import (
    AlternativeDataCreate, AlternativeDataUpdate, AlternativeDataResponse,
    SatelliteDataCreate, SatelliteDataUpdate, SatelliteDataResponse,
    SupplyChainDataCreate, SupplyChainDataUpdate, SupplyChainDataResponse,
    RecruitmentDataCreate, RecruitmentDataUpdate, RecruitmentDataResponse,
    SentimentDataCreate, SentimentDataUpdate, SentimentDataResponse,
    KnowledgeGraphCreate, KnowledgeGraphUpdate, KnowledgeGraphResponse,
    AlternativeDataWithDetails
)
from utils.auth import get_current_user
from models.user import User

router = APIRouter(prefix="/alternative-data", tags=["alternative-data"])

# 另类数据基础CRUD
@router.post("/", response_model=AlternativeDataResponse, status_code=status.HTTP_201_CREATED)
def create_alternative_data(
    data: AlternativeDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建另类数据"""
    db_data = AlternativeData(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/", response_model=List[AlternativeDataResponse])
def get_alternative_data_list(
    data_type: Optional[str] = Query(None, description="数据类型"),
    source: Optional[str] = Query(None, description="数据源"),
    is_active: Optional[bool] = Query(None, description="是否活跃"),
    is_processed: Optional[bool] = Query(None, description="是否已处理"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取另类数据列表"""
    query = db.query(AlternativeData)
    
    if data_type:
        query = query.filter(AlternativeData.data_type == data_type)
    if source:
        query = query.filter(AlternativeData.source == source)
    if is_active is not None:
        query = query.filter(AlternativeData.is_active == is_active)
    if is_processed is not None:
        query = query.filter(AlternativeData.is_processed == is_processed)
    
    data_list = query.order_by(AlternativeData.created_at.desc()).offset(offset).limit(limit).all()
    return data_list

@router.get("/{data_id}", response_model=AlternativeDataWithDetails)
def get_alternative_data(
    data_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取另类数据详情"""
    data = db.query(AlternativeData).filter(AlternativeData.id == data_id).first()
    if not data:
        raise HTTPException(status_code=404, detail="数据不存在")
    
    # 获取关联的详细数据
    satellite_data = db.query(SatelliteData).filter(SatelliteData.alternative_data_id == data_id).first()
    supply_chain_data = db.query(SupplyChainData).filter(SupplyChainData.alternative_data_id == data_id).first()
    recruitment_data = db.query(RecruitmentData).filter(RecruitmentData.alternative_data_id == data_id).first()
    sentiment_data = db.query(SentimentData).filter(SentimentData.alternative_data_id == data_id).first()
    
    return AlternativeDataWithDetails(
        **data.__dict__,
        satellite_data=satellite_data,
        supply_chain_data=supply_chain_data,
        recruitment_data=recruitment_data,
        sentiment_data=sentiment_data
    )

@router.put("/{data_id}", response_model=AlternativeDataResponse)
def update_alternative_data(
    data_id: int,
    data_update: AlternativeDataUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新另类数据"""
    db_data = db.query(AlternativeData).filter(AlternativeData.id == data_id).first()
    if not db_data:
        raise HTTPException(status_code=404, detail="数据不存在")
    
    update_data = data_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_data, field, value)
    
    db.commit()
    db.refresh(db_data)
    return db_data

@router.delete("/{data_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alternative_data(
    data_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除另类数据"""
    db_data = db.query(AlternativeData).filter(AlternativeData.id == data_id).first()
    if not db_data:
        raise HTTPException(status_code=404, detail="数据不存在")
    
    db.delete(db_data)
    db.commit()

# 卫星图像数据
@router.post("/satellite", response_model=SatelliteDataResponse, status_code=status.HTTP_201_CREATED)
def create_satellite_data(
    data: SatelliteDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建卫星图像数据"""
    # 验证另类数据是否存在
    alternative_data = db.query(AlternativeData).filter(AlternativeData.id == data.alternative_data_id).first()
    if not alternative_data:
        raise HTTPException(status_code=404, detail="另类数据不存在")
    
    db_data = SatelliteData(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/satellite", response_model=List[SatelliteDataResponse])
def get_satellite_data_list(
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取卫星图像数据列表"""
    data_list = db.query(SatelliteData).offset(offset).limit(limit).all()
    return data_list

# 供应链数据
@router.post("/supply-chain", response_model=SupplyChainDataResponse, status_code=status.HTTP_201_CREATED)
def create_supply_chain_data(
    data: SupplyChainDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建供应链数据"""
    # 验证另类数据是否存在
    alternative_data = db.query(AlternativeData).filter(AlternativeData.id == data.alternative_data_id).first()
    if not alternative_data:
        raise HTTPException(status_code=404, detail="另类数据不存在")
    
    db_data = SupplyChainData(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/supply-chain", response_model=List[SupplyChainDataResponse])
def get_supply_chain_data_list(
    company_name: Optional[str] = Query(None, description="公司名称"),
    industry: Optional[str] = Query(None, description="行业"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取供应链数据列表"""
    query = db.query(SupplyChainData)
    
    if company_name:
        query = query.filter(SupplyChainData.company_name.contains(company_name))
    if industry:
        query = query.filter(SupplyChainData.industry == industry)
    
    data_list = query.offset(offset).limit(limit).all()
    return data_list

# 招聘数据
@router.post("/recruitment", response_model=RecruitmentDataResponse, status_code=status.HTTP_201_CREATED)
def create_recruitment_data(
    data: RecruitmentDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建招聘数据"""
    # 验证另类数据是否存在
    alternative_data = db.query(AlternativeData).filter(AlternativeData.id == data.alternative_data_id).first()
    if not alternative_data:
        raise HTTPException(status_code=404, detail="另类数据不存在")
    
    db_data = RecruitmentData(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/recruitment", response_model=List[RecruitmentDataResponse])
def get_recruitment_data_list(
    company_name: Optional[str] = Query(None, description="公司名称"),
    industry: Optional[str] = Query(None, description="行业"),
    location: Optional[str] = Query(None, description="工作地点"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取招聘数据列表"""
    query = db.query(RecruitmentData)
    
    if company_name:
        query = query.filter(RecruitmentData.company_name.contains(company_name))
    if industry:
        query = query.filter(RecruitmentData.industry == industry)
    if location:
        query = query.filter(RecruitmentData.location.contains(location))
    
    data_list = query.offset(offset).limit(limit).all()
    return data_list

# 舆情数据
@router.post("/sentiment", response_model=SentimentDataResponse, status_code=status.HTTP_201_CREATED)
def create_sentiment_data(
    data: SentimentDataCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建舆情数据"""
    # 验证另类数据是否存在
    alternative_data = db.query(AlternativeData).filter(AlternativeData.id == data.alternative_data_id).first()
    if not alternative_data:
        raise HTTPException(status_code=404, detail="另类数据不存在")
    
    db_data = SentimentData(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/sentiment", response_model=List[SentimentDataResponse])
def get_sentiment_data_list(
    source_type: Optional[str] = Query(None, description="来源类型"),
    sentiment_label: Optional[str] = Query(None, description="情感标签"),
    language: Optional[str] = Query(None, description="语言"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取舆情数据列表"""
    query = db.query(SentimentData)
    
    if source_type:
        query = query.filter(SentimentData.source_type == source_type)
    if sentiment_label:
        query = query.filter(SentimentData.sentiment_label == sentiment_label)
    if language:
        query = query.filter(SentimentData.language == language)
    
    data_list = query.offset(offset).limit(limit).all()
    return data_list

# 知识图谱
@router.post("/knowledge-graph", response_model=KnowledgeGraphResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_graph(
    data: KnowledgeGraphCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建知识图谱关系"""
    db_data = KnowledgeGraph(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

@router.get("/knowledge-graph", response_model=List[KnowledgeGraphResponse])
def get_knowledge_graph_list(
    entity_type: Optional[str] = Query(None, description="实体类型"),
    entity_name: Optional[str] = Query(None, description="实体名称"),
    relation_type: Optional[str] = Query(None, description="关系类型"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取知识图谱关系列表"""
    query = db.query(KnowledgeGraph)
    
    if entity_type:
        query = query.filter(KnowledgeGraph.entity_type == entity_type)
    if entity_name:
        query = query.filter(KnowledgeGraph.entity_name.contains(entity_name))
    if relation_type:
        query = query.filter(KnowledgeGraph.relation_type == relation_type)
    
    data_list = query.offset(offset).limit(limit).all()
    return data_list

# 统计分析
@router.get("/statistics/overview")
def get_alternative_data_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取另类数据统计概览"""
    # 按数据类型统计
    type_stats = {}
    for data_type in ["卫星图像", "供应链", "招聘", "舆情", "社交媒体", "新闻", "天气", "交通", "能源", "其他"]:
        count = db.query(AlternativeData).filter(AlternativeData.data_type == data_type).count()
        type_stats[data_type] = count
    
    # 按数据源统计
    source_stats = {}
    sources = db.query(AlternativeData.source).distinct().all()
    for source in sources:
        count = db.query(AlternativeData).filter(AlternativeData.source == source[0]).count()
        source_stats[source[0]] = count
    
    # 处理状态统计
    processed_count = db.query(AlternativeData).filter(AlternativeData.is_processed == True).count()
    unprocessed_count = db.query(AlternativeData).filter(AlternativeData.is_processed == False).count()
    
    return {
        "type_statistics": type_stats,
        "source_statistics": source_stats,
        "processed_count": processed_count,
        "unprocessed_count": unprocessed_count,
        "total_count": processed_count + unprocessed_count
    } 