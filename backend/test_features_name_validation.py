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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_features_name_validation.db"
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
    if os.path.exists("test_features_name_validation.db"):
        os.remove("test_features_name_validation.db")

@pytest.fixture(scope="function")
def client(setup_database):
    # 确保数据库表已创建后再初始化 TestClient
    with TestClient(app) as c:
        yield c

def test_valid_name_chinese(client):
    """测试有效的中文名称"""
    feature_data = {
        "name": "测试特征",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "中文特征名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["name"] == "测试特征"
    print("中文名称验证通过")

def test_valid_name_english(client):
    """测试有效的英文名称"""
    feature_data = {
        "name": "TestFeature",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "英文特征名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["name"] == "TestFeature"
    print("英文名称验证通过")

def test_valid_name_mixed(client):
    """测试有效的中英文混合名称"""
    feature_data = {
        "name": "测试Feature_123",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "中英文混合特征名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["name"] == "测试Feature_123"
    print("中英文混合名称验证通过")

def test_valid_name_with_underscore(client):
    """测试包含下划线的有效名称"""
    feature_data = {
        "name": "test_feature_name",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "下划线特征名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["name"] == "test_feature_name"
    print("下划线名称验证通过")

def test_valid_name_with_hyphen(client):
    """测试包含中划线的有效名称"""
    feature_data = {
        "name": "test-feature-name",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "中划线特征名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["name"] == "test-feature-name"
    print("中划线名称验证通过")

def test_invalid_name_empty(client):
    """测试空名称"""
    feature_data = {
        "name": "",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "空名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 422
    print("空名称验证失败（预期）")

def test_invalid_name_whitespace(client):
    """测试空白字符名称"""
    feature_data = {
        "name": "   ",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "空白字符名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 422
    print("空白字符名称验证失败（预期）")

def test_invalid_name_too_long(client):
    """测试过长名称"""
    long_name = "a" * 101  # 101个字符
    feature_data = {
        "name": long_name,
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "过长名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 422
    print("过长名称验证失败（预期）")

def test_invalid_name_special_characters(client):
    """测试包含特殊字符的名称"""
    invalid_names = [
        "test@feature",
        "test#feature",
        "test$feature",
        "test%feature",
        "test^feature",
        "test&feature",
        "test*feature",
        "test(feature)",
        "test[feature]",
        "test{feature}",
        "test|feature",
        "test\\feature",
        "test/feature",
        "test+feature",
        "test=feature",
        "test<feature>",
        "test?feature",
        "test!feature",
        "test~feature",
        "test`feature"
    ]
    
    for invalid_name in invalid_names:
        feature_data = {
            "name": invalid_name,
            "type": "数值",
            "version": "v1.0",
            "created_by": "测试用户",
            "status": "active",
            "description": "特殊字符名称测试",
            "lineage": "测试血缘"
        }
        
        resp = client.post("/features/", json=feature_data)
        assert resp.status_code == 422, f"名称 '{invalid_name}' 应该被拒绝"
    
    print("特殊字符名称验证失败（预期）")

def test_invalid_name_starts_with_digit(client):
    """测试以数字开头的名称"""
    feature_data = {
        "name": "123test",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "数字开头名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 422
    print("数字开头名称验证失败（预期）")

def test_invalid_name_ends_with_underscore(client):
    """测试以下划线结尾的名称"""
    feature_data = {
        "name": "test_",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "下划线结尾名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 422
    print("下划线结尾名称验证失败（预期）")

def test_invalid_name_ends_with_hyphen(client):
    """测试以中划线结尾的名称"""
    feature_data = {
        "name": "test-",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "中划线结尾名称测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 422
    print("中划线结尾名称验证失败（预期）")

def test_valid_name_update(client):
    """测试更新时的有效名称"""
    # 先创建一个特征
    feature_data = {
        "name": "原始特征",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "原始特征",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    feature_id = resp.json()["id"]
    
    # 更新为有效名称
    update_data = {
        "name": "更新后的特征"
    }
    
    resp = client.put(f"/features/{feature_id}", json=update_data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["name"] == "更新后的特征"
    print("更新时有效名称验证通过")

def test_invalid_name_update(client):
    """测试更新时的无效名称"""
    # 先创建一个特征
    feature_data = {
        "name": "原始特征",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "原始特征",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    feature_id = resp.json()["id"]
    
    # 更新为无效名称
    update_data = {
        "name": "无效@特征"
    }
    
    resp = client.put(f"/features/{feature_id}", json=update_data)
    assert resp.status_code == 422
    print("更新时无效名称验证失败（预期）")

def test_name_trimming(client):
    """测试名称自动去除首尾空格"""
    feature_data = {
        "name": "  测试特征  ",
        "type": "数值",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "名称去空格测试",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["name"] == "测试特征"  # 应该去除首尾空格
    print("名称去空格验证通过")

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 