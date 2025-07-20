from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from database import Base
from datetime import datetime

class FeatureLineage(Base):
    """特征血缘关系模型"""
    __tablename__ = 'feature_lineages'
    
    id = Column(Integer, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey('features.id'), nullable=False)
    parent_feature_id = Column(Integer, ForeignKey('features.id'), nullable=True)
    lineage_type = Column(String(50), nullable=False, default='derived')  # derived, aggregated, transformed
    transformation_rule = Column(Text, nullable=True)  # 转换规则描述
    data_source = Column(String(200), nullable=True)  # 数据来源
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<FeatureLineage(feature_id={self.feature_id}, parent_id={self.parent_feature_id}, type={self.lineage_type})>" 