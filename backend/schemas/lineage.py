from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class FeatureLineageBase(BaseModel):
    """血缘关系基础模型"""
    feature_id: int = Field(..., description="特征ID")
    parent_feature_id: Optional[int] = Field(None, description="父特征ID")
    lineage_type: str = Field(default="derived", description="血缘类型")
    transformation_rule: Optional[str] = Field(None, description="转换规则描述")
    data_source: Optional[str] = Field(None, description="数据来源")

class FeatureLineageCreate(FeatureLineageBase):
    pass

class FeatureLineageUpdate(BaseModel):
    """血缘关系更新模型"""
    parent_feature_id: Optional[int] = Field(None, description="父特征ID")
    lineage_type: Optional[str] = Field(None, description="血缘类型")
    transformation_rule: Optional[str] = Field(None, description="转换规则描述")
    data_source: Optional[str] = Field(None, description="数据来源")

class FeatureLineageResponse(FeatureLineageBase):
    """血缘关系响应模型"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FeatureDependencyBase(BaseModel):
    """特征依赖基础模型"""
    dependent_id: int = Field(..., description="依赖方特征ID")
    dependency_id: int = Field(..., description="被依赖方特征ID")
    dependency_type: str = Field(default="direct", description="依赖类型")

class FeatureDependencyCreate(FeatureDependencyBase):
    pass

class FeatureDependencyResponse(FeatureDependencyBase):
    """特征依赖响应模型"""
    created_at: datetime

    class Config:
        from_attributes = True

class FeatureLineageTree(BaseModel):
    """特征血缘树模型"""
    feature_id: int
    feature_name: str
    parent_id: Optional[int]
    parent_name: Optional[str]
    lineage_type: str
    transformation_rule: Optional[str]
    data_source: Optional[str]
    children: List['FeatureLineageTree'] = []
    depth: int = 0

    class Config:
        from_attributes = True

# 解决循环引用
FeatureLineageTree.model_rebuild()

class FeatureLineageGraph(BaseModel):
    """特征血缘图模型"""
    nodes: List[dict] = Field(..., description="节点列表")
    edges: List[dict] = Field(..., description="边列表")
    root_nodes: List[int] = Field(..., description="根节点ID列表")
    leaf_nodes: List[int] = Field(..., description="叶子节点ID列表")

class LineageAnalysis(BaseModel):
    """血缘分析结果模型"""
    feature_id: int
    feature_name: str
    dependency_count: int = Field(..., description="依赖数量")
    dependent_count: int = Field(..., description="被依赖数量")
    max_depth: int = Field(..., description="最大深度")
    circular_dependencies: List[List[int]] = Field(default=[], description="循环依赖")
    critical_path: List[int] = Field(default=[], description="关键路径") 