from enum import Enum
from typing import List

class FeatureType(str, Enum):
    """特征类型枚举"""
    
    # 数值型特征
    NUMERICAL = "数值型"
    PERCENTAGE = "百分比"
    RATIO = "比率"
    INDEX = "指数"
    
    # 分类型特征
    CATEGORICAL = "分类型"
    BINARY = "二分类"
    ORDINAL = "有序分类"
    
    # 文本型特征
    TEXT = "文本型"
    SENTIMENT = "情感分析"
    KEYWORD = "关键词"
    
    # 时间型特征
    TEMPORAL = "时间型"
    DATE = "日期"
    TIMESTAMP = "时间戳"
    DURATION = "持续时间"
    
    # 复合型特征
    COMPOSITE = "复合型"
    DERIVED = "衍生型"
    AGGREGATED = "聚合型"
    
    @classmethod
    def get_all_types(cls) -> List[str]:
        """获取所有特征类型"""
        return [member.value for member in cls]
    
    @classmethod
    def get_numerical_types(cls) -> List[str]:
        """获取数值型特征类型"""
        return [
            cls.NUMERICAL.value,
            cls.PERCENTAGE.value,
            cls.RATIO.value,
            cls.INDEX.value
        ]
    
    @classmethod
    def get_categorical_types(cls) -> List[str]:
        """获取分类型特征类型"""
        return [
            cls.CATEGORICAL.value,
            cls.BINARY.value,
            cls.ORDINAL.value
        ]
    
    @classmethod
    def get_text_types(cls) -> List[str]:
        """获取文本型特征类型"""
        return [
            cls.TEXT.value,
            cls.SENTIMENT.value,
            cls.KEYWORD.value
        ]
    
    @classmethod
    def get_temporal_types(cls) -> List[str]:
        """获取时间型特征类型"""
        return [
            cls.TEMPORAL.value,
            cls.DATE.value,
            cls.TIMESTAMP.value,
            cls.DURATION.value
        ]
    
    @classmethod
    def get_composite_types(cls) -> List[str]:
        """获取复合型特征类型"""
        return [
            cls.COMPOSITE.value,
            cls.DERIVED.value,
            cls.AGGREGATED.value
        ]
    
    @classmethod
    def is_valid_type(cls, type_value: str) -> bool:
        """验证特征类型是否有效"""
        return type_value in cls.get_all_types()
    
    @classmethod
    def get_type_category(cls, type_value: str) -> str:
        """获取特征类型所属类别"""
        if type_value in cls.get_numerical_types():
            return "数值型"
        elif type_value in cls.get_categorical_types():
            return "分类型"
        elif type_value in cls.get_text_types():
            return "文本型"
        elif type_value in cls.get_temporal_types():
            return "时间型"
        elif type_value in cls.get_composite_types():
            return "复合型"
        else:
            return "未知类型" 