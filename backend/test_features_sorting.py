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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_features_sorting.db"
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
    if os.path.exists("test_features_sorting.db"):
        os.remove("test_features_sorting.db")

@pytest.fixture(scope="function")
def client(setup_database):
    # 确保数据库表已创建后再初始化 TestClient
    with TestClient(app) as c:
        yield c

def create_test_features(client):
    """创建测试特征数据"""
    features_data = [
        {
            "name": "A特征",
            "type": "数值",
            "version": "v1.0",
            "created_by": "用户A",
            "status": "active",
            "description": "第一个特征",
            "lineage": "血缘A"
        },
        {
            "name": "C特征",
            "type": "分类",
            "version": "v2.0",
            "created_by": "用户C",
            "status": "inactive",
            "description": "第三个特征",
            "lineage": "血缘C"
        },
        {
            "name": "B特征",
            "type": "数值",
            "version": "v1.5",
            "created_by": "用户B",
            "status": "active",
            "description": "第二个特征",
            "lineage": "血缘B"
        }
    ]
    
    created_features = []
    for feature_data in features_data:
        resp = client.post("/features/", json=feature_data)
        assert resp.status_code == 201
        created_features.append(resp.json())
    
    return created_features

def test_features_sort_by_name_asc(client):
    """测试按名称升序排序"""
    features = create_test_features(client)
    
    resp = client.get("/features/?sort_by=name&sort_order=asc")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证按名称升序排序
    names = [feature["name"] for feature in result["items"]]
    assert names == ["A特征", "B特征", "C特征"]
    print(f"按名称升序排序: {names}")

def test_features_sort_by_name_desc(client):
    """测试按名称降序排序"""
    features = create_test_features(client)
    
    resp = client.get("/features/?sort_by=name&sort_order=desc")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证按名称降序排序
    names = [feature["name"] for feature in result["items"]]
    assert names == ["C特征", "B特征", "A特征"]
    print(f"按名称降序排序: {names}")

def test_features_sort_by_type_asc(client):
    """测试按类型升序排序"""
    features = create_test_features(client)
    
    resp = client.get("/features/?sort_by=type&sort_order=asc")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证按类型升序排序
    types = [feature["type"] for feature in result["items"]]
    assert types == ["分类", "数值", "数值"]
    print(f"按类型升序排序: {types}")

def test_features_sort_by_type_desc(client):
    """测试按类型降序排序"""
    features = create_test_features(client)
    
    resp = client.get("/features/?sort_by=type&sort_order=desc")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证按类型降序排序
    types = [feature["type"] for feature in result["items"]]
    assert types == ["数值", "数值", "分类"]
    print(f"按类型降序排序: {types}")

def test_features_sort_by_status_asc(client):
    """测试按状态升序排序"""
    features = create_test_features(client)
    
    resp = client.get("/features/?sort_by=status&sort_order=asc")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证按状态升序排序
    statuses = [feature["status"] for feature in result["items"]]
    assert statuses == ["active", "active", "inactive"]
    print(f"按状态升序排序: {statuses}")

def test_features_sort_by_status_desc(client):
    """测试按状态降序排序"""
    features = create_test_features(client)
    
    resp = client.get("/features/?sort_by=status&sort_order=desc")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证按状态降序排序
    statuses = [feature["status"] for feature in result["items"]]
    assert statuses == ["inactive", "active", "active"]
    print(f"按状态降序排序: {statuses}")

def test_features_sort_by_created_at_default(client):
    """测试默认按创建时间降序排序"""
    features = create_test_features(client)
    
    resp = client.get("/features/")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证默认按创建时间降序排序（最新创建的在前面）
    assert len(result["items"]) == 3
    print(f"默认按创建时间降序排序: 返回 {len(result['items'])} 个特征")

def test_features_sort_by_created_at_asc(client):
    """测试按创建时间升序排序"""
    features = create_test_features(client)
    
    resp = client.get("/features/?sort_by=created_at&sort_order=asc")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证按创建时间升序排序（最早创建的在前面）
    assert len(result["items"]) == 3
    print(f"按创建时间升序排序: 返回 {len(result['items'])} 个特征")

def test_features_sort_with_pagination(client):
    """测试排序与分页结合"""
    features = create_test_features(client)
    
    resp = client.get("/features/?sort_by=name&sort_order=asc&limit=2&offset=0")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证排序和分页结合
    names = [feature["name"] for feature in result["items"]]
    assert names == ["A特征", "B特征"]
    assert result["total"] == 3
    assert result["limit"] == 2
    assert result["offset"] == 0
    print(f"排序与分页结合: {names}")

def test_features_sort_with_search(client):
    """测试排序与搜索结合"""
    features = create_test_features(client)
    
    resp = client.get("/features/?name=特征&sort_by=type&sort_order=desc")
    assert resp.status_code == 200
    result = resp.json()
    
    # 验证排序和搜索结合
    types = [feature["type"] for feature in result["items"]]
    assert types == ["数值", "数值", "分类"]
    print(f"排序与搜索结合: {types}")

def test_features_sort_invalid_field(client):
    """测试无效排序字段"""
    features = create_test_features(client)
    
    # 测试无效的排序字段，应该使用默认字段
    resp = client.get("/features/?sort_by=invalid_field&sort_order=asc")
    assert resp.status_code == 200
    result = resp.json()
    
    # 应该使用默认的 created_at 排序
    assert len(result["items"]) == 3
    print(f"无效排序字段: 使用默认排序，返回 {len(result['items'])} 个特征")

def test_features_sort_invalid_order(client):
    """测试无效排序方向"""
    features = create_test_features(client)
    
    # 测试无效的排序方向，应该使用默认方向
    resp = client.get("/features/?sort_by=name&sort_order=invalid")
    assert resp.status_code == 200
    result = resp.json()
    
    # 应该使用默认的降序排序
    names = [feature["name"] for feature in result["items"]]
    assert names == ["C特征", "B特征", "A特征"]
    print(f"无效排序方向: 使用默认降序，{names}")

def test_features_sort_case_insensitive(client):
    """测试排序方向大小写不敏感"""
    features = create_test_features(client)
    
    # 测试大写排序方向
    resp = client.get("/features/?sort_by=name&sort_order=ASC")
    assert resp.status_code == 200
    result = resp.json()
    
    names = [feature["name"] for feature in result["items"]]
    assert names == ["A特征", "B特征", "C特征"]
    print(f"大写排序方向: {names}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 