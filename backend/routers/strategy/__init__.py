"""
AI投资策略引擎路由包
提供策略管理、信号生成、回测分析等功能
"""
from fastapi import APIRouter

from .base import router as base_router
from .macro_timing import router as macro_timing_router
from .sector_rotation import router as sector_rotation_router
from .multi_factor import router as multi_factor_router
from .signal import router as signal_router
from .backtest import router as backtest_router
from .allocation import router as allocation_router
from .factor_model import router as factor_model_router
from .market_regime import router as market_regime_router

# 创建主路由器
router = APIRouter(prefix="/strategy", tags=["AI投资策略引擎"])

# 注册所有子模块的路由器
router.include_router(base_router, prefix="")
router.include_router(macro_timing_router, prefix="")
router.include_router(sector_rotation_router, prefix="")
router.include_router(multi_factor_router, prefix="")
router.include_router(signal_router, prefix="")
router.include_router(backtest_router, prefix="")
router.include_router(allocation_router, prefix="")
router.include_router(factor_model_router, prefix="")
router.include_router(market_regime_router, prefix="")

__all__ = [
    "router",
    "base_router",
    "macro_timing_router", 
    "sector_rotation_router",
    "multi_factor_router",
    "signal_router",
    "backtest_router",
    "allocation_router",
    "factor_model_router",
    "market_regime_router"
] 