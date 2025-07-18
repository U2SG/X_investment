import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import sessionmaker
from models import Base
from database import get_db
from sqlalchemy import create_engine
import os
from datetime import datetime, timezone

# 使用测试数据库（内存数据库，避免污染正式数据）
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 重写依赖，使用测试数据库
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    yield
    # 测试结束后清理
    Base.metadata.drop_all(bind=engine)
    engine.dispose()  # 关闭所有连接
    if os.path.exists("test.db"):
        os.remove("test.db")

@pytest.fixture(scope="module")
def client(setup_database):
    # 确保数据库表已创建后再初始化 TestClient
    with TestClient(app) as c:
        yield c

def register_and_login(client, username, password, email):
    reg_resp = client.post("/users/", json={
        "username": username,
        "password": password,
        "email": email
    })
    print("注册响应：", reg_resp.status_code, reg_resp.json())
    assert reg_resp.status_code in (200, 201), "注册失败"
    login_resp = client.post("/auth/token", data={
        "username": username,
        "password": password
    })
    print("登录响应：", login_resp.status_code, login_resp.json())
    assert login_resp.status_code == 200, "登录失败"
    token = login_resp.json().get("access_token")
    assert token, "未获取到token"
    return token

def test_portfolio_crud(client):
    # 注册并登录
    token = register_and_login(client, "user1", "password123", "user1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 创建投资组合
    resp = client.post("/portfolios/", json={
        "name": "测试组合",
        "description": "自动化测试",
        "risk_level": 3
    }, headers=headers)
    assert resp.status_code == 201
    portfolio_id = resp.json()["id"]

    # 查询自己所有投资组合
    resp = client.get("/portfolios/me", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    # 查询投资组合详情
    resp = client.get(f"/portfolios/{portfolio_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "测试组合"

    # 更新投资组合
    resp = client.put(f"/portfolios/{portfolio_id}", json={
        "name": "新组合名",
        "risk_level": 4
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "新组合名"
    assert resp.json()["risk_level"] == 4

    # 删除投资组合
    resp = client.delete(f"/portfolios/{portfolio_id}", headers=headers)
    assert resp.status_code == 200

    # 删除后再查详情应404
    resp = client.get(f"/portfolios/{portfolio_id}", headers=headers)
    assert resp.status_code == 404

def test_portfolio_permission(client):
    # 用户A
    token_a = register_and_login(client, "userA", "passA123", "a@example.com")
    headers_a = {"Authorization": f"Bearer {token_a}"}
    # 用户B
    token_b = register_and_login(client, "userB", "passB123", "b@example.com")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # A创建组合
    resp = client.post("/portfolios/", json={
        "name": "A的组合",
        "description": "",
        "risk_level": 2
    }, headers=headers_a)
    portfolio_id = resp.json()["id"]

    # B不能查A的组合详情
    resp = client.get(f"/portfolios/{portfolio_id}", headers=headers_b)
    assert resp.status_code == 404

    # B不能更新A的组合
    resp = client.put(f"/portfolios/{portfolio_id}", json={"name": "B试图改名"}, headers=headers_b)
    assert resp.status_code == 404

    # B不能删除A的组合
    resp = client.delete(f"/portfolios/{portfolio_id}", headers=headers_b)
    assert resp.status_code == 404

def test_portfolio_with_assets(client):
    # 注册并登录
    token = register_and_login(client, "user2", "password456", "user2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 创建两个资产
    resp = client.post("/assets/", json={
        "code": "600519",
        "name": "贵州茅台",
        "asset_type": "股票",
        "description": "中国高端白酒龙头"
    })
    assert resp.status_code == 201
    asset1_id = resp.json()["id"]

    resp = client.post("/assets/", json={
        "code": "510300",
        "name": "沪深300ETF",
        "asset_type": "基金",
        "description": "宽基ETF"
    })
    assert resp.status_code == 201
    asset2_id = resp.json()["id"]

    # 创建投资组合时指定资产及权重
    resp = client.post("/portfolios/", json={
        "name": "资产组合A",
        "description": "含两种资产",
        "risk_level": 3,
        "assets": [
            {"asset_id": asset1_id, "weight": 60.0},
            {"asset_id": asset2_id, "weight": 40.0}
        ]
    }, headers=headers)
    assert resp.status_code == 201
    portfolio_id = resp.json()["id"]

    # 查询投资组合详情，校验资产及权重
    resp = client.get(f"/portfolios/{portfolio_id}", headers=headers)
    assert resp.status_code == 200
    portfolio = resp.json()
    assert len(portfolio["portfolio_assets"]) == 2
    weights = {a["asset"]["code"]: a["weight"] for a in portfolio["portfolio_assets"]}
    assert weights["600519"] == 60.0
    assert weights["510300"] == 40.0

    # 更新投资组合资产及权重
    resp = client.put(f"/portfolios/{portfolio_id}/assets", json=[
        {"asset_id": asset1_id, "weight": 30.0},
        {"asset_id": asset2_id, "weight": 70.0}
    ], headers=headers)
    assert resp.status_code == 200

    # 再查详情，校验权重已更新
    resp = client.get(f"/portfolios/{portfolio_id}", headers=headers)
    assert resp.status_code == 200
    portfolio = resp.json()
    assert len(portfolio["portfolio_assets"]) == 2
    weights = {a["asset"]["code"]: a["weight"] for a in portfolio["portfolio_assets"]}
    assert weights["600519"] == 30.0
    assert weights["510300"] == 70.0