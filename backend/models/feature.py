from sqlalchemy import Column, Integer, String, DateTime, Text
from database import Base
from datetime import datetime

class Feature(Base):
    __tablename__ = 'features'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    version = Column(String(20), nullable=False)
    created_by = Column(String(20), nullable=False)
    status = Column(String(20), default="active")
    description = Column(Text)
    lineage = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Feature(id={self.id}, name='{self.name}', type='{self.type}')>" 