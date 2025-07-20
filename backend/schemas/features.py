from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
import re
from .feature_types import FeatureType

class FeatureBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="特征名称")
    type: str = Field(..., description="特征类型")
    version: str = Field(..., description="特征版本")
    created_by: str = Field(..., description="创建者")
    status: str = Field(default="active", description="特征状态")
    description: Optional[str] = Field(default=None, description="特征描述")
    lineage: Optional[str] = Field(default=None, description="特征血缘")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证特征名称格式"""
        # 先去除首尾空格
        v = v.strip()
        
        if not v:
            raise ValueError('特征名称不能为空')
        
        # 检查长度
        if len(v) < 1 or len(v) > 100:
            raise ValueError('特征名称长度必须在1-100字符之间')
        
        # 检查格式：只允许中文、英文、数字、下划线、中划线
        # 正则表达式：^[\u4e00-\u9fa5a-zA-Z0-9_-]+$
        pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_-]+$'
        if not re.match(pattern, v):
            raise ValueError('特征名称只能包含中文、英文、数字、下划线(_)、中划线(-)')
        
        # 检查是否以数字开头
        if v[0].isdigit():
            raise ValueError('特征名称不能以数字开头')
        
        # 检查是否以特殊字符结尾
        if v.endswith('_') or v.endswith('-'):
            raise ValueError('特征名称不能以下划线或中划线结尾')
        
        return v

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """验证特征类型"""
        if not v:
            raise ValueError('特征类型不能为空')
        
        # 处理旧数据中的类型名称不匹配问题
        type_mapping = {
            "数值": "数值型",
            "分类": "分类型",
            "文本": "文本型",
            "时间": "时间型",
            "复合": "复合型"
        }
        
        # 如果存在映射，则转换类型名称
        if v in type_mapping:
            v = type_mapping[v]
        
        if not FeatureType.is_valid_type(v):
            valid_types = FeatureType.get_all_types()
            raise ValueError(f'无效的特征类型: {v}。有效类型包括: {", ".join(valid_types)}')
        
        return v

class FeatureCreate(FeatureBase):
    pass

class FeatureUpdate(BaseModel):
    name: Optional[str] = Field(None, description="特征名称")
    type: Optional[str] = Field(None, description="特征类型")
    version: Optional[str] = Field(None, description="特征版本")
    created_by: Optional[str] = Field(None, description="创建者")
    status: Optional[str] = Field(None, description="特征状态")
    description: Optional[str] = Field(None, description="特征描述")
    lineage: Optional[str] = Field(None, description="特征血缘")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """验证特征名称格式（更新时可选）"""
        if v is None:
            return v
        
        # 去除首尾空格
        v = v.strip()
        
        # 检查是否为空
        if not v:
            raise ValueError('特征名称不能为空')
        
        # 检查长度
        if len(v) < 1 or len(v) > 100:
            raise ValueError('特征名称长度必须在1-100字符之间')
        
        # 检查格式：只允许中文、英文、数字、下划线、中划线
        pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_-]+$'
        if not re.match(pattern, v):
            raise ValueError('特征名称只能包含中文、英文、数字、下划线(_)、中划线(-)')
        
        # 检查是否以数字开头
        if v[0].isdigit():
            raise ValueError('特征名称不能以数字开头')
        
        # 检查是否以特殊字符结尾
        if v.endswith('_') or v.endswith('-'):
            raise ValueError('特征名称不能以下划线或中划线结尾')
        
        return v

    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        """验证特征类型（更新时可选）"""
        if v is None:
            return v
        
        # 处理旧数据中的类型名称不匹配问题
        type_mapping = {
            "数值": "数值型",
            "分类": "分类型",
            "文本": "文本型",
            "时间": "时间型",
            "复合": "复合型"
        }
        
        # 如果存在映射，则转换类型名称
        if v in type_mapping:
            v = type_mapping[v]
        
        if not FeatureType.is_valid_type(v):
            valid_types = FeatureType.get_all_types()
            raise ValueError(f'无效的特征类型: {v}。有效类型包括: {", ".join(valid_types)}')
        
        return v

class FeatureResponse(FeatureBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 