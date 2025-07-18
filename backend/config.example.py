"""
后端服务配置示例文件
使用方法：复制此文件为 config.py 并根据实际环境修改配置
"""

# 服务器设置
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# 数据库配置
DATABASE_CONFIG = {
    "url": "postgresql://user:password@localhost:5432/investment_advisor",
    "pool_size": 20,
    "max_overflow": 10
}

# 安全配置
SECRET_KEY = "your-secret-key-here"  # 生产环境请使用强随机密钥
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"

# 第三方API密钥
API_KEYS = {
    "wind": "your-wind-api-key",
    "tushare": "your-tushare-token"
}

# 日志配置
LOG_LEVEL = "INFO" 