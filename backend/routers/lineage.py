from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List
from database import get_db
from models.feature import Feature
from models.feature_lineage import FeatureLineage
from schemas.lineage import (
    FeatureLineageCreate,
    FeatureLineageResponse,
    FeatureLineageTree,
    FeatureLineageGraph,
    LineageAnalysis
)

router = APIRouter(prefix="/lineage", tags=["lineage"])

@router.post("/", response_model=FeatureLineageResponse, status_code=status.HTTP_201_CREATED)
def create_lineage(lineage: FeatureLineageCreate, db: Session = Depends(get_db)):
    """创建特征血缘关系"""
    # 验证特征是否存在
    feature = db.query(Feature).filter(Feature.id == lineage.feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="特征不存在")
    
    # 验证父特征是否存在
    if lineage.parent_feature_id is not None:
        parent_feature = db.query(Feature).filter(Feature.id == lineage.parent_feature_id).first()
        if not parent_feature:
            raise HTTPException(status_code=404, detail="父特征不存在")
        
        # 检查循环依赖
        if lineage.feature_id == lineage.parent_feature_id:
            raise HTTPException(status_code=400, detail="不能依赖自己")
    
    # 检查是否已存在血缘关系
    existing_lineage = db.query(FeatureLineage).filter(
        and_(
            FeatureLineage.feature_id == lineage.feature_id,
            FeatureLineage.parent_feature_id == lineage.parent_feature_id
        )
    ).first()
    
    if existing_lineage:
        raise HTTPException(status_code=400, detail="血缘关系已存在")
    
    # 创建血缘关系
    lineage_data = lineage.model_dump()
    db_lineage = FeatureLineage(**lineage_data)
    db.add(db_lineage)
    db.commit()
    db.refresh(db_lineage)
    
    # 构造返回对象，确保类型正确
    return FeatureLineageResponse(
        id=getattr(db_lineage, 'id'),
        feature_id=getattr(db_lineage, 'feature_id'),
        parent_feature_id=getattr(db_lineage, 'parent_feature_id'),
        lineage_type=str(getattr(db_lineage, 'lineage_type')),
        transformation_rule=str(getattr(db_lineage, 'transformation_rule')) if getattr(db_lineage, 'transformation_rule') is not None else None,
        data_source=str(getattr(db_lineage, 'data_source')) if getattr(db_lineage, 'data_source') is not None else None,
        created_at=getattr(db_lineage, 'created_at')
    )

@router.get("/feature/{feature_id}", response_model=List[FeatureLineageResponse])
def get_feature_lineages(feature_id: int, db: Session = Depends(get_db)):
    """获取特征的血缘关系"""
    # 验证特征是否存在
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="特征不存在")
    
    # 查询血缘关系
    db_lineages = db.query(FeatureLineage).filter(FeatureLineage.feature_id == feature_id).all()
    
    # 转换为响应模型，确保类型正确
    lineages = []
    for db_lineage in db_lineages:
        lineage = FeatureLineageResponse(
            id=getattr(db_lineage, 'id'),
            feature_id=getattr(db_lineage, 'feature_id'),
            parent_feature_id=getattr(db_lineage, 'parent_feature_id'),
            lineage_type=str(getattr(db_lineage, 'lineage_type')),
            transformation_rule=str(getattr(db_lineage, 'transformation_rule')) if getattr(db_lineage, 'transformation_rule') is not None else None,
            data_source=str(getattr(db_lineage, 'data_source')) if getattr(db_lineage, 'data_source') is not None else None,
            created_at=getattr(db_lineage, 'created_at')
        )
        lineages.append(lineage)
    
    return lineages

@router.get("/feature/{feature_id}/tree", response_model=FeatureLineageTree)
def get_feature_lineage_tree(feature_id: int, db: Session = Depends(get_db)):
    """获取特征的血缘树"""
    # 验证特征是否存在
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="特征不存在")
    
    def build_tree(current_feature_id: int, depth: int = 0) -> FeatureLineageTree:
        current_feature = db.query(Feature).filter(Feature.id == current_feature_id).first()
        if not current_feature:
            raise HTTPException(status_code=404, detail="特征不存在")
        
        # 查找当前特征的血缘关系
        lineage = db.query(FeatureLineage).filter(FeatureLineage.feature_id == current_feature_id).first()
        
        # 获取父特征信息
        parent_id = None
        parent_name = None
        lineage_type = "root"
        transformation_rule = None
        data_source = None
        
        if lineage is not None:
            parent_id = getattr(lineage, 'parent_feature_id')
            lineage_type = getattr(lineage, 'lineage_type')
            transformation_rule = None
            if getattr(lineage, 'transformation_rule') is not None:
                transformation_rule = str(getattr(lineage, 'transformation_rule'))
            data_source = None
            if getattr(lineage, 'data_source') is not None:
                data_source = str(getattr(lineage, 'data_source'))
            
            # 获取父特征名称
            if parent_id is not None:
                parent_feature = db.query(Feature).filter(Feature.id == parent_id).first()
                if parent_feature:
                    parent_name = getattr(parent_feature, 'name')
        
        # 构建血缘树节点
        tree = FeatureLineageTree(
            feature_id=getattr(current_feature, 'id'),
            feature_name=str(getattr(current_feature, 'name')),
            parent_id=parent_id,
            parent_name=str(parent_name) if parent_name is not None else None,
            lineage_type=str(lineage_type),
            transformation_rule=transformation_rule,
            data_source=data_source,
            depth=depth
        )
        
        # 递归构建子节点
        children_lineages = db.query(FeatureLineage).filter(
            FeatureLineage.parent_feature_id == current_feature_id
        ).all()
        
        for child_lineage in children_lineages:
            child_feature_id = getattr(child_lineage, 'feature_id')
            child_tree = build_tree(child_feature_id, depth + 1)
            tree.children.append(child_tree)
        
        return tree
    
    return build_tree(feature_id)

@router.get("/feature/{feature_id}/graph", response_model=FeatureLineageGraph)
def get_feature_lineage_graph(feature_id: int, db: Session = Depends(get_db)):
    """获取特征的血缘图"""
    # 验证特征是否存在
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="特征不存在")
    
    # 获取所有相关特征
    all_lineages = db.query(FeatureLineage).filter(
        or_(
            FeatureLineage.feature_id == feature_id,
            FeatureLineage.parent_feature_id == feature_id
        )
    ).all()
    
    # 构建节点和边
    nodes = []
    edges = []
    node_ids = set()  # 用于存储整数ID
    
    for lineage in all_lineages:
        # 获取当前特征ID（确保是整数类型）
        current_feature_id = getattr(lineage, 'feature_id')
        
        # 添加当前特征节点
        if current_feature_id not in node_ids:
            feature = db.query(Feature).filter(Feature.id == current_feature_id).first()
            if feature:
                # 从SQLAlchemy对象中获取实际值
                feature_id_int = getattr(feature, 'id')
                feature_name = str(getattr(feature, 'name'))
                feature_type = str(getattr(feature, 'type'))
                
                nodes.append({
                    "id": feature_id_int,
                    "name": feature_name,
                    "type": feature_type
                })
                node_ids.add(feature_id_int)
        
        # 添加父特征节点
        parent_id = getattr(lineage, 'parent_feature_id')
        if parent_id is not None:
            if parent_id not in node_ids:
                parent_feature = db.query(Feature).filter(Feature.id == parent_id).first()
                if parent_feature:
                    # 从SQLAlchemy对象中获取实际值
                    parent_id_int = getattr(parent_feature, 'id')
                    parent_name = str(getattr(parent_feature, 'name'))
                    parent_type = str(getattr(parent_feature, 'type'))
                    
                    nodes.append({
                        "id": parent_id_int,
                        "name": parent_name,
                        "type": parent_type
                    })
                    node_ids.add(parent_id_int)
        
        # 添加边
        if parent_id is not None:
            # 从SQLAlchemy对象中获取实际值
            source_id = parent_id
            target_id = current_feature_id
            lineage_type = str(getattr(lineage, 'lineage_type'))
            
            # 安全地处理可能为None的字段
            transformation_rule = None
            if getattr(lineage, 'transformation_rule') is not None:
                transformation_rule = str(getattr(lineage, 'transformation_rule'))
            
            edges.append({
                "source": source_id,
                "target": target_id,
                "type": lineage_type,
                "rule": transformation_rule
            })
    
    # 找出根节点和叶子节点
    root_nodes = [node["id"] for node in nodes if not any(edge["target"] == node["id"] for edge in edges)]
    leaf_nodes = [node["id"] for node in nodes if not any(edge["source"] == node["id"] for edge in edges)]
    
    return FeatureLineageGraph(
        nodes=nodes,
        edges=edges,
        root_nodes=root_nodes,
        leaf_nodes=leaf_nodes
    )

@router.get("/feature/{feature_id}/analysis", response_model=LineageAnalysis)
def analyze_feature_lineage(feature_id: int, db: Session = Depends(get_db)):
    """分析特征血缘关系"""
    # 验证特征是否存在
    feature = db.query(Feature).filter(Feature.id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="特征不存在")
    
    # 计算依赖数量
    dependency_count = db.query(FeatureLineage).filter(
        FeatureLineage.feature_id == feature_id
    ).count()
    
    # 计算被依赖数量
    dependent_count = db.query(FeatureLineage).filter(
        FeatureLineage.parent_feature_id == feature_id
    ).count()
    
    # 检测循环依赖（简化版本）
    circular_dependencies = []
    
    # 计算最大深度
    def calculate_depth(current_feature_id: int, visited=None):
        """计算特征依赖的最大深度"""
        # 初始化visited集合
        if visited is None:
            visited = set()
        
        # 检查循环依赖
        if current_feature_id in visited:
            return 0
        
        # 添加当前特征到已访问集合
        new_visited = visited.copy()
        new_visited.add(current_feature_id)
        max_depth = 0
        
        # 查找当前特征的所有依赖
        lineages = db.query(FeatureLineage).filter(FeatureLineage.feature_id == current_feature_id).all()
        for lineage in lineages:
            # 确保parent_feature_id不为None
            parent_id = getattr(lineage, 'parent_feature_id')
            if parent_id is not None:
                # 递归计算深度
                depth = calculate_depth(parent_id, new_visited)
                max_depth = max(max_depth, depth + 1)
        
        return max_depth
    
    # 计算最大深度
    max_depth = calculate_depth(feature_id)
    
    # 构建关键路径（简化版本）
    critical_path = [feature_id]
    current_id = feature_id
    while True:
        lineage = db.query(FeatureLineage).filter(FeatureLineage.feature_id == current_id).first()
        if lineage:
            parent_id = getattr(lineage, 'parent_feature_id')
            if parent_id is not None:
                critical_path.append(parent_id)
                current_id = parent_id
            else:
                break
        else:
            break
    
    # 从SQLAlchemy对象中获取实际值
    feature_id_val = getattr(feature, 'id')
    feature_name_val = str(getattr(feature, 'name'))
    
    return LineageAnalysis(
        feature_id=feature_id_val,
        feature_name=feature_name_val,
        dependency_count=dependency_count,
        dependent_count=dependent_count,
        max_depth=max_depth,
        circular_dependencies=circular_dependencies,
        critical_path=critical_path
    ) 