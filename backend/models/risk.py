from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON
from datetime import datetime
from . import Base

class RiskAssessmentResult(Base):
    """
    风险测评结果模型。
    存储用户提交的风险测评问卷答案。
    """
    __tablename__ = "risk_assessment_results"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    answers: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow) 