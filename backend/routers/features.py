from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc, asc
from typing import List, Optional
from pydantic import BaseModel
from models.feature import Feature
from schemas.features import FeatureCreate, FeatureUpdate, FeatureResponse
from schemas.feature_types import FeatureType
from database import get_db

router = APIRouter(prefix="/features", tags=["特征工程"])

class FeaturesResponse(BaseModel):
    """分页响应模型"""
    items: List[FeatureResponse]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool

class FeatureTypesResponse(BaseModel):
    """特征类型响应模型"""
    all_types: List[str]
    numerical_types: List[str]
    categorical_types: List[str]
    text_types: List[str]
    temporal_types: List[str]
    composite_types: List[str]

@router.get("/types", response_model=FeatureTypesResponse)
def get_feature_types():
    """
    获取所有可用的特征类型
    """
    return FeatureTypesResponse(
        all_types=FeatureType.get_all_types(),
        numerical_types=FeatureType.get_numerical_types(),
        categorical_types=FeatureType.get_categorical_types(),
        text_types=FeatureType.get_text_types(),
        temporal_types=FeatureType.get_temporal_types(),
        composite_types=FeatureType.get_composite_types()
    )

@router.get("/", response_model=FeaturesResponse)
def get_features(
    name: Optional[str] = Query(None, description="特征名称搜索"),
    type: Optional[str] = Query(None, description="特征类型搜索"),
    status: Optional[str] = Query(None, description="特征状态搜索"),
    limit: int = Query(10, ge=1, le=100, description="每页数量，默认10，最大100"),
    offset: int = Query(0, ge=0, description="偏移量，默认0"),
    sort_by: str = Query("created_at", description="排序字段：name, type, created_at, status"),
    sort_order: str = Query("desc", description="排序方向：asc, desc"),
    db: Session = Depends(get_db)
):
    """
    获取特征列表，支持按名称、类型、状态进行模糊搜索，支持分页和排序
    """
    # 构建基础查询
    query = db.query(Feature)
    
    # 按名称模糊搜索
    if name:
        query = query.filter(Feature.name.ilike(f"%{name}%"))
    
    # 按类型精确搜索
    if type:
        query = query.filter(Feature.type == type)
    
    # 按状态精确搜索
    if status:
        query = query.filter(Feature.status == status)
    
    # 应用排序
    sort_field = getattr(Feature, sort_by, Feature.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))
    
    # 获取总数
    total = query.count()
    
    # 应用分页
    features = query.offset(offset).limit(limit).all()
    
    # 计算分页信息
    has_next = offset + limit < total
    has_prev = offset > 0
    
    # 将 SQLAlchemy 对象转换为 Pydantic 对象
    feature_responses = [FeatureResponse.model_validate(feature) for feature in features]
    
    return FeaturesResponse(
        items=feature_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_next=has_next,
        has_prev=has_prev
    )

@router.post("/", response_model=FeatureResponse, status_code=status.HTTP_201_CREATED)
def create_feature(feature: FeatureCreate, db: Session = Depends(get_db)):
    db_feature = Feature(**feature.model_dump())
    db.add(db_feature)
    db.commit()
    db.refresh(db_feature)
    return db_feature

@router.get("/{feature_id}", response_model=FeatureResponse)
def get_feature(feature_id: int, db: Session = Depends(get_db)):
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="特征不存在")
    return feature

@router.put("/{feature_id}", response_model=FeatureResponse)
def update_feature(feature_id: int, feature_update: FeatureUpdate, db: Session = Depends(get_db)):
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="特征不存在")
    for k, v in feature_update.model_dump(exclude_unset=True).items():
        setattr(feature, k, v)
    db.commit()
    db.refresh(feature)
    return feature

@router.delete("/{feature_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feature(feature_id: int, db: Session = Depends(get_db)):
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="特征不存在")
    db.delete(feature)
    db.commit() 