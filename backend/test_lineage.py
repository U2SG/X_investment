import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import sessionmaker
from models import Base
from database import get_db
from sqlalchemy import create_engine
import os

# 使用测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_lineage.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test_lineage.db"):
        os.remove("test_lineage.db")

@pytest.fixture(scope="function")
def client(setup_database):
    with TestClient(app) as c:
        yield c

def create_test_features(client):
    """创建测试特征"""
    features = []
    
    # 创建基础特征
    feature_data = {
        "name": "基础特征1",
        "type": "数值型",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "基础特征1",
        "lineage": "原始数据"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    features.append(resp.json())
    
    # 创建基础特征2
    feature_data = {
        "name": "基础特征2",
        "type": "数值型",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "基础特征2",
        "lineage": "原始数据"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    features.append(resp.json())
    
    return features

def test_create_lineage(client):
    """测试创建血缘关系"""
    # 创建测试特征
    features = create_test_features(client)
    
    # 创建血缘关系
    lineage_data = {
        "feature_id": features[1]["id"],
        "parent_feature_id": features[0]["id"],
        "lineage_type": "derived",
        "transformation_rule": "基础特征1 * 2",
        "data_source": "计算得出"
    }
    
    resp = client.post("/lineage/", json=lineage_data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["feature_id"] == features[1]["id"]
    assert result["parent_feature_id"] == features[0]["id"]
    assert result["lineage_type"] == "derived"

def test_create_self_dependency(client):
    """测试创建自依赖（应该失败）"""
    features = create_test_features(client)
    
    lineage_data = {
        "feature_id": features[0]["id"],
        "parent_feature_id": features[0]["id"],
        "lineage_type": "derived"
    }
    
    resp = client.post("/lineage/", json=lineage_data)
    assert resp.status_code == 400
    assert "不能依赖自己" in resp.json()["detail"]

def test_get_feature_lineages(client):
    """测试获取特征血缘关系"""
    features = create_test_features(client)
    
    # 创建血缘关系
    lineage_data = {
        "feature_id": features[1]["id"],
        "parent_feature_id": features[0]["id"],
        "lineage_type": "derived",
        "transformation_rule": "基础特征1 * 2"
    }
    
    resp = client.post("/lineage/", json=lineage_data)
    assert resp.status_code == 201
    
    # 获取血缘关系
    resp = client.get(f"/lineage/feature/{features[1]['id']}")
    assert resp.status_code == 200
    lineages = resp.json()
    assert len(lineages) == 1
    assert lineages[0]["parent_feature_id"] == features[0]["id"]

def test_get_feature_lineage_tree(client):
    """测试获取特征血缘树"""
    features = create_test_features(client)
    
    # 创建血缘关系
    lineage_data = {
        "feature_id": features[1]["id"],
        "parent_feature_id": features[0]["id"],
        "lineage_type": "derived",
        "transformation_rule": "基础特征1 * 2"
    }
    
    resp = client.post("/lineage/", json=lineage_data)
    assert resp.status_code == 201
    
    # 获取血缘树
    resp = client.get(f"/lineage/feature/{features[1]['id']}/tree")
    assert resp.status_code == 200
    tree = resp.json()
    assert tree["feature_id"] == features[1]["id"]
    assert tree["parent_id"] == features[0]["id"]
    assert tree["lineage_type"] == "derived"

def test_get_feature_lineage_graph(client):
    """测试获取特征血缘图"""
    features = create_test_features(client)
    
    # 创建血缘关系
    lineage_data = {
        "feature_id": features[1]["id"],
        "parent_feature_id": features[0]["id"],
        "lineage_type": "derived"
    }
    
    resp = client.post("/lineage/", json=lineage_data)
    assert resp.status_code == 201
    
    # 获取血缘图
    resp = client.get(f"/lineage/feature/{features[1]['id']}/graph")
    assert resp.status_code == 200
    graph = resp.json()
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert len(graph["root_nodes"]) == 1
    assert len(graph["leaf_nodes"]) == 1

def test_analyze_feature_lineage(client):
    """测试分析特征血缘关系"""
    features = create_test_features(client)
    
    # 创建血缘关系
    lineage_data = {
        "feature_id": features[1]["id"],
        "parent_feature_id": features[0]["id"],
        "lineage_type": "derived"
    }
    
    resp = client.post("/lineage/", json=lineage_data)
    assert resp.status_code == 201
    
    # 分析血缘关系
    resp = client.get(f"/lineage/feature/{features[1]['id']}/analysis")
    assert resp.status_code == 200
    analysis = resp.json()
    assert analysis["feature_id"] == features[1]["id"]
    assert analysis["dependency_count"] == 1
    assert analysis["dependent_count"] == 0
    assert analysis["max_depth"] == 1

def test_create_dependency(client):
    """测试创建依赖关系"""
    features = create_test_features(client)
    
    # 创建依赖关系
    dependency_data = {
        "dependent_id": features[1]["id"],
        "dependency_id": features[0]["id"],
        "dependency_type": "direct"
    }
    
    resp = client.post("/lineage/dependencies", json=dependency_data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["dependent_id"] == features[1]["id"]
    assert result["dependency_id"] == features[0]["id"]

def test_delete_dependency(client):
    """测试删除依赖关系"""
    features = create_test_features(client)
    
    # 创建依赖关系
    dependency_data = {
        "dependent_id": features[1]["id"],
        "dependency_id": features[0]["id"],
        "dependency_type": "direct"
    }
    
    resp = client.post("/lineage/dependencies", json=dependency_data)
    assert resp.status_code == 201
    
    # 删除依赖关系
    resp = client.delete(f"/lineage/dependencies/{features[1]['id']}/{features[0]['id']}")
    assert resp.status_code == 200
    assert "依赖关系已删除" in resp.json()["message"]

def test_complex_lineage_scenario(client):
    """测试复杂血缘关系场景"""
    # 创建多个特征
    features = []
    for i in range(3):
        feature_data = {
            "name": f"特征{i+1}",
            "type": "数值型",
            "version": "v1.0",
            "created_by": "测试用户",
            "status": "active",
            "description": f"特征{i+1}",
            "lineage": "原始数据"
        }
        
        resp = client.post("/features/", json=feature_data)
        assert resp.status_code == 201
        features.append(resp.json())
    
    # 创建血缘关系链：特征1 -> 特征2 -> 特征3
    lineage_data = {
        "feature_id": features[1]["id"],
        "parent_feature_id": features[0]["id"],
        "lineage_type": "derived",
        "transformation_rule": "特征1 * 2"
    }
    
    resp = client.post("/lineage/", json=lineage_data)
    assert resp.status_code == 201
    
    lineage_data = {
        "feature_id": features[2]["id"],
        "parent_feature_id": features[1]["id"],
        "lineage_type": "aggregated",
        "transformation_rule": "特征2 + 10"
    }
    
    resp = client.post("/lineage/", json=lineage_data)
    assert resp.status_code == 201
    
    # 分析最终特征的血缘关系
    resp = client.get(f"/lineage/feature/{features[2]['id']}/analysis")
    assert resp.status_code == 200
    analysis = resp.json()
    assert analysis["dependency_count"] == 1
    assert analysis["max_depth"] == 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 