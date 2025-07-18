"""
AI投资策略引擎测试
测试策略管理、信号生成、回测分析等功能
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json

from main import app
from database import get_db, Base
from models.user import User
from models.strategy import Strategy, StrategySignal, BacktestResult, PortfolioAllocation, FactorModel, MarketRegime
from models.market_data import MarketData
from utils.auth import create_access_token

# 创建测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_strategy.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建测试数据库表
Base.metadata.create_all(bind=engine)

def override_get_db():
    """覆盖数据库依赖"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# 创建测试客户端
client = TestClient(app)

# 测试用户数据
test_user_data = {
    "username": "test_strategy_user",
    "email": "strategy@test.com",
    "password": "testpassword123"
}

# 测试策略数据
test_strategy_data = {
    "name": "测试多因子策略",
    "description": "基于价值、动量、质量因子的多因子策略",
    "strategy_type": "MULTI_FACTOR",
    "asset_class": "STOCK",
    "parameters": {
        "value_weight": 0.4,
        "momentum_weight": 0.3,
        "quality_weight": 0.3,
        "rebalance_frequency": "monthly"
    },
    "risk_level": 3,
    "expected_return": 0.12,
    "max_drawdown": 0.15
}

# 测试市场数据
test_market_data = {
    "symbol": "000001.SZ",
    "name": "平安银行",
    "asset_type": "STOCK",
    "exchange": "SZSE",
    "currency": "CNY",
    "sector": "金融",
    "industry": "银行",
    "market_cap": 1000000000.0,
    "pe_ratio": 12.5,
    "pb_ratio": 1.2,
    "dividend_yield": 0.03
}

# 测试信号数据
test_signal_data = {
    "strategy_id": 1,
    "market_data_id": 1,
    "signal_type": "BUY",
    "signal_strength": 0.8,
    "target_weight": 0.05,
    "confidence_score": 0.75,
    "reasoning": "基于多因子模型，该股票在价值、动量、质量三个维度均表现良好",
    "factors": {
        "value_score": 0.8,
        "momentum_score": 0.7,
        "quality_score": 0.9
    },
    "signal_date": datetime.now().isoformat()
}

# 测试回测数据
test_backtest_data = {
    "strategy_id": 1,
    "start_date": (datetime.now() - timedelta(days=365)).isoformat(),
    "end_date": datetime.now().isoformat(),
    "initial_capital": 1000000.0,
    "total_return": 0.15,
    "annualized_return": 0.12,
    "volatility": 0.18,
    "sharpe_ratio": 0.67,
    "sortino_ratio": 0.85,
    "max_drawdown": 0.12,
    "calmar_ratio": 1.0,
    "var_95": 0.08,
    "cvar_95": 0.12,
    "beta": 0.95,
    "alpha": 0.03,
    "total_trades": 24,
    "winning_trades": 16,
    "losing_trades": 8,
    "win_rate": 0.67,
    "avg_win": 0.02,
    "avg_loss": 0.015,
    "profit_factor": 1.33,
    "performance_data": {
        "nav_curve": [1.0, 1.02, 1.05, 1.08, 1.12, 1.15],
        "drawdown_curve": [0.0, -0.01, -0.02, -0.01, 0.0, 0.0]
    },
    "trade_log": {
        "trades": [
            {"date": "2024-01-01", "action": "BUY", "symbol": "000001.SZ", "quantity": 1000, "price": 10.0},
            {"date": "2024-02-01", "action": "SELL", "symbol": "000001.SZ", "quantity": 1000, "price": 10.5}
        ],
        "summary": {
            "total_trades": 2,
            "total_volume": 2000,
            "total_value": 20500.0
        }
    },
    "factor_analysis": {
        "value_contribution": 0.04,
        "momentum_contribution": 0.06,
        "quality_contribution": 0.05
    }
}

# 测试因子模型数据
test_factor_model_data = {
    "name": "三因子模型",
    "description": "基于Fama-French三因子模型",
    "factors": ["market", "size", "value"],
    "factor_weights": {
        "market": 0.6,
        "size": 0.2,
        "value": 0.2
    },
    "model_parameters": {
        "lookback_period": 252,
        "rebalance_frequency": "monthly"
    }
}

# 测试市场状态数据
test_regime_data = {
    "regime_name": "牛市状态",
    "description": "市场处于上升趋势，风险偏好较高",
    "economic_cycle": "扩张",
    "market_sentiment": "乐观",
    "volatility_regime": "低波动",
    "regime_indicators": {
        "gdp_growth": 0.05,
        "inflation_rate": 0.02,
        "interest_rate": 0.03
    },
    "transition_probabilities": {
        "bull_to_bear": 0.2,
        "bull_to_sideways": 0.3,
        "bull_to_bull": 0.5
    },
    "start_date": datetime.now().isoformat(),
    "end_date": None
}

class TestStrategyEngine:
    """策略引擎测试类"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 清理数据库
        db = TestingSessionLocal()
        db.query(MarketRegime).delete()
        db.query(FactorModel).delete()
        db.query(BacktestResult).delete()
        db.query(StrategySignal).delete()
        db.query(PortfolioAllocation).delete()
        db.query(Strategy).delete()
        db.query(MarketData).delete()
        db.query(User).delete()
        db.commit()
        db.close()
        
        # 创建测试用户
        response = client.post("/users/", json=test_user_data)
        assert response.status_code == 201
        
        # 登录获取token
        login_response = client.post("/auth/token", data={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        })
        assert login_response.status_code == 200
        self.token = login_response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # 创建测试市场数据
        response = client.post("/market-data/", json=test_market_data, headers=self.headers)
        assert response.status_code == 201
        self.market_data_id = response.json()["id"]
        
        # 更新测试信号数据中的market_data_id
        test_signal_data["market_data_id"] = self.market_data_id
    
    def test_create_strategy(self):
        """测试创建策略"""
        response = client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == test_strategy_data["name"]
        assert data["strategy_type"] == test_strategy_data["strategy_type"]
        assert data["asset_class"] == test_strategy_data["asset_class"]
        assert data["risk_level"] == test_strategy_data["risk_level"]
        assert data["is_active"] == True
    
    def test_get_strategies(self):
        """测试获取策略列表"""
        # 创建策略
        client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        
        # 获取策略列表
        response = client.get("/strategy/", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == test_strategy_data["name"]
    
    def test_get_strategy_by_id(self):
        """测试根据ID获取策略"""
        # 创建策略
        create_response = client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        strategy_id = create_response.json()["id"]
        
        # 获取策略
        response = client.get(f"/strategy/{strategy_id}", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == strategy_id
        assert data["name"] == test_strategy_data["name"]
    
    def test_update_strategy(self):
        """测试更新策略"""
        # 创建策略
        create_response = client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        strategy_id = create_response.json()["id"]
        
        # 更新策略
        update_data = {
            "name": "更新后的策略名称",
            "description": "更新后的策略描述",
            "risk_level": 4
        }
        response = client.put(f"/strategy/{strategy_id}", json=update_data, headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
        assert data["risk_level"] == update_data["risk_level"]
    
    def test_delete_strategy(self):
        """测试删除策略"""
        # 创建策略
        create_response = client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        strategy_id = create_response.json()["id"]
        
        # 删除策略
        response = client.delete(f"/strategy/{strategy_id}", headers=self.headers)
        assert response.status_code == 204
        
        # 验证策略已被删除
        get_response = client.get(f"/strategy/{strategy_id}", headers=self.headers)
        assert get_response.status_code == 404
    
    def test_create_strategy_signal(self):
        """测试创建策略信号"""
        # 创建策略
        strategy_response = client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        strategy_id = strategy_response.json()["id"]
        
        # 更新信号数据
        signal_data = test_signal_data.copy()
        signal_data["strategy_id"] = strategy_id
        
        # 创建信号
        response = client.post("/strategy/signals", json=signal_data, headers=self.headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["strategy_id"] == strategy_id
        assert data["signal_type"] == signal_data["signal_type"]
        assert data["signal_strength"] == signal_data["signal_strength"]
    
    def test_get_strategy_signals(self):
        """测试获取策略信号列表"""
        # 创建策略和信号
        strategy_response = client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        strategy_id = strategy_response.json()["id"]
        
        signal_data = test_signal_data.copy()
        signal_data["strategy_id"] = strategy_id
        client.post("/strategy/signals", json=signal_data, headers=self.headers)
        
        # 获取信号列表
        response = client.get("/strategy/signals", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["strategy_id"] == strategy_id
    
    def test_create_backtest_result(self):
        """测试创建回测结果"""
        # 创建策略
        strategy_response = client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        strategy_id = strategy_response.json()["id"]
        
        # 更新回测数据
        backtest_data = test_backtest_data.copy()
        backtest_data["strategy_id"] = strategy_id
        
        # 创建回测结果
        response = client.post("/strategy/backtest", json=backtest_data, headers=self.headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["strategy_id"] == strategy_id
        assert data["total_return"] == backtest_data["total_return"]
        assert data["sharpe_ratio"] == backtest_data["sharpe_ratio"]
    
    def test_get_backtest_results(self):
        """测试获取回测结果列表"""
        # 创建策略和回测结果
        strategy_response = client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        strategy_id = strategy_response.json()["id"]
        
        backtest_data = test_backtest_data.copy()
        backtest_data["strategy_id"] = strategy_id
        client.post("/strategy/backtest", json=backtest_data, headers=self.headers)
        
        # 获取回测结果列表
        response = client.get("/strategy/backtest", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["strategy_id"] == strategy_id
    
    def test_create_factor_model(self):
        """测试创建因子模型"""
        response = client.post("/strategy/factors", json=test_factor_model_data, headers=self.headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == test_factor_model_data["name"]
        assert data["factors"] == test_factor_model_data["factors"]
        assert data["is_active"] == True
    
    def test_get_factor_models(self):
        """测试获取因子模型列表"""
        # 创建因子模型
        client.post("/strategy/factors", json=test_factor_model_data, headers=self.headers)
        
        # 获取因子模型列表
        response = client.get("/strategy/factors", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == test_factor_model_data["name"]
    
    def test_create_market_regime(self):
        """测试创建市场状态"""
        response = client.post("/strategy/regimes", json=test_regime_data, headers=self.headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["regime_name"] == test_regime_data["regime_name"]
        assert data["economic_cycle"] == test_regime_data["economic_cycle"]
        assert data["market_sentiment"] == test_regime_data["market_sentiment"]
    
    def test_get_market_regimes(self):
        """测试获取市场状态列表"""
        # 创建市场状态
        client.post("/strategy/regimes", json=test_regime_data, headers=self.headers)
        
        # 获取市场状态列表
        response = client.get("/strategy/regimes", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 1
        assert data[0]["regime_name"] == test_regime_data["regime_name"]
    
    def test_strategy_statistics(self):
        """测试策略统计信息"""
        # 创建测试数据
        client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        client.post("/strategy/factors", json=test_factor_model_data, headers=self.headers)
        
        # 获取统计信息
        response = client.get("/strategy/statistics/overview", headers=self.headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "strategies" in data
        assert "signals" in data
        assert "backtests" in data
        assert data["strategies"]["total"] == 1
        assert data["strategies"]["active"] == 1
    
    def test_strategy_filtering(self):
        """测试策略筛选功能"""
        # 创建不同类型的策略
        strategy1 = test_strategy_data.copy()
        strategy1["name"] = "股票策略"
        strategy1["strategy_type"] = "MULTI_FACTOR"
        strategy1["asset_class"] = "STOCK"
        
        strategy2 = test_strategy_data.copy()
        strategy2["name"] = "债券策略"
        strategy2["strategy_type"] = "MOMENTUM"
        strategy2["asset_class"] = "BOND"
        
        client.post("/strategy/", json=strategy1, headers=self.headers)
        client.post("/strategy/", json=strategy2, headers=self.headers)
        
        # 按策略类型筛选
        response = client.get("/strategy/?strategy_type=MULTI_FACTOR", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["strategy_type"] == "MULTI_FACTOR"
        
        # 按资产类别筛选
        response = client.get("/strategy/?asset_class=BOND", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["asset_class"] == "BOND"
    
    def test_signal_filtering(self):
        """测试信号筛选功能"""
        # 创建策略和信号
        strategy_response = client.post("/strategy/", json=test_strategy_data, headers=self.headers)
        strategy_id = strategy_response.json()["id"]
        
        signal_data = test_signal_data.copy()
        signal_data["strategy_id"] = strategy_id
        client.post("/strategy/signals", json=signal_data, headers=self.headers)
        
        # 按策略ID筛选
        response = client.get(f"/strategy/signals?strategy_id={strategy_id}", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["strategy_id"] == strategy_id
        
        # 按信号类型筛选
        response = client.get("/strategy/signals?signal_type=BUY", headers=self.headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["signal_type"] == "BUY"
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        # 不带token访问
        response = client.get("/strategy/")
        assert response.status_code == 401
        
        response = client.post("/strategy/", json=test_strategy_data)
        assert response.status_code == 401
    
    def test_invalid_strategy_id(self):
        """测试无效的策略ID"""
        response = client.get("/strategy/999", headers=self.headers)
        assert response.status_code == 404
        
        response = client.put("/strategy/999", json={"name": "test"}, headers=self.headers)
        assert response.status_code == 404
        
        response = client.delete("/strategy/999", headers=self.headers)
        assert response.status_code == 404
    
    def test_invalid_signal_id(self):
        """测试无效的信号ID"""
        response = client.get("/strategy/signals/999", headers=self.headers)
        assert response.status_code == 404
        
        response = client.put("/strategy/signals/999", json={"signal_type": "SELL"}, headers=self.headers)
        assert response.status_code == 404
        
        response = client.delete("/strategy/signals/999", headers=self.headers)
        assert response.status_code == 404
    
    def test_invalid_backtest_id(self):
        """测试无效的回测结果ID"""
        response = client.get("/strategy/backtest/999", headers=self.headers)
        assert response.status_code == 404
        
        response = client.put("/strategy/backtest/999", json={"total_return": 0.1}, headers=self.headers)
        assert response.status_code == 404
        
        response = client.delete("/strategy/backtest/999", headers=self.headers)
        assert response.status_code == 404
    
    def test_invalid_factor_model_id(self):
        """测试无效的因子模型ID"""
        response = client.get("/strategy/factors/999", headers=self.headers)
        assert response.status_code == 404
        
        response = client.put("/strategy/factors/999", json={"name": "test"}, headers=self.headers)
        assert response.status_code == 404
        
        response = client.delete("/strategy/factors/999", headers=self.headers)
        assert response.status_code == 404
    
    def test_invalid_regime_id(self):
        """测试无效的市场状态ID"""
        response = client.get("/strategy/regimes/999", headers=self.headers)
        assert response.status_code == 404
        
        response = client.put("/strategy/regimes/999", json={"regime_name": "test"}, headers=self.headers)
        assert response.status_code == 404
        
        response = client.delete("/strategy/regimes/999", headers=self.headers)
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 