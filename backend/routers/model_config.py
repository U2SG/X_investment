"""
模型配置路由
提供AI模型参数的配置和管理功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.model_config import ModelConfig
from schemas.model_config import (
    ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse,
    ModelConfigTemplate, MacroTimingConfig, SectorRotationConfig, MultiFactorConfig
)

router = APIRouter(prefix="/model-config", tags=["模型配置"])


@router.get("/templates", response_model=ModelConfigTemplate)
def get_model_config_templates():
    """获取模型配置模板"""
    return ModelConfigTemplate()


@router.get("/", response_model=List[ModelConfigResponse])
def get_model_configs(
    model_name: Optional[str] = Query(None, description="模型名称"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取模型配置列表"""
    query = db.query(ModelConfig)
    
    # 应用筛选条件
    if model_name:
        query = query.filter(ModelConfig.model_name == model_name)
    if is_active is not None:
        query = query.filter(ModelConfig.is_active == is_active)
    
    # 排序并分页
    configs = query.order_by(ModelConfig.created_at.desc()).offset(offset).limit(limit).all()
    
    return configs


@router.get("/{config_id}", response_model=ModelConfigResponse)
def get_model_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个模型配置"""
    config = db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    return config


@router.post("/", response_model=ModelConfigResponse)
def create_model_config(
    config: ModelConfigCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建模型配置"""
    # 检查是否已存在相同名称和版本的配置
    existing_config = db.query(ModelConfig).filter(
        ModelConfig.model_name == config.model_name,
        ModelConfig.model_version == config.model_version
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=400, 
            detail=f"已存在模型 {config.model_name} 版本 {config.model_version} 的配置"
        )
    
    # 创建新配置
    db_config = ModelConfig(
        model_name=config.model_name,
        model_version=config.model_version,
        parameters=config.parameters,
        description=config.description,
        is_active=config.is_active
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.put("/{config_id}", response_model=ModelConfigResponse)
def update_model_config(
    config_id: int,
    config_update: ModelConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新模型配置"""
    db_config = db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    # 更新字段
    if config_update.parameters is not None:
        db_config.parameters = config_update.parameters
    if config_update.description is not None:
        db_config.description = config_update.description
    if config_update.is_active is not None:
        db_config.is_active = config_update.is_active
    
    db_config.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.delete("/{config_id}")
def delete_model_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除模型配置"""
    db_config = db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    db.delete(db_config)
    db.commit()
    
    return {"message": "模型配置已删除"}


@router.post("/{config_id}/activate")
def activate_model_config(
    config_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """激活模型配置"""
    db_config = db.query(ModelConfig).filter(ModelConfig.id == config_id).first()
    if not db_config:
        raise HTTPException(status_code=404, detail="模型配置不存在")
    
    # 先停用同模型的其他配置
    db.query(ModelConfig).filter(
        ModelConfig.model_name == db_config.model_name,
        ModelConfig.is_active == True
    ).update({"is_active": False})
    
    # 激活当前配置
    db_config.is_active = True
    db_config.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": f"模型配置 {config_id} 已激活"}


@router.get("/active/{model_name}", response_model=ModelConfigResponse)
def get_active_model_config(
    model_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定模型的激活配置"""
    config = db.query(ModelConfig).filter(
        ModelConfig.model_name == model_name,
        ModelConfig.is_active == True
    ).first()
    
    if not config:
        raise HTTPException(
            status_code=404, 
            detail=f"模型 {model_name} 没有激活的配置"
        )
    
    return config


@router.post("/macro-timing/default")
def create_default_macro_timing_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建默认宏观择时模型配置"""
    default_config = MacroTimingConfig()
    
    # 检查是否已存在默认配置
    existing_config = db.query(ModelConfig).filter(
        ModelConfig.model_name == "macro_timing",
        ModelConfig.model_version == "1.0"
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=400,
            detail="默认宏观择时模型配置已存在"
        )
    
    # 创建默认配置
    db_config = ModelConfig(
        model_name="macro_timing",
        model_version="1.0",
        parameters=default_config.dict(),
        description="默认宏观择时模型配置",
        is_active=True
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.post("/sector-rotation/default")
def create_default_sector_rotation_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建默认行业轮动模型配置"""
    default_config = SectorRotationConfig()
    
    # 检查是否已存在默认配置
    existing_config = db.query(ModelConfig).filter(
        ModelConfig.model_name == "sector_rotation",
        ModelConfig.model_version == "1.0"
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=400,
            detail="默认行业轮动模型配置已存在"
        )
    
    # 创建默认配置
    db_config = ModelConfig(
        model_name="sector_rotation",
        model_version="1.0",
        parameters=default_config.dict(),
        description="默认行业轮动模型配置",
        is_active=True
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config


@router.post("/multi-factor/default")
def create_default_multi_factor_config(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建默认多因子模型配置"""
    default_config = MultiFactorConfig()
    
    # 检查是否已存在默认配置
    existing_config = db.query(ModelConfig).filter(
        ModelConfig.model_name == "multi_factor",
        ModelConfig.model_version == "1.0"
    ).first()
    
    if existing_config:
        raise HTTPException(
            status_code=400,
            detail="默认多因子模型配置已存在"
        )
    
    # 创建默认配置
    db_config = ModelConfig(
        model_name="multi_factor",
        model_version="1.0",
        parameters=default_config.dict(),
        description="默认多因子模型配置",
        is_active=True
    )
    
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    
    return db_config 