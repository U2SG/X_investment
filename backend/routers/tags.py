"""
标签相关API路由
实现查询所有标签及其被引用次数
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
import sys
import os

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database import get_db
from models import Tag, Asset

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)

@router.get("/", response_model=List[dict])
def get_tags_with_ref_count(db: Session = Depends(get_db)):
    """
    查询所有标签及其被资产引用次数。
    - 返回: List[dict]，每项包含标签id、名称、被引用次数
    """
    tags = db.query(Tag).all()
    result = []
    for tag in tags:
        ref_count = len(tag.assets)
        result.append({"id": tag.id, "name": tag.name, "ref_count": ref_count})
    return result

@router.get("/assets")
def get_all_tags_with_assets(db: Session = Depends(get_db)):
    """
    查询所有标签及其下的资产列表。
    - 返回: List[dict]，每项包含标签id、名称、资产列表
    """
    tags = db.query(Tag).all()
    result = []
    for tag in tags:
        assets = [{"id": a.id, "code": a.code, "name": a.name} for a in tag.assets]
        result.append({"id": tag.id, "name": tag.name, "assets": assets})
    return result

@router.get("/{tag_id}")
def get_tag_detail(tag_id: int, db: Session = Depends(get_db)):
    """
    查询标签详情及其关联资产。
    - 参数: tag_id (int): 标签ID
    - 返回: dict，包含标签id、名称、资产列表
    - 异常: 标签不存在时返回404
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    assets = [{"id": a.id, "code": a.code, "name": a.name} for a in tag.assets]
    return {"id": tag.id, "name": tag.name, "assets": assets}

@router.delete("/{tag_id}", status_code=200)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """
    删除指定标签，若被资产引用则禁止删除。
    - 参数: tag_id (int): 标签ID
    - 返回: {"detail": "删除成功"}
    - 异常: 标签不存在或被引用时返回404/400
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    if len(tag.assets) > 0:
        raise HTTPException(status_code=400, detail="该标签已被资产引用，无法删除")
    db.delete(tag)
    db.commit()
    return {"detail": "删除成功"}

@router.post("/{tag_id}/assets", response_model=list[dict])
def add_assets_to_tag(tag_id: int, asset_ids: list[int] = Body(..., description="资产ID列表"), db: Session = Depends(get_db)):
    """
    为标签批量添加资产。
    - 参数: tag_id (int): 标签ID, asset_ids (List[int]): 资产ID列表
    - 返回: List[dict]，标签下最新资产列表
    - 异常: 标签或资产不存在时返回404/400
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    for asset_id in asset_ids:
        asset = db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise HTTPException(status_code=400, detail=f"资产ID {asset_id} 不存在")
        if asset not in tag.assets:
            tag.assets.append(asset)
    db.commit()
    return [{"id": a.id, "code": a.code, "name": a.name} for a in tag.assets]

@router.delete("/{tag_id}/assets/{asset_id}", status_code=200)
def remove_asset_from_tag(tag_id: int, asset_id: int, db: Session = Depends(get_db)):
    """
    将指定资产从标签下移除。
    - 参数: tag_id (int): 标签ID, asset_id (int): 资产ID
    - 返回: {"detail": "移除成功"}
    - 异常: 标签或资产不存在、未关联时返回404/400
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    if asset not in tag.assets:
        raise HTTPException(status_code=400, detail="该资产未关联此标签")
    tag.assets.remove(asset)
    db.commit()
    return {"detail": "移除成功"} 