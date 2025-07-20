"""
多因子模型模块
提供多因子信号生成和历史查询功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from utils.auth import get_current_user
from models.user import User
from models.strategy import (
    Strategy, MultiFactorScore
)
from models.ai_models import MultiFactorModel
from schemas.strategy import (
    MultiFactorRequest, MultiFactorResponse, StockScore
)

router = APIRouter(prefix="", tags=["多因子模型"])

# 初始化AI模型
multi_factor_model = MultiFactorModel()


@router.post("/multi_factor_signal", response_model=MultiFactorResponse)
def multi_factor_signal(
    req: MultiFactorRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """生成多因子信号"""
    print("[DEBUG] 多因子模型API收到请求:", req)
    
    # 准备股票数据
    stocks_data = [{
        "symbol": stock.symbol,
        "name": stock.name,
        "factor_values": stock.factor_values
    } for stock in req.stocks]
    
    # 使用真实AI模型生成股票排名
    stock_scores, adjusted_weights, discovered_factors, reasoning, confidence = multi_factor_model.generate_stock_ranking(
        stocks_data=stocks_data,
        factor_weights=req.factor_weights,
        market_regime=req.market_regime,
        auto_discover=req.auto_discover
    )
    
    # 转换为StockScore对象
    stock_score_objects = []
    for score_data in stock_scores:
        stock_score_objects.append(StockScore(
            symbol=score_data["symbol"],
            name=score_data["name"],
            total_score=score_data["total_score"],
            factor_contribution=score_data["factor_contribution"],
            rank=score_data["rank"]
        ))
    
    print("[DEBUG] 多因子模型API响应:", stock_score_objects, adjusted_weights)
    
    # 创建信号日期
    signal_date = datetime.utcnow()
    
    # 持久化存储到数据库
    db_score = MultiFactorScore(
        stocks_data=stocks_data,
        factor_weights=req.factor_weights,
        market_regime=req.market_regime,
        auto_discover=req.auto_discover,
        stock_scores=stock_scores,
        adjusted_weights=adjusted_weights,
        discovered_factors=discovered_factors,
        reasoning=reasoning,
        model_version=multi_factor_model.model_name,
        signal_date=signal_date
    )
    
    # 如果请求中包含策略ID，则关联到该策略
    if hasattr(req, 'strategy_id') and req.strategy_id:
        strategy = db.query(Strategy).filter(Strategy.id == req.strategy_id).first()
        if strategy:
            db_score.strategy_id = strategy.id
    
    db.add(db_score)
    db.commit()
    db.refresh(db_score)
    
    return MultiFactorResponse(
        stock_scores=stock_score_objects,
        adjusted_weights=adjusted_weights,
        discovered_factors=discovered_factors,
        reasoning=reasoning,
        signal_date=signal_date
    )


@router.get("/multi_factor_scores", response_model=List[MultiFactorResponse])
def get_multi_factor_scores(
    strategy_id: Optional[int] = Query(None, description="策略ID"),
    market_regime: Optional[str] = Query(None, description="市场状态"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=1, le=1000, description="限制数量"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取多因子评分历史记录"""
    query = db.query(MultiFactorScore)
    
    # 应用筛选条件
    if strategy_id:
        query = query.filter(MultiFactorScore.strategy_id == strategy_id)
    if market_regime:
        query = query.filter(MultiFactorScore.market_regime == market_regime)
    if start_date:
        query = query.filter(MultiFactorScore.signal_date >= start_date)
    if end_date:
        query = query.filter(MultiFactorScore.signal_date <= end_date)
    
    # 排序并分页
    scores = query.order_by(MultiFactorScore.signal_date.desc()).offset(offset).limit(limit).all()
    
    # 转换为响应格式
    result = []
    for score in scores:
        # 转换股票评分列表
        stock_scores_list = []
        for stock_data in score.stock_scores:
            stock_scores_list.append(StockScore(
                symbol=stock_data["symbol"],
                name=stock_data["name"],
                total_score=stock_data["total_score"],
                factor_contribution=stock_data["factor_contribution"],
                rank=stock_data["rank"]
            ))
        
        result.append(MultiFactorResponse(
            stock_scores=stock_scores_list,
            adjusted_weights=score.adjusted_weights,
            discovered_factors=score.discovered_factors,
            reasoning=score.reasoning,
            signal_date=score.signal_date
        ))
    
    return result


@router.get("/multi_factor_scores/{score_id}", response_model=MultiFactorResponse)
def get_multi_factor_score(
    score_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个多因子评分"""
    score = db.query(MultiFactorScore).filter(MultiFactorScore.id == score_id).first()
    if not score:
        raise HTTPException(status_code=404, detail="评分不存在")
    
    # 转换股票评分列表
    stock_scores_list = []
    for stock_data in score.stock_scores:
        stock_scores_list.append(StockScore(
            symbol=stock_data["symbol"],
            name=stock_data["name"],
            total_score=stock_data["total_score"],
            factor_contribution=stock_data["factor_contribution"],
            rank=stock_data["rank"]
        ))
    
    return MultiFactorResponse(
        stock_scores=stock_scores_list,
        adjusted_weights=score.adjusted_weights,
        discovered_factors=score.discovered_factors,
        reasoning=score.reasoning,
        signal_date=score.signal_date
    ) 