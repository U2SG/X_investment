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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_features_pagination.db"
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

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    # 每个测试函数都重新创建表
    Base.metadata.create_all(bind=engine)
    yield
    # 测试结束后清理
    Base.metadata.drop_all(bind=engine)
    engine.dispose()  # 关闭所有连接
    if os.path.exists("test_features_pagination.db"):
        os.remove("test_features_pagination.db")

@pytest.fixture(scope="function")
def client(setup_database):
    # 确保数据库表已创建后再初始化 TestClient
    with TestClient(app) as c:
        yield c

def create_test_features(client, count=15):
    """创建指定数量的测试特征数据"""
    features_data = []
    for i in range(count):
        feature_data = {
            "name": f"测试特征{i+1}",
            "type": "数值" if i % 2 == 0 else "分类",
            "version": f"v{i+1}.0",
            "created_by": f"用户{i+1}",
            "status": "active" if i % 3 != 0 else "inactive",
            "description": f"第{i+1}个测试特征",
            "lineage": f"血缘{i+1}"
        }
        features_data.append(feature_data)
    
    created_features = []
    for feature_data in features_data:
        resp = client.post("/features/", json=feature_data)
        assert resp.status_code == 201
        created_features.append(resp.json())
    
    return created_features

def test_features_pagination_default(client):
    """测试默认分页参数"""
    # 创建15个测试特征
    features = create_test_features(client, 15)
    
    # 测试默认分页（limit=10, offset=0）
    resp = client.get("/features/")
    assert resp.status_code == 200
    result = resp.json()
    
    assert result["total"] == 15
    assert result["limit"] == 10
    assert result["offset"] == 0
    assert len(result["items"]) == 10
    assert result["has_next"] == True
    assert result["has_prev"] == False
    print(f"默认分页: 总数={result['total']}, 当前页={len(result['items'])}, 有下一页={result['has_next']}")

def test_features_pagination_custom_limit(client):
    """测试自定义每页数量"""
    # 创建15个测试特征
    features = create_test_features(client, 15)
    
    # 测试自定义limit
    resp = client.get("/features/?limit=5")
    assert resp.status_code == 200
    result = resp.json()
    
    assert result["total"] == 15
    assert result["limit"] == 5
    assert result["offset"] == 0
    assert len(result["items"]) == 5
    assert result["has_next"] == True
    assert result["has_prev"] == False
    print(f"自定义limit=5: 总数={result['total']}, 当前页={len(result['items'])}, 有下一页={result['has_next']}")

def test_features_pagination_offset(client):
    """测试偏移量"""
    # 创建15个测试特征
    features = create_test_features(client, 15)
    
    # 测试offset=5
    resp = client.get("/features/?limit=5&offset=5")
    assert resp.status_code == 200
    result = resp.json()
    
    assert result["total"] == 15
    assert result["limit"] == 5
    assert result["offset"] == 5
    assert len(result["items"]) == 5
    assert result["has_next"] == True
    assert result["has_prev"] == True
    print(f"offset=5: 总数={result['total']}, 当前页={len(result['items'])}, 有下一页={result['has_next']}, 有上一页={result['has_prev']}")

def test_features_pagination_last_page(client):
    """测试最后一页"""
    # 创建15个测试特征
    features = create_test_features(client, 15)
    
    # 测试最后一页
    resp = client.get("/features/?limit=5&offset=10")
    assert resp.status_code == 200
    result = resp.json()
    
    assert result["total"] == 15
    assert result["limit"] == 5
    assert result["offset"] == 10
    assert len(result["items"]) == 5
    assert result["has_next"] == False
    assert result["has_prev"] == True
    print(f"最后一页: 总数={result['total']}, 当前页={len(result['items'])}, 有下一页={result['has_next']}, 有上一页={result['has_prev']}")

def test_features_pagination_with_search(client):
    """测试分页与搜索结合"""
    # 创建15个测试特征
    features = create_test_features(client, 15)
    
    # 测试搜索+分页
    resp = client.get("/features/?name=测试&limit=3&offset=0")
    assert resp.status_code == 200
    result = resp.json()
    
    assert result["total"] == 15  # 所有特征都包含"测试"
    assert result["limit"] == 3
    assert result["offset"] == 0
    assert len(result["items"]) == 3
    assert result["has_next"] == True
    assert result["has_prev"] == False
    
    # 验证返回的特征都包含"测试"
    for feature in result["items"]:
        assert "测试" in feature["name"]
    print(f"搜索+分页: 总数={result['total']}, 当前页={len(result['items'])}, 有下一页={result['has_next']}")

def test_features_pagination_edge_cases(client):
    """测试边界情况"""
    # 创建5个测试特征
    features = create_test_features(client, 5)
    
    # 测试limit超过总数
    resp = client.get("/features/?limit=20")
    assert resp.status_code == 200
    result = resp.json()
    assert result["total"] == 5
    assert len(result["items"]) == 5
    assert result["has_next"] == False
    print(f"limit超过总数: 总数={result['total']}, 返回={len(result['items'])}")
    
    # 测试offset超过总数
    resp = client.get("/features/?offset=10")
    assert resp.status_code == 200
    result = resp.json()
    assert result["total"] == 5
    assert len(result["items"]) == 0
    assert result["has_next"] == False
    assert result["has_prev"] == True
    print(f"offset超过总数: 总数={result['total']}, 返回={len(result['items'])}")

def test_features_pagination_parameter_validation(client):
    """测试参数验证"""
    # 测试limit最小值
    resp = client.get("/features/?limit=0")
    assert resp.status_code == 422  # 验证失败
    
    # 测试limit最大值
    resp = client.get("/features/?limit=101")
    assert resp.status_code == 422  # 验证失败
    
    # 测试offset最小值
    resp = client.get("/features/?offset=-1")
    assert resp.status_code == 422  # 验证失败
    
    # 测试有效参数
    resp = client.get("/features/?limit=50&offset=0")
    assert resp.status_code == 200
    print("参数验证测试通过")

def test_features_pagination_empty_result(client):
    """测试空结果的分页"""
    # 不创建任何特征
    
    # 测试空结果
    resp = client.get("/features/")
    assert resp.status_code == 200
    result = resp.json()
    
    assert result["total"] == 0
    assert result["limit"] == 10
    assert result["offset"] == 0
    assert len(result["items"]) == 0
    assert result["has_next"] == False
    assert result["has_prev"] == False
    print(f"空结果分页: 总数={result['total']}, 返回={len(result['items'])}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 