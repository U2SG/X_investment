"""
批量生成资产脚本
"""
import random
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Asset

# 示例资产数据
asset_types = ["股票", "基金", "债券", "ETF"]
sample_assets = [
    {"code": f"60{random.randint(1000,9999)}", "name": f"测试股票{i}", "asset_type": "股票", "description": f"自动生成的股票{i}"} for i in range(1, 6)
] + [
    {"code": f"51{random.randint(1000,9999)}", "name": f"测试基金{i}", "asset_type": "基金", "description": f"自动生成的基金{i}"} for i in range(1, 6)
] + [
    {"code": f"11{random.randint(1000,9999)}", "name": f"测试债券{i}", "asset_type": "债券", "description": f"自动生成的债券{i}"} for i in range(1, 4)
] + [
    {"code": f"15{random.randint(1000,9999)}", "name": f"测试ETF{i}", "asset_type": "ETF", "description": f"自动生成的ETF{i}"} for i in range(1, 3)
]

def batch_create_assets():
    db: Session = SessionLocal()
    try:
        for asset in sample_assets:
            # 避免重复插入
            exists = db.query(Asset).filter(Asset.code == asset["code"]).first()
            if not exists:
                db.add(Asset(**asset))
        db.commit()
        print(f"已批量生成 {len(sample_assets)} 个资产。")
    finally:
        db.close()

if __name__ == "__main__":
    batch_create_assets()