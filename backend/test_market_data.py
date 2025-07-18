"""
市场数据API测试
测试市场数据相关的所有API端点
"""
import pytest
import sys
import os
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from models.user import User
from models.market_data import MarketData, PriceHistory, MarketIndex, IndexHistory, AssetType

# 配置测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_market_data.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试数据库表
Base.metadata.create_all(bind=engine)

def override_get_db():
    """重写数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 测试数据
test_user_data = {
    "username": "testuser_market",
    "email": "test_market@example.com",
    "password": "testpassword123"
}

test_market_data = {
    "symbol": "000001.SZ",
    "name": "平安银行",
    "asset_type": "STOCK",
    "exchange": "SZSE",
    "currency": "CNY",
    "industry": "银行",
    "sector": "金融",
    "market_cap": 1000000000.0,
    "pe_ratio": 15.5,
    "pb_ratio": 1.2,
    "dividend_yield": 3.5
}

test_price_history = {
    "date": datetime.now().isoformat(),
    "open_price": 10.5,
    "high_price": 11.2,
    "low_price": 10.3,
    "close_price": 10.8,
    "adjusted_close": 10.8,
    "volume": 1000000,
    "turnover": 10800000,
    "ma5": 10.6,
    "ma10": 10.4,
    "ma20": 10.2,
    "ma60": 9.8
}

test_market_index = {
    "code": "000300.SH",
    "name": "沪深300指数",
    "description": "反映沪深两市300只股票的整体表现",
    "base_date": datetime(2005, 1, 1).isoformat(),
    "base_value": 1000.0,
    "is_active": True
}

class TestMarketDataAPI:
    """市场数据API测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 清理测试数据库
        db = TestingSessionLocal()
        db.query(IndexHistory).delete()
        db.query(PriceHistory).delete()
        db.query(MarketIndex).delete()
        db.query(MarketData).delete()
        db.query(User).delete()
        db.commit()
        db.close()
        
        # 创建测试用户
        response = client.post("/users/", json=test_user_data)
        assert response.status_code == 201
        self.user_data = response.json()
        
        # 登录获取token
        login_response = client.post("/auth/token", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    def test_create_market_data(self):
        """测试创建市场数据"""
        response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert response.status_code == 201
        data = response.json()
        assert data["symbol"] == test_market_data["symbol"]
        assert data["name"] == test_market_data["name"]
        assert data["asset_type"] == test_market_data["asset_type"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_market_data_duplicate_symbol(self):
        """测试创建重复证券代码的市场数据"""
        # 先创建一个
        response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert response.status_code == 201
        
        # 再创建相同代码的
        response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert response.status_code == 400
        assert "已存在" in response.json()["detail"]
    
    def test_get_market_data_list(self):
        """测试获取市场数据列表"""
        # 创建测试数据
        response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert response.status_code == 201
        
        # 获取列表
        response = client.get("/market-data/", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["symbol"] == test_market_data["symbol"]
    
    def test_get_market_data_list_with_filters(self):
        """测试带筛选条件的市场数据列表"""
        # 创建测试数据
        response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert response.status_code == 201
        
        # 按资产类型筛选
        response = client.get("/market-data/?asset_type=STOCK", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # 按交易所筛选
        response = client.get("/market-data/?exchange=SZSE", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # 按不存在的条件筛选
        response = client.get("/market-data/?asset_type=BOND", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_market_data_by_id(self):
        """测试根据ID获取市场数据"""
        # 创建测试数据
        create_response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert create_response.status_code == 201
        market_data_id = create_response.json()["id"]
        
        # 获取数据
        response = client.get(f"/market-data/{market_data_id}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == market_data_id
        assert data["symbol"] == test_market_data["symbol"]
    
    def test_get_market_data_not_found(self):
        """测试获取不存在的市场数据"""
        response = client.get("/market-data/999", headers=self.headers)
        assert response.status_code == 404
        assert "不存在" in response.json()["detail"]
    
    def test_update_market_data(self):
        """测试更新市场数据"""
        # 创建测试数据
        create_response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert create_response.status_code == 201
        market_data_id = create_response.json()["id"]
        
        # 更新数据
        update_data = {"name": "平安银行(更新)", "pe_ratio": 16.0}
        response = client.put(f"/market-data/{market_data_id}", json=update_data, headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "平安银行(更新)"
        assert data["pe_ratio"] == 16.0
        assert data["symbol"] == test_market_data["symbol"]  # 未更新的字段保持不变
    
    def test_delete_market_data(self):
        """测试删除市场数据"""
        # 创建测试数据
        create_response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert create_response.status_code == 201
        market_data_id = create_response.json()["id"]
        
        # 删除数据
        response = client.delete(f"/market-data/{market_data_id}", headers=self.headers)
        assert response.status_code == 204
        
        # 验证已删除
        get_response = client.get(f"/market-data/{market_data_id}", headers=self.headers)
        assert get_response.status_code == 404
    
    def test_create_price_history(self):
        """测试创建价格历史数据"""
        # 先创建市场数据
        market_response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert market_response.status_code == 201
        market_data_id = market_response.json()["id"]
        
        # 创建价格历史
        response = client.post(f"/market-data/{market_data_id}/price-history", 
                              json=test_price_history, headers=self.headers)
        assert response.status_code == 201
        data = response.json()
        assert data["market_data_id"] == market_data_id
        assert data["close_price"] == test_price_history["close_price"]
        assert "id" in data
    
    def test_get_price_history(self):
        """测试获取价格历史数据"""
        # 先创建市场数据和价格历史
        market_response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert market_response.status_code == 201
        market_data_id = market_response.json()["id"]
        
        client.post(f"/market-data/{market_data_id}/price-history", 
                   json=test_price_history, headers=self.headers)
        
        # 获取价格历史
        response = client.get(f"/market-data/{market_data_id}/price-history", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["market_data_id"] == market_data_id
    
    def test_create_market_index(self):
        """测试创建市场指数"""
        response = client.post("/market-data/indices", json=test_market_index, headers=self.headers)
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == test_market_index["code"]
        assert data["name"] == test_market_index["name"]
        assert "id" in data
        assert "created_at" in data
    
    def test_get_market_indices(self):
        """测试获取市场指数列表"""
        # 创建测试数据
        response = client.post("/market-data/indices", json=test_market_index, headers=self.headers)
        assert response.status_code == 201
        
        # 获取列表
        response = client.get("/market-data/indices", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["code"] == test_market_index["code"]
    
    def test_get_market_statistics(self):
        """测试获取市场数据统计信息"""
        # 创建一些测试数据
        client.post("/market-data/", json=test_market_data, headers=self.headers)
        client.post("/market-data/indices", json=test_market_index, headers=self.headers)
        
        # 获取统计信息
        response = client.get("/market-data/statistics/overview", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        
        assert "asset_type_statistics" in data
        assert "total_assets" in data
        assert "total_indices" in data
        assert data["total_assets"] == 1
        assert data["total_indices"] == 1
        assert data["asset_type_statistics"]["STOCK"] == 1
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        # 不带token访问
        response = client.get("/market-data/")
        assert response.status_code == 401
        
        response = client.post("/market-data/", json=test_market_data)
        assert response.status_code == 401


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"]) 