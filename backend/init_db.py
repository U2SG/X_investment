"""
数据库初始化脚本
用于创建所有定义的数据库表
"""
import logging
from database import engine
from models import Base, User

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """创建所有数据库表"""
    logger.info("正在创建数据库表...")
    
    # 使用Base.metadata.create_all()创建所有模型对应的表
    Base.metadata.create_all(bind=engine)
    
    logger.info("数据库表创建完成！")

if __name__ == "__main__":
    # 直接运行此脚本将初始化数据库
    logger.info("开始数据库初始化...")
    init_db()
    logger.info("数据库初始化完成！") 