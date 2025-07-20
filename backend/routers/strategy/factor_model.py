"""
因子模型管理模块
提供因子模型的增删改查功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    FactorModel
)
from schemas.strategy import (
    FactorModelCreate, FactorModelUpdate, FactorModelResponse
)

router = APIRouter(prefix="", tags=["因子模型管理"])


@router.post("/factors", response_model=FactorModelResponse, status_code=status.HTTP_201_CREATED)
def create_factor_model(
    factor_model: FactorModelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建因子模型"""
    db_factor_model = FactorModel(**factor_model.model_dump())
    db.add(db_factor_model)
    db.commit()
    db.refresh(db_factor_model)
    return db_factor_model


@router.get("/factors", response_model=List[FactorModelResponse])
def get_factor_models(
    is_active: Optional[bool] = Query(None, description="是否活跃"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取因子模型列表"""
    query = db.query(FactorModel)
    
    if is_active is not None:
        query = query.filter(FactorModel.is_active == is_active)
    
    factor_models = query.offset(offset).limit(limit).all()
    return factor_models


@router.get("/factors/{factor_model_id}", response_model=FactorModelResponse)
def get_factor_model(
    factor_model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个因子模型"""
    factor_model = db.query(FactorModel).filter(FactorModel.id == factor_model_id).first()
    if not factor_model:
        raise HTTPException(status_code=404, detail="因子模型不存在")
    return factor_model


@router.put("/factors/{factor_model_id}", response_model=FactorModelResponse)
def update_factor_model(
    factor_model_id: int,
    factor_model_update: FactorModelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新因子模型"""
    db_factor_model = db.query(FactorModel).filter(FactorModel.id == factor_model_id).first()
    if not db_factor_model:
        raise HTTPException(status_code=404, detail="因子模型不存在")
    
    update_data = factor_model_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_factor_model, field, value)
    
    db.commit()
    db.refresh(db_factor_model)
    return db_factor_model


@router.delete("/factors/{factor_model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_factor_model(
    factor_model_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除因子模型"""
    db_factor_model = db.query(FactorModel).filter(FactorModel.id == factor_model_id).first()
    if not db_factor_model:
        raise HTTPException(status_code=404, detail="因子模型不存在")
    
    db.delete(db_factor_model)
    db.commit() 