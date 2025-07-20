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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_features.db"
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
    if os.path.exists("test_features.db"):
        os.remove("test_features.db")

@pytest.fixture(scope="function")
def client(setup_database):
    # 确保数据库表已创建后再初始化 TestClient
    with TestClient(app) as c:
        yield c

def create_test_features(client):
    """创建测试特征数据"""
    features_data = [
        {
            "name": "测试特征1",
            "type": "数值",
            "version": "v1.0",
            "created_by": "测试用户",
            "status": "active",
            "description": "第一个测试特征",
            "lineage": "测试血缘1"
        },
        {
            "name": "测试特征2",
            "type": "分类",
            "version": "v1.0",
            "created_by": "测试用户",
            "status": "active",
            "description": "第二个测试特征",
            "lineage": "测试血缘2"
        },
        {
            "name": "数值特征",
            "type": "数值",
            "version": "v2.0",
            "created_by": "开发用户",
            "status": "inactive",
            "description": "数值类型特征",
            "lineage": "数值血缘"
        },
        {
            "name": "分类特征",
            "type": "分类",
            "version": "v1.5",
            "created_by": "开发用户",
            "status": "active",
            "description": "分类类型特征",
            "lineage": "分类血缘"
        }
    ]
    
    created_features = []
    for feature_data in features_data:
        resp = client.post("/features/", json=feature_data)
        assert resp.status_code == 201
        created_features.append(resp.json())
    
    return created_features

def test_features_search_no_params(client):
    """测试无参数搜索（获取所有特征）"""
    # 创建测试数据
    features = create_test_features(client)
    
    # 测试无参数搜索
    resp = client.get("/features/")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 4
    print(f"无参数搜索: 获取到 {len(result_features)} 个特征")

def test_features_search_by_name(client):
    """测试按名称搜索"""
    # 创建测试数据
    features = create_test_features(client)
    
    # 测试名称模糊搜索
    resp = client.get("/features/?name=测试")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 2
    for feature in result_features:
        assert "测试" in feature["name"]
    print(f"名称搜索: 找到 {len(result_features)} 个包含'测试'的特征")
    
    # 测试精确名称搜索
    resp = client.get("/features/?name=测试特征1")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 1
    assert result_features[0]["name"] == "测试特征1"
    print(f"精确名称搜索: 找到 {len(result_features)} 个特征")

def test_features_search_by_type(client):
    """测试按类型搜索"""
    # 创建测试数据
    features = create_test_features(client)
    
    # 测试数值类型搜索
    resp = client.get("/features/?type=数值")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 2
    for feature in result_features:
        assert feature["type"] == "数值"
    print(f"数值类型搜索: 找到 {len(result_features)} 个数值特征")
    
    # 测试分类类型搜索
    resp = client.get("/features/?type=分类")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 2
    for feature in result_features:
        assert feature["type"] == "分类"
    print(f"分类类型搜索: 找到 {len(result_features)} 个分类特征")

def test_features_search_by_status(client):
    """测试按状态搜索"""
    # 创建测试数据
    features = create_test_features(client)
    
    # 测试活跃状态搜索
    resp = client.get("/features/?status=active")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 3
    for feature in result_features:
        assert feature["status"] == "active"
    print(f"活跃状态搜索: 找到 {len(result_features)} 个活跃特征")
    
    # 测试非活跃状态搜索
    resp = client.get("/features/?status=inactive")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 1
    for feature in result_features:
        assert feature["status"] == "inactive"
    print(f"非活跃状态搜索: 找到 {len(result_features)} 个非活跃特征")

def test_features_search_combined(client):
    """测试组合搜索"""
    # 创建测试数据
    features = create_test_features(client)
    
    # 测试类型和状态组合搜索
    resp = client.get("/features/?type=数值&status=active")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 1
    feature = result_features[0]
    assert feature["type"] == "数值"
    assert feature["status"] == "active"
    print(f"组合搜索: 找到 {len(result_features)} 个数值且活跃的特征")
    
    # 测试名称和类型组合搜索
    resp = client.get("/features/?name=特征&type=分类")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 2
    for feature in result_features:
        assert "特征" in feature["name"]
        assert feature["type"] == "分类"
    print(f"名称和类型组合搜索: 找到 {len(result_features)} 个特征")

def test_features_search_empty_result(client):
    """测试搜索无结果的情况"""
    # 创建测试数据
    features = create_test_features(client)
    
    # 测试不存在的名称
    resp = client.get("/features/?name=不存在的特征")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 0
    print("不存在的名称搜索: 返回空结果")
    
    # 测试不存在的类型
    resp = client.get("/features/?type=不存在的类型")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 0
    print("不存在的类型搜索: 返回空结果")
    
    # 测试不存在的状态
    resp = client.get("/features/?status=不存在的状态")
    assert resp.status_code == 200
    result_features = resp.json()
    assert len(result_features) == 0
    print("不存在的状态搜索: 返回空结果")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 