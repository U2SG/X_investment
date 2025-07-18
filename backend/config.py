"""
后端服务配置文件
从环境变量加载配置，如未设置则使用默认值
"""
import os
import secrets
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()  # 自动加载 .env 文件到环境变量

# 服务器设置
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "True").lower() in ("true", "1", "t")

# 数据库配置
DATABASE_CONFIG = {
    "url": os.getenv("DATABASE_URL", "sqlite:///./investment_advisor.db"),  # 默认使用SQLite
    "pool_size": int(os.getenv("DATABASE_POOL_SIZE", "5")),
    "max_overflow": int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
}

# 安全配置
# 如果环境变量中没有设置SECRET_KEY，则生成一个随机密钥
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(32)
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
ALGORITHM = os.getenv("ALGORITHM", "HS256")

# 第三方API密钥
API_KEYS: Dict[str, Any] = {
    "wind": os.getenv("WIND_API_KEY", ""),
    "tushare": os.getenv("TUSHARE_TOKEN", "")
}

# 日志配置
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# 开发环境检查
if DEBUG and SECRET_KEY == secrets.token_hex(32):
    print("警告: 使用开发环境密钥，请勿在生产环境中使用！") 