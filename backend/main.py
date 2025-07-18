"""
主应用模块
FastAPI应用入口点
"""
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import users, auth  # 导入用户和认证路由
from routers import portfolios  # 导入投资组合路由
from routers import assets  # 导入资产路由
from routers import tags  # 导入标签路由
from routers import market_data  # 导入市场数据路由
from routers import strategy  # 导入策略引擎路由

# 创建FastAPI应用实例
app = FastAPI()

# 添加CORS中间件，允许前端跨域请求后端API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源的跨域请求，生产环境应限制为特定域名
    allow_credentials=True,  # 允许发送cookie等凭证信息
    allow_methods=["*"],  # 允许所有HTTP方法（GET、POST等）
    allow_headers=["*"],  # 允许所有HTTP请求头
)

# 包含路由
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(portfolios.router)
app.include_router(assets.router)
app.include_router(tags.router)
app.include_router(market_data.router)
app.include_router(strategy.router)

@app.get("/")
def read_root():
    """根路由：返回简单的欢迎信息"""
    return {"message": "Hello, World!"}

@app.get("/health")
def health_check():
    """健康检查接口：用于监控服务状态，返回ok表示服务正常运行"""
    return {"status": "ok"} 