import pytest
from fastapi.testclient import TestClient
from main import app
from sqlalchemy.orm import sessionmaker
from models import Base
from database import get_db
from sqlalchemy import create_engine
import os
from collections import defaultdict

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tags.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test_tags.db"):
        os.remove("test_tags.db")

@pytest.fixture(scope="module")
def client(setup_database):
    with TestClient(app) as c:
        yield c

def register_and_login(client, username, password, email=None):
    if email is None:
        email = f"{username}@example.com"
    # 注册
    resp = client.post("/users/", json={"username": username, "password": password, "email": email})
    assert resp.status_code == 201
    # 登录
    resp = client.post("/auth/token", data={"username": username, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return token

def test_batch_add_tags_to_assets(client):
    token = register_and_login(client, "autheduser1", "pass123")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建两个资产
    resp = client.post("/assets/", json={
        "code": "600001",
        "name": "资产A",
        "asset_type": "股票",
        "description": "测试资产A"
    })
    assert resp.status_code == 201
    asset1_id = resp.json()["id"]

    resp = client.post("/assets/", json={
        "code": "600002",
        "name": "资产B",
        "asset_type": "基金",
        "description": "测试资产B"
    })
    assert resp.status_code == 201
    asset2_id = resp.json()["id"]

    # 批量为资产添加标签
    resp = client.post("/assets/tags", json=[
        {"asset_id": asset1_id, "tags": ["热门", "科技"]},
        {"asset_id": asset2_id, "tags": ["热门", "蓝筹"]}
    ], headers=headers)
    assert resp.status_code == 200
    result = resp.json()
    assert any("热门" in r["tags"] for r in result)
    assert any("科技" in r["tags"] for r in result)
    assert any("蓝筹" in r["tags"] for r in result)

    # 查询资产A的标签
    resp = client.get(f"/assets/{asset1_id}/tags")
    assert resp.status_code == 200
    tags = resp.json()
    assert set(tags) == {"热门", "科技"}

    # 查询资产B的标签
    resp = client.get(f"/assets/{asset2_id}/tags")
    assert resp.status_code == 200
    tags = resp.json()
    assert set(tags) == {"热门", "蓝筹"}

    # 查询所有标签及其引用次数
    resp = client.get("/tags")
    assert resp.status_code == 200
    tags_info = {t["name"]: t["ref_count"] for t in resp.json()}
    assert tags_info["热门"] == 2
    assert tags_info["科技"] == 1
    assert tags_info["蓝筹"] == 1

    # 查询标签详情及其资产
    # 先查所有标签，拿到“热门”标签id
    resp = client.get("/tags")
    tag_obj = next((t for t in resp.json() if t["name"] == "热门"), None)
    assert tag_obj is not None
    tag_id = tag_obj["id"]
    resp = client.get(f"/tags/{tag_id}")
    assert resp.status_code == 200
    tag_detail = resp.json()
    asset_names = [a["name"] for a in tag_detail["assets"]]
    assert "资产A" in asset_names and "资产B" in asset_names

def test_batch_add_tags_requires_auth(client):
    # 不带token直接请求
    resp = client.post("/assets/tags", json=[{"asset_id": 1, "tags": ["科技"]}])
    assert resp.status_code == 401

def test_batch_remove_tags_from_assets(client):
    token = register_and_login(client, "autheduser2", "pass122")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建两个资产
    resp = client.post("/assets/", json={
        "code": "600101",
        "name": "资产C",
        "asset_type": "股票",
        "description": "测试资产C"
    })
    assert resp.status_code == 201
    asset1_id = resp.json()["id"]

    resp = client.post("/assets/", json={
        "code": "600102",
        "name": "资产D",
        "asset_type": "基金",
        "description": "测试资产D"
    })
    assert resp.status_code == 201
    asset2_id = resp.json()["id"]

    # 批量为资产添加标签
    resp = client.post("/assets/tags", json=[
        {"asset_id": asset1_id, "tags": ["热门", "科技", "蓝筹"]},
        {"asset_id": asset2_id, "tags": ["热门", "蓝筹"]}
    ], headers=headers)
    assert resp.status_code == 200

    # 批量移除标签
    resp = client.post("/assets/tags/remove", json=[
        {"asset_id": asset1_id, "tags": ["热门", "蓝筹"]},
        {"asset_id": asset2_id, "tags": ["蓝筹"]}
    ], headers=headers)
    assert resp.status_code == 200
    result = resp.json()
    # 资产C应只剩下“科技”标签
    asset1_tags = next(r["tags"] for r in result if r["asset_id"] == asset1_id)
    assert set(asset1_tags) == {"科技"}
    # 资产D应只剩下“热门”标签
    asset2_tags = next(r["tags"] for r in result if r["asset_id"] == asset2_id)
    assert set(asset2_tags) == {"热门"}

def test_remove_tag_auto_delete_if_unused(client):
    token = register_and_login(client, "autheduser3", "pass1233")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产并添加唯一标签
    resp = client.post("/assets/", json={
        "code": "600201",
        "name": "资产E",
        "asset_type": "股票",
        "description": "测试资产E"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]

    # 添加唯一标签“独有”
    resp = client.post(f"/assets/{asset_id}/tags", json=["独有"], headers=headers)
    assert resp.status_code == 200
    assert "独有" in resp.json()

    # 移除该标签
    resp = client.post("/assets/tags/remove", json=[{"asset_id": asset_id, "tags": ["独有"]}], headers=headers)
    assert resp.status_code == 200
    # 查询所有标签，"独有" 应不存在
    resp = client.get("/tags")
    tag_names = [t["name"] for t in resp.json()]
    assert "独有" not in tag_names

def test_batch_remove_tags_requires_auth(client):
    # 不带token直接请求
    resp = client.post("/assets/tags/remove", json=[{"asset_id": 1, "tags": ["科技"]}])
    assert resp.status_code == 401

def test_batch_add_and_remove_tags_with_auth(client):
    token = register_and_login(client, "taguser", "tagpass123")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产
    resp = client.post("/assets/", json={
        "code": "600301",
        "name": "资产F",
        "asset_type": "股票",
        "description": "测试资产F"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    # 批量添加标签
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["科技", "热门"]}], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert set(tags) == {"科技", "热门"}
    # 批量移除标签
    resp = client.post("/assets/tags/remove", json=[{"asset_id": asset_id, "tags": ["热门"]}], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert set(tags) == {"科技"}

def test_batch_add_tags_param_validation(client):
    token = register_and_login(client, "validuser1", "pass1111")
    headers = {"Authorization": f"Bearer {token}"}
    # asset_id 非正整数
    resp = client.post("/assets/tags", json=[{"asset_id": 0, "tags": ["科技"]}], headers=headers)
    assert resp.status_code == 400
    resp = client.post("/assets/tags", json=[{"asset_id": "abc", "tags": ["科技"]}], headers=headers)
    assert resp.status_code == 400
    # tags 非法
    resp = client.post("/assets/tags", json=[{"asset_id": 1, "tags": []}], headers=headers)
    assert resp.status_code == 400
    resp = client.post("/assets/tags", json=[{"asset_id": 1, "tags": [""]}], headers=headers)
    assert resp.status_code == 400
    resp = client.post("/assets/tags", json=[{"asset_id": 1, "tags": [123]}], headers=headers)
    assert resp.status_code == 400

def test_batch_remove_tags_param_validation(client):
    token = register_and_login(client, "validuser2", "pass1112")
    headers = {"Authorization": f"Bearer {token}"}
    # asset_id 非正整数
    resp = client.post("/assets/tags/remove", json=[{"asset_id": 0, "tags": ["科技"]}], headers=headers)
    assert resp.status_code == 400
    resp = client.post("/assets/tags/remove", json=[{"asset_id": "abc", "tags": ["科技"]}], headers=headers)
    assert resp.status_code == 400
    # tags 非法
    resp = client.post("/assets/tags/remove", json=[{"asset_id": 1, "tags": []}], headers=headers)
    assert resp.status_code == 400
    resp = client.post("/assets/tags/remove", json=[{"asset_id": 1, "tags": [""]}], headers=headers)
    assert resp.status_code == 400
    resp = client.post("/assets/tags/remove", json=[{"asset_id": 1, "tags": [123]}], headers=headers)
    assert resp.status_code == 400

def test_batch_add_tags_partial_invalid_asset(client):
    token = register_and_login(client, "partuser1", "pass1111")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建一个合法资产
    resp = client.post("/assets/", json={
        "code": "600401",
        "name": "资产G",
        "asset_type": "股票",
        "description": "测试资产G"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    # asset_id=99999 不存在
    resp = client.post("/assets/tags", json=[
        {"asset_id": asset_id, "tags": ["科技"]},
        {"asset_id": 99999, "tags": ["科技"]}
    ], headers=headers)
    assert resp.status_code == 200
    # 只返回合法资产结果
    assert any(r["asset_id"] == asset_id for r in resp.json())

def test_batch_remove_tags_partial_invalid_asset(client):
    token = register_and_login(client, "partuser2", "pass1232")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建一个合法资产并添加标签
    resp = client.post("/assets/", json={
        "code": "600402",
        "name": "资产H",
        "asset_type": "股票",
        "description": "测试资产H"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["科技"]}], headers=headers)
    assert resp.status_code == 200
    # asset_id=99999 不存在
    resp = client.post("/assets/tags/remove", json=[
        {"asset_id": asset_id, "tags": ["科技"]},
        {"asset_id": 99999, "tags": ["科技"]}
    ], headers=headers)
    assert resp.status_code == 200
    # 只返回合法资产结果
    assert any(r["asset_id"] == asset_id for r in resp.json())

def test_batch_add_tags_idempotent(client):
    token = register_and_login(client, "idemuser1", "pass1231")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产
    resp = client.post("/assets/", json={
        "code": "600501",
        "name": "资产I",
        "asset_type": "股票",
        "description": "测试资产I"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    # 同一资产多次出现，标签不同
    resp = client.post("/assets/tags", json=[
        {"asset_id": asset_id, "tags": ["A"]},
        {"asset_id": asset_id, "tags": ["B"]}
    ], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert set(tags) == {"A", "B"}

def test_batch_remove_tags_idempotent(client):
    token = register_and_login(client, "idemuser2", "pass1232")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产并添加标签
    resp = client.post("/assets/", json={
        "code": "600502",
        "name": "资产J",
        "asset_type": "股票",
        "description": "测试资产J"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["A", "B"]}], headers=headers)
    assert resp.status_code == 200
    # 同一资产多次出现，移除不同标签
    resp = client.post("/assets/tags/remove", json=[
        {"asset_id": asset_id, "tags": ["A"]},
        {"asset_id": asset_id, "tags": ["B"]}
    ], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert tags == []

def test_batch_add_tags_duplicate_tag_names(client):
    token = register_and_login(client, "duptaguser1", "pass1231")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产
    resp = client.post("/assets/", json={
        "code": "600601",
        "name": "资产K",
        "asset_type": "股票",
        "description": "测试资产K"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    # tags 列表中同一标签重复
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["A", "A", "B"]}], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert set(tags) == {"A", "B"}

def test_batch_remove_tags_duplicate_tag_names(client):
    token = register_and_login(client, "duptaguser2", "pass1232")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产并添加标签
    resp = client.post("/assets/", json={
        "code": "600602",
        "name": "资产L",
        "asset_type": "股票",
        "description": "测试资产L"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["A", "B"]}], headers=headers)
    assert resp.status_code == 200
    # tags 列表中同一标签重复移除
    resp = client.post("/assets/tags/remove", json=[{"asset_id": asset_id, "tags": ["A", "A", "B"]}], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert tags == []

def test_batch_add_tags_empty_request(client):
    token = register_and_login(client, "emptyuser3", "testpass3")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/assets/tags", json=[], headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []

def test_batch_remove_tags_empty_request(client):
    token = register_and_login(client, "emptyuser4", "testpass4")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/assets/tags/remove", json=[], headers=headers)
    assert resp.status_code == 200
    assert resp.json() == []

def test_shared_tag_ref_count_and_auto_delete(client):
    token = register_and_login(client, "shareduser", "pass1231")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建两个资产
    resp = client.post("/assets/", json={
        "code": "600701",
        "name": "资产M",
        "asset_type": "股票",
        "description": "测试资产M"
    })
    assert resp.status_code == 201
    asset1_id = resp.json()["id"]
    resp = client.post("/assets/", json={
        "code": "600702",
        "name": "资产N",
        "asset_type": "股票",
        "description": "测试资产N"
    })
    assert resp.status_code == 201
    asset2_id = resp.json()["id"]
    # 两个资产都添加同一标签“共享”
    resp = client.post("/assets/tags", json=[
        {"asset_id": asset1_id, "tags": ["共享"]},
        {"asset_id": asset2_id, "tags": ["共享"]}
    ], headers=headers)
    assert resp.status_code == 200
    # 查询标签引用次数
    resp = client.get("/tags")
    tag_info = next(t for t in resp.json() if t["name"] == "共享")
    assert tag_info["ref_count"] == 2
    tag_id = tag_info["id"]
    # 只移除资产M的“共享”标签
    resp = client.post("/assets/tags/remove", json=[{"asset_id": asset1_id, "tags": ["共享"]}], headers=headers)
    assert resp.status_code == 200
    # 标签应仍存在，引用次数为1
    resp = client.get("/tags")
    tag_info = next(t for t in resp.json() if t["name"] == "共享")
    assert tag_info["ref_count"] == 1
    # 再移除资产N的“共享”标签
    resp = client.post("/assets/tags/remove", json=[{"asset_id": asset2_id, "tags": ["共享"]}], headers=headers)
    assert resp.status_code == 200
    # 标签应被自动删除
    resp = client.get("/tags")
    tag_names = [t["name"] for t in resp.json()]
    assert "共享" not in tag_names

# 确保未登录用户访问时始终返回401，且响应内容包含标准认证错误信息
def test_batch_add_tags_requires_auth_detail(client):
    resp = client.post("/assets/tags", json=[{"asset_id": 1, "tags": ["科技"]}])
    assert resp.status_code == 401
    assert resp.json()["detail"] in ["未认证", "无效的认证凭证", "Not authenticated"]

def test_batch_remove_tags_requires_auth_detail(client):
    resp = client.post("/assets/tags/remove", json=[{"asset_id": 1, "tags": ["科技"]}])
    assert resp.status_code == 401
    assert resp.json()["detail"] in ["未认证", "无效的认证凭证", "Not authenticated"]

# 覆盖“批量操作时部分标签名不存在”的场景，确保不存在的标签不会影响其他标签的正常处理
def test_batch_add_tags_with_nonexistent_tag(client):
    token = register_and_login(client, "nonexuser1", "testpass1")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产
    resp = client.post("/assets/", json={
        "code": "601001",
        "name": "资产X",
        "asset_type": "股票",
        "description": "测试资产X"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    # 添加部分不存在的标签
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["新标签", "已存在"]}], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert set(tags) == {"新标签", "已存在"}


def test_batch_remove_tags_with_nonexistent_tag(client):
    token = register_and_login(client, "nonexuser2", "testpass2")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产并添加标签
    resp = client.post("/assets/", json={
        "code": "601002",
        "name": "资产Y",
        "asset_type": "股票",
        "description": "测试资产Y"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["A", "B"]}], headers=headers)
    assert resp.status_code == 200
    # 移除部分不存在的标签
    resp = client.post("/assets/tags/remove", json=[{"asset_id": asset_id, "tags": ["A", "不存在的标签"]}], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert tags == ["B"]

# 覆盖“批量操作时部分 asset_id 不存在”的场景，确保不存在的资产不会影响其他合法资产的正常处理
def test_batch_add_tags_with_nonexistent_asset(client):
    token = register_and_login(client, "nonexuser3", "testpass3")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建一个合法资产
    resp = client.post("/assets/", json={
        "code": "601003",
        "name": "资产Z",
        "asset_type": "股票",
        "description": "测试资产Z"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    # asset_id=99999 不存在
    resp = client.post("/assets/tags", json=[
        {"asset_id": asset_id, "tags": ["科技"]},
        {"asset_id": 99999, "tags": ["科技"]}
    ], headers=headers)
    assert resp.status_code == 200
    # 只返回合法资产结果
    assert any(r["asset_id"] == asset_id for r in resp.json())


def test_batch_remove_tags_with_nonexistent_asset(client):
    token = register_and_login(client, "nonexuser4", "testpass4")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建一个合法资产并添加标签
    resp = client.post("/assets/", json={
        "code": "601004",
        "name": "资产W",
        "asset_type": "股票",
        "description": "测试资产W"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["A"]}], headers=headers)
    assert resp.status_code == 200
    # asset_id=99999 不存在
    resp = client.post("/assets/tags/remove", json=[
        {"asset_id": asset_id, "tags": ["A"]},
        {"asset_id": 99999, "tags": ["A"]}
    ], headers=headers)
    assert resp.status_code == 200
    # 只返回合法资产结果
    assert any(r["asset_id"] == asset_id for r in resp.json())

# 覆盖“批量操作时 tags 列表中同一标签名重复出现”的幂等性场景，确保结果与去重后等价
def test_batch_add_tags_duplicate_tag_names_in_tags_list(client):
    token = register_and_login(client, "duptaguser3", "testpass3")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产
    resp = client.post("/assets/", json={
        "code": "601005",
        "name": "资产Q",
        "asset_type": "股票",
        "description": "测试资产Q"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    # tags 列表中同一标签重复
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["A", "A", "B"]}], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert set(tags) == {"A", "B"}


def test_batch_remove_tags_duplicate_tag_names_in_tags_list(client):
    token = register_and_login(client, "duptaguser4", "testpass4")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建资产并添加标签
    resp = client.post("/assets/", json={
        "code": "601006",
        "name": "资产R",
        "asset_type": "股票",
        "description": "测试资产R"
    })
    assert resp.status_code == 201
    asset_id = resp.json()["id"]
    resp = client.post("/assets/tags", json=[{"asset_id": asset_id, "tags": ["A", "B"]}], headers=headers)
    assert resp.status_code == 200
    # tags 列表中同一标签重复移除
    resp = client.post("/assets/tags/remove", json=[{"asset_id": asset_id, "tags": ["A", "A", "B"]}], headers=headers)
    assert resp.status_code == 200
    tags = next(r["tags"] for r in resp.json() if r["asset_id"] == asset_id)
    assert tags == []

# 覆盖“同一标签名在不同资产间共享时，移除后引用计数正确”的场景
def test_shared_tag_ref_count_and_auto_delete_v2(client):
    token = register_and_login(client, "shareduser2", "testpass5")
    headers = {"Authorization": f"Bearer {token}"}
    # 创建两个资产
    resp = client.post("/assets/", json={
        "code": "601007",
        "name": "资产M2",
        "asset_type": "股票",
        "description": "测试资产M2"
    })
    assert resp.status_code == 201
    asset1_id = resp.json()["id"]
    resp = client.post("/assets/", json={
        "code": "601008",
        "name": "资产N2",
        "asset_type": "股票",
        "description": "测试资产N2"
    })
    assert resp.status_code == 201
    asset2_id = resp.json()["id"]
    # 两个资产都添加同一标签“共享2”
    resp = client.post("/assets/tags", json=[
        {"asset_id": asset1_id, "tags": ["共享2"]},
        {"asset_id": asset2_id, "tags": ["共享2"]}
    ], headers=headers)
    assert resp.status_code == 200
    # 查询标签引用次数
    resp = client.get("/tags")
    tag_info = next(t for t in resp.json() if t["name"] == "共享2")
    assert tag_info["ref_count"] == 2
    tag_id = tag_info["id"]
    # 只移除资产M2的“共享2”标签
    resp = client.post("/assets/tags/remove", json=[{"asset_id": asset1_id, "tags": ["共享2"]}], headers=headers)
    assert resp.status_code == 200
    # 标签应仍存在，引用次数为1
    resp = client.get("/tags")
    tag_info = next(t for t in resp.json() if t["name"] == "共享2")
    assert tag_info["ref_count"] == 1
    # 再移除资产N2的“共享2”标签
    resp = client.post("/assets/tags/remove", json=[{"asset_id": asset2_id, "tags": ["共享2"]}], headers=headers)
    assert resp.status_code == 200
    # 标签应被自动删除
    resp = client.get("/tags")
    tag_names = [t["name"] for t in resp.json()]
    assert "共享2" not in tag_names
    
# 覆盖“批量操作时部分 tags 为空列表或全为空字符串”的非法输入场景，确保返回 400 错误
def test_batch_add_tags_invalid_tags_field(client):
    token = register_and_login(client, "invaliduser1", "testpass6")
    headers = {"Authorization": f"Bearer {token}"}
    # tags 为空列表
    resp = client.post("/assets/tags", json=[{"asset_id": 1, "tags": []}], headers=headers)
    assert resp.status_code == 400
    # tags 全为空字符串
    resp = client.post("/assets/tags", json=[{"asset_id": 1, "tags": [""]}], headers=headers)
    assert resp.status_code == 400


def test_batch_remove_tags_invalid_tags_field(client):
    token = register_and_login(client, "invaliduser2", "testpass7")
    headers = {"Authorization": f"Bearer {token}"}
    # tags 为空列表
    resp = client.post("/assets/tags/remove", json=[{"asset_id": 1, "tags": []}], headers=headers)
    assert resp.status_code == 400
    # tags 全为空字符串
    resp = client.post("/assets/tags/remove", json=[{"asset_id": 1, "tags": [""]}], headers=headers)
    assert resp.status_code == 400

