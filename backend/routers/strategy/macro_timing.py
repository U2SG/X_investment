"""
宏观择时模型模块
提供宏观择时信号生成和历史查询功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    Strategy, MacroTimingSignal
)
from models.ai_models import MacroTimingModel
from schemas.strategy import (
    MacroTimingRequest, MacroTimingResponse
)

router = APIRouter(prefix="", tags=["宏观择时模型"])

# 初始化AI模型
macro_timing_model = MacroTimingModel()


@router.post("/macro_timing_signal", response_model=MacroTimingResponse)
def macro_timing_signal(
    req: MacroTimingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成宏观择时信号"""
    print("[DEBUG] 宏观择时API收到请求:", req)
    
    # 使用真实AI模型生成配置建议
    allocation, reasoning, confidence = macro_timing_model.generate_asset_allocation(
        economic_cycle=req.economic_cycle,
        market_sentiment=req.market_sentiment,
        additional_factors=req.additional_factors
    )
    
    print("[DEBUG] 宏观择时API响应:", allocation, reasoning, confidence)
    
    # 创建信号日期
    signal_date = datetime.utcnow()
    
    # 持久化存储到数据库
    db_signal = MacroTimingSignal(
        economic_cycle=req.economic_cycle,
        market_sentiment=req.market_sentiment,
        additional_factors=req.additional_factors,
        recommended_allocation=allocation,
        reasoning=reasoning,
        confidence_score=confidence,
        model_version=macro_timing_model.model_name,
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
    
    return MacroTimingResponse(
        recommended_allocation=allocation,
        reasoning=reasoning,
        signal_date=signal_date
    )


@router.get("/macro_timing_signals", response_model=List[MacroTimingResponse])
def get_macro_timing_signals(
    strategy_id: Optional[int] = Query(None, description="策略ID"),
    economic_cycle: Optional[str] = Query(None, description="经济周期"),
    market_sentiment: Optional[str] = Query(None, description="市场情绪"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取宏观择时信号历史记录"""
    query = db.query(MacroTimingSignal)
    
    # 应用筛选条件
    if strategy_id:
        query = query.filter(MacroTimingSignal.strategy_id == strategy_id)
    if economic_cycle:
        query = query.filter(MacroTimingSignal.economic_cycle == economic_cycle)
    if market_sentiment:
        query = query.filter(MacroTimingSignal.market_sentiment == market_sentiment)
    if start_date:
        query = query.filter(MacroTimingSignal.signal_date >= start_date)
    if end_date:
        query = query.filter(MacroTimingSignal.signal_date <= end_date)
    
    # 排序并分页
    signals = query.order_by(MacroTimingSignal.signal_date.desc()).offset(offset).limit(limit).all()
    
    # 转换为响应格式
    result = []
    for signal in signals:
        result.append(MacroTimingResponse(
            recommended_allocation=dict(signal.recommended_allocation) if signal.recommended_allocation else {},
            reasoning=str(signal.reasoning) if signal.reasoning else None,
            signal_date=signal.signal_date
        ))
    
    return result


@router.get("/macro_timing_signals/{signal_id}", response_model=MacroTimingResponse)
def get_macro_timing_signal(
    signal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个宏观择时信号"""
    signal = db.query(MacroTimingSignal).filter(MacroTimingSignal.id == signal_id).first()
    if not signal:
        raise HTTPException(status_code=404, detail="信号不存在")
    
    return MacroTimingResponse(
        recommended_allocation=signal.recommended_allocation,
        reasoning=signal.reasoning,
        signal_date=signal.signal_date
    ) 