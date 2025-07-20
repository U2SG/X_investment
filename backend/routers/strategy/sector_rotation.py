"""
行业轮动模型模块
提供行业轮动信号生成和历史查询功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    Strategy, SectorRotationSignal
)
from models.ai_models import SectorRotationModel
from schemas.strategy import (
    SectorRotationRequest, SectorRotationResponse
)

router = APIRouter(prefix="", tags=["行业轮动模型"])

# 初始化AI模型
sector_rotation_model = SectorRotationModel()


@router.post("/sector_rotation_signal", response_model=SectorRotationResponse)
def sector_rotation_signal(
    req: SectorRotationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成行业轮动信号"""
    print("[DEBUG] 行业轮动API收到请求:", req)
    
    # 使用真实AI模型生成行业配置建议
    allocation, reasoning, confidence = sector_rotation_model.generate_industry_allocation(
        industry_scores=req.industry_scores,
        fund_flows=req.fund_flows,
        additional_factors=req.additional_factors
    )
    
    print("[DEBUG] 行业轮动API响应:", allocation, reasoning, confidence)
    
    # 创建信号日期
    signal_date = datetime.utcnow()
    
    # 持久化存储到数据库
    db_signal = SectorRotationSignal(
        industry_scores=req.industry_scores,
        fund_flows=req.fund_flows,
        additional_factors=req.additional_factors,
        recommended_industry_allocation=allocation,
        reasoning=reasoning,
        confidence_score=confidence,
        model_version=sector_rotation_model.model_name,
        signal_date=signal_date
    )
    
    # 如果请求中包含策略ID，则关联到该策略
    if hasattr(req, 'strategy_id') and req.strategy_id:
        strategy = db.query(Strategy).filter(Strategy.id == req.strategy_id).first()
        if strategy:
            db_signal.strategy_id = strategy.id
    
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    
    return SectorRotationResponse(
        recommended_industry_allocation=allocation,
        reasoning=reasoning,
        signal_date=signal_date
    )


@router.get("/sector_rotation_signals", response_model=List[SectorRotationResponse])
def get_sector_rotation_signals(
    strategy_id: Optional[int] = Query(None, description="策略ID"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取行业轮动信号历史记录"""
    query = db.query(SectorRotationSignal)
    
    # 应用筛选条件
    if strategy_id:
        query = query.filter(SectorRotationSignal.strategy_id == strategy_id)
    if start_date:
        query = query.filter(SectorRotationSignal.signal_date >= start_date)
    if end_date:
        query = query.filter(SectorRotationSignal.signal_date <= end_date)
    
    # 排序并分页
    signals = query.order_by(SectorRotationSignal.signal_date.desc()).offset(offset).limit(limit).all()
    
    # 转换为响应格式
    result = []
    for signal in signals:
        result.append(SectorRotationResponse(
            recommended_industry_allocation=signal.recommended_industry_allocation,
            reasoning=signal.reasoning,
            signal_date=signal.signal_date
        ))
    
    return result


@router.get("/sector_rotation_signals/{signal_id}", response_model=SectorRotationResponse)
def get_sector_rotation_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个行业轮动信号"""
    signal = db.query(SectorRotationSignal).filter(SectorRotationSignal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="信号不存在")
    
    return SectorRotationResponse(
        recommended_industry_allocation=signal.recommended_industry_allocation,
        reasoning=signal.reasoning,
        signal_date=signal.signal_date
    ) 