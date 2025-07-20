import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import sessionmaker
from models import Base
from database import get_db
from sqlalchemy import create_engine
import os
from schemas.feature_types import FeatureType

# 使用测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_feature_types.db"
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
    if os.path.exists("test_feature_types.db"):
        os.remove("test_feature_types.db")

@pytest.fixture(scope="function")
def client(setup_database):
    with TestClient(app) as c:
        yield c

def test_feature_types_enum():
    """测试特征类型枚举"""
    # 测试所有类型
    all_types = FeatureType.get_all_types()
    assert len(all_types) > 0
    assert "数值型" in all_types
    assert "分类型" in all_types
    assert "文本型" in all_types
    assert "时间型" in all_types
    assert "复合型" in all_types
    
    # 测试数值型类型
    numerical_types = FeatureType.get_numerical_types()
    assert "数值型" in numerical_types
    assert "百分比" in numerical_types
    assert "比率" in numerical_types
    assert "指数" in numerical_types
    
    # 测试分类型类型
    categorical_types = FeatureType.get_categorical_types()
    assert "分类型" in categorical_types
    assert "二分类" in categorical_types
    assert "有序分类" in categorical_types
    
    # 测试文本型类型
    text_types = FeatureType.get_text_types()
    assert "文本型" in text_types
    assert "情感分析" in text_types
    assert "关键词" in text_types
    
    # 测试时间型类型
    temporal_types = FeatureType.get_temporal_types()
    assert "时间型" in temporal_types
    assert "日期" in temporal_types
    assert "时间戳" in temporal_types
    assert "持续时间" in temporal_types
    
    # 测试复合型类型
    composite_types = FeatureType.get_composite_types()
    assert "复合型" in composite_types
    assert "衍生型" in composite_types
    assert "聚合型" in composite_types

def test_feature_type_validation():
    """测试特征类型验证"""
    # 测试有效类型
    assert FeatureType.is_valid_type("数值型") == True
    assert FeatureType.is_valid_type("分类型") == True
    assert FeatureType.is_valid_type("文本型") == True
    assert FeatureType.is_valid_type("时间型") == True
    assert FeatureType.is_valid_type("复合型") == True
    
    # 测试无效类型
    assert FeatureType.is_valid_type("无效类型") == False
    assert FeatureType.is_valid_type("") == False
    assert FeatureType.is_valid_type(None) == False

def test_feature_type_categories():
    """测试特征类型分类"""
    # 测试数值型分类
    assert FeatureType.get_type_category("数值型") == "数值型"
    assert FeatureType.get_type_category("百分比") == "数值型"
    assert FeatureType.get_type_category("比率") == "数值型"
    assert FeatureType.get_type_category("指数") == "数值型"
    
    # 测试分类型分类
    assert FeatureType.get_type_category("分类型") == "分类型"
    assert FeatureType.get_type_category("二分类") == "分类型"
    assert FeatureType.get_type_category("有序分类") == "分类型"
    
    # 测试文本型分类
    assert FeatureType.get_type_category("文本型") == "文本型"
    assert FeatureType.get_type_category("情感分析") == "文本型"
    assert FeatureType.get_type_category("关键词") == "文本型"
    
    # 测试时间型分类
    assert FeatureType.get_type_category("时间型") == "时间型"
    assert FeatureType.get_type_category("日期") == "时间型"
    assert FeatureType.get_type_category("时间戳") == "时间型"
    assert FeatureType.get_type_category("持续时间") == "时间型"
    
    # 测试复合型分类
    assert FeatureType.get_type_category("复合型") == "复合型"
    assert FeatureType.get_type_category("衍生型") == "复合型"
    assert FeatureType.get_type_category("聚合型") == "复合型"
    
    # 测试未知类型
    assert FeatureType.get_type_category("未知类型") == "未知类型"

def test_get_feature_types_api(client):
    """测试获取特征类型 API"""
    resp = client.get("/features/types")
    assert resp.status_code == 200
    
    data = resp.json()
    assert "all_types" in data
    assert "numerical_types" in data
    assert "categorical_types" in data
    assert "text_types" in data
    assert "temporal_types" in data
    assert "composite_types" in data
    
    # 验证返回的数据
    assert len(data["all_types"]) > 0
    assert len(data["numerical_types"]) > 0
    assert len(data["categorical_types"]) > 0
    assert len(data["text_types"]) > 0
    assert len(data["temporal_types"]) > 0
    assert len(data["composite_types"]) > 0

def test_valid_feature_creation(client):
    """测试有效特征类型创建"""
    feature_data = {
        "name": "测试特征",
        "type": "数值型",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "测试描述",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    result = resp.json()
    assert result["type"] == "数值型"

def test_invalid_feature_creation(client):
    """测试无效特征类型创建"""
    feature_data = {
        "name": "测试特征",
        "type": "无效类型",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "测试描述",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 422
    error_detail = resp.json()
    assert "无效的特征类型" in error_detail["detail"][0]["msg"]

def test_feature_type_update(client):
    """测试特征类型更新"""
    # 先创建一个特征
    feature_data = {
        "name": "原始特征",
        "type": "数值型",
        "version": "v1.0",
        "created_by": "测试用户",
        "status": "active",
        "description": "原始特征",
        "lineage": "测试血缘"
    }
    
    resp = client.post("/features/", json=feature_data)
    assert resp.status_code == 201
    feature_id = resp.json()["id"]
    
    # 更新为有效类型
    update_data = {
        "type": "分类型"
    }
    
    resp = client.put(f"/features/{feature_id}", json=update_data)
    assert resp.status_code == 200
    result = resp.json()
    assert result["type"] == "分类型"
    
    # 更新为无效类型
    update_data = {
        "type": "无效类型"
    }
    
    resp = client.put(f"/features/{feature_id}", json=update_data)
    assert resp.status_code == 422
    error_detail = resp.json()
    assert "无效的特征类型" in error_detail["detail"][0]["msg"]

def test_all_feature_types_creation(client):
    """测试所有特征类型的创建"""
    valid_types = FeatureType.get_all_types()
    
    for feature_type in valid_types:
        feature_data = {
            "name": f"测试特征_{feature_type}",
            "type": feature_type,
            "version": "v1.0",
            "created_by": "测试用户",
            "status": "active",
            "description": f"测试{feature_type}特征",
            "lineage": "测试血缘"
        }
        
        resp = client.post("/features/", json=feature_data)
        assert resp.status_code == 201, f"类型 {feature_type} 创建失败"
        result = resp.json()
        assert result["type"] == feature_type

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 