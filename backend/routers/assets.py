"""
资产相关API路由
实现资产的添加和查询
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List
import sys
import os
import logging
from collections import defaultdict

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加父目录到Python路径
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from database import get_db
from models import Asset, PortfolioAsset, Tag
from schemas.portfolio import AssetCreate, AssetResponse, PortfolioAssetResponse, PortfolioResponse
from utils.auth import get_current_active_user
from models import User

router = APIRouter(
    prefix="/assets",
    tags=["assets"],
    responses={404: {"description": "未找到资产"}},
)

@router.post("/", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(asset_in: AssetCreate, db: Session = Depends(get_db)):
    """
    添加新资产。
    - 参数: asset_in (AssetCreate): 资产创建请求体
    - 返回: AssetResponse 新建资产详情
    - 异常: 资产代码已存在时返回400
    """
    # 检查资产代码唯一性
    db_asset = db.query(Asset).filter(Asset.code == asset_in.code).first()
    if db_asset:
        raise HTTPException(status_code=400, detail="资产代码已存在")
    asset = Asset(
        code=asset_in.code,
        name=asset_in.name,
        asset_type=asset_in.asset_type,
        description=asset_in.description
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset

@router.get("/", response_model=List[AssetResponse])
def get_assets(db: Session = Depends(get_db)):
    """
    查询所有资产
    """
    assets = db.query(Asset).all()
    return assets

@router.get("/me")
def get_assets_with_ref_count(db: Session = Depends(get_db)):
    """
    查询所有资产及其被投资组合引用次数
    """
    assets = db.query(Asset).all()
    result = []
    for asset in assets:
        ref_count = db.query(PortfolioAsset).filter(PortfolioAsset.asset_id == asset.id).count()
        asset_data = AssetResponse.from_orm(asset).dict()
        asset_data["ref_count"] = ref_count
        result.append(asset_data)
    return result

@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset_detail(asset_id: int, db: Session = Depends(get_db)):
    """
    查询单个资产详情
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    return asset

@router.get("/{asset_id}/portfolios", response_model=list[PortfolioAssetResponse])
def get_asset_portfolios(asset_id: int, db: Session = Depends(get_db)):
    """
    查询指定资产被哪些投资组合引用
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    portfolio_assets = db.query(PortfolioAsset).filter(PortfolioAsset.asset_id == asset_id).all()
    return portfolio_assets

@router.post("/{asset_id}/tags", response_model=list[str])
def add_tags_to_asset(asset_id: int, tags: list[str] = Body(..., description="标签名列表"), db: Session = Depends(get_db)):
    """
    为指定资产添加标签（自动创建新标签并关联）
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    tag_objs = []
    for tag_name in tags:
        tag = db.query(Tag).filter(Tag.name == tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        if tag not in asset.tags:
            asset.tags.append(tag)
        tag_objs.append(tag)
    db.commit()
    return [tag.name for tag in asset.tags]

@router.get("/{asset_id}/tags", response_model=list[str])
def get_asset_tags(asset_id: int, db: Session = Depends(get_db)):
    """
    查询指定资产的所有标签
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    return [tag.name for tag in asset.tags]

@router.delete("/{asset_id}", status_code=200)
def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """
    删除指定资产，若被投资组合引用则禁止删除
    """
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="资产不存在")
    # 检查是否被投资组合引用
    ref_count = db.query(PortfolioAsset).filter(PortfolioAsset.asset_id == asset_id).count()
    if ref_count > 0:
        raise HTTPException(status_code=400, detail="该资产已被投资组合引用，无法删除")
    db.delete(asset)
    db.commit()
    return {"detail": "删除成功"}

@router.post(
    "/tags",
    response_model=list[dict],
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": [
                        {"asset_id": 1, "tags": ["科技", "热门"]},
                        {"asset_id": 2, "tags": ["蓝筹"]},
                        {"asset_id": 1, "tags": ["蓝筹"]}
                    ]
                }
            }
        },
        "responses": {
            200: {
                "description": "批量添加标签后的资产标签列表",
                "content": {
                    "application/json": {
                        "example": [
                            {"asset_id": 1, "tags": ["科技", "热门", "蓝筹"]},
                            {"asset_id": 2, "tags": ["蓝筹"]}
                        ]
                    }
                }
            }
        }
    }
)
def batch_add_tags_to_assets(
    data: list[dict] = Body(default=[], min_items=0, description="资产ID与标签名列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    批量为多个资产添加标签（需登录）

    权限要求：已登录用户

    请求参数：
        data: List[dict]，每项格式：
            {
                "asset_id": int,         # 资产ID
                "tags": List[str]        # 要添加的标签名列表
            }
        允许同一资产多次出现，所有标签会自动合并去重。

    返回值：
        List[dict]，每项格式：
            {
                "asset_id": int,
                "tags": List[str]   # 该资产最新的全部标签
            }

    示例：
        POST /assets/tags
        Body: [
            {"asset_id": 1, "tags": ["科技", "热门"]},
            {"asset_id": 2, "tags": ["蓝筹"]},
            {"asset_id": 1, "tags": ["蓝筹"]}
        ]
        返回：[
            {"asset_id": 1, "tags": ["科技", "热门", "蓝筹"]},
            {"asset_id": 2, "tags": ["蓝筹"]}
        ]
    常见错误响应：
        400 参数校验失败: {"detail": "asset_id 必须为正整数"}
        400 参数校验失败: {"detail": "tags 必须为非空字符串列表"}
        500 数据库异常: {"detail": "数据库错误: ..."}

    安全建议：
        - 推荐为本接口集成速率限制（Rate Limiting），防止恶意批量操作。
        - 可用 Redis 实现分布式限流（如 slowapi、limits、或自定义令牌桶算法等）。
        - 典型限流策略：每用户每分钟不超过N次，超限返回429。
        - 严格使用ORM查询和参数化，防止SQL注入。
        - 所有批量操作均需权限校验，防止越权访问。
        - 建议对批量操作行为进行日志审计，便于追溯和风控。
        - 对标签名等输入字段进行长度和内容校验，防止恶意注入和XSS。

    幂等性说明：
        本接口为幂等操作：
        - 同一资产、同一标签多次添加不会导致重复关联。
        - 同一请求中同一资产多次出现、tags 列表中同一标签多次出现，系统会自动去重，结果与合并后等价。
        - 重复请求不会产生副作用。
    典型幂等性场景：
        - [{"asset_id": 1, "tags": ["A", "A", "B"]}, {"asset_id": 1, "tags": ["B"]}] 结果等价于 [{"asset_id": 1, "tags": ["A", "B"]}]

    接口变更建议/版本化说明：
        - 如需未来扩展批量操作更多字段（如批量设置标签颜色、描述等），建议将 tags 字段扩展为对象列表，如 tags: List[TagCreate]。
        - 若需API升级，推荐采用URL版本号（如 /v2/assets/tags），并保持向后兼容。
        - 变更需在docstring和OpenAPI文档中注明，便于前后端协作。

    国际化（i18n）设计建议：
        - 若需支持多语言错误信息，建议结合FastAPI的自定义异常处理和Accept-Language头，动态返回不同语言的错误内容。
        - 标签名等业务字段如需多语言展示，可在数据库中为标签增加多语言字段（如 name_en, name_zh），前端根据用户语言选择展示。
        - 推荐统一错误码和多语言消息映射，便于前后端协作和国际化维护。
    性能优化建议：
        - 如遇大批量操作或高并发场景，建议采用批量SQL（如 bulk_save_objects）、分批处理、异步任务队列（如Celery/RQ）等方式优化性能。
        - 可结合数据库索引优化标签/资产查询速度。
        - 对于极大批量操作，建议前端分批提交，后端异步处理并通知结果。
        - 监控慢查询和数据库锁，及时优化瓶颈。
    可测试性建议：
        - 推荐所有依赖（如数据库、用户认证）均通过FastAPI依赖注入，便于自动化测试时Mock。
        - 自动化测试应使用独立的测试数据库，测试前后清理数据，保证测试隔离。
        - 可通过覆盖 get_db/get_current_active_user 依赖，模拟不同用户和权限场景。
        - 建议为每个边界和异常场景编写自动化测试用例，提升代码健壮性。
    可观测性建议：
        - 推荐为本接口关键操作（如批量添加、异常、慢操作）记录结构化日志，便于追踪和分析。
        - 接口调用量、失败率、响应时间等应纳入监控体系（如Prometheus、Grafana、APM等）。
        - 重要异常和高延迟操作建议自动告警，便于及时响应。
        - 可结合trace_id、user_id等上下文信息，提升日志可追溯性。
    依赖关系说明：
        - 依赖数据库（如PostgreSQL、SQLite等）进行资产、标签、关联关系的持久化。
        - 依赖用户认证系统（如JWT、OAuth2）进行权限校验。
        - 可选依赖缓存服务（如Redis）用于限流、加速标签/资产查询。
        - 依赖FastAPI依赖注入机制（Depends）实现解耦和可测试性。
    团队协作与文档维护建议：
        - 每次接口变更（参数、行为、返回值等）需同步更新docstring和OpenAPI文档，保持文档与实现一致。
        - 代码评审时关注文档与实现的同步性，避免“文档漂移”。
        - 推荐使用自动化工具（如Swagger/OpenAPI生成、Sphinx等）生成和校验接口文档。
        - 鼓励团队成员在贡献新特性或修复bug时，补充/完善相关文档和注释。
        - 重要接口建议配套编写使用示例和FAQ，便于新成员快速上手。
    可扩展性建议：
        - 如需支持更多批量操作（如批量标签合并、批量标签转移、批量标签重命名等），建议采用操作类型参数（如 action: str）+参数对象的设计，或采用命令模式/插件机制实现批量操作扩展。
        - 推荐将批量操作逻辑解耦为独立服务或模块，便于后续维护和扩展。
        - 批量操作类型和参数建议在OpenAPI文档中详细说明，便于前后端协作。
    """
    try:
        if not data:
            return []
        # 合并同一资产的所有标签
        asset_tags_map = defaultdict(set)
        for item in data:
            asset_id = item.get("asset_id")
            tags = item.get("tags", [])
            # 参数校验
            if not isinstance(asset_id, int) or asset_id <= 0:
                raise HTTPException(status_code=400, detail="asset_id 必须为正整数")
            if not isinstance(tags, list) or not tags or not all(isinstance(t, str) and t.strip() for t in tags):
                raise HTTPException(status_code=400, detail="tags 必须为非空字符串列表")
            asset_tags_map[asset_id].update(tags)
        result = []
        for asset_id, tags in asset_tags_map.items():
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                continue
            for tag_name in tags:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                    db.commit()
                    db.refresh(tag)
                if tag not in asset.tags:
                    asset.tags.append(tag)
            db.commit()
            result.append({"asset_id": asset.id, "tags": [t.name for t in asset.tags]})
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}")

@router.post(
    "/tags/remove",
    response_model=list[dict],
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": [
                        {"asset_id": 1, "tags": ["科技", "热门"]},
                        {"asset_id": 2, "tags": ["蓝筹"]},
                        {"asset_id": 1, "tags": ["蓝筹"]}
                    ]
                }
            }
        },
        "responses": {
            200: {
                "description": "批量移除标签后的资产标签列表",
                "content": {
                    "application/json": {
                        "example": [
                            {"asset_id": 1, "tags": []},
                            {"asset_id": 2, "tags": []}
                        ]
                    }
                }
            }
        }
    }
)
def batch_remove_tags_from_assets(
    data: list[dict] = Body(default=[], min_items=0, description="资产ID与要移除的标签名列表"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    批量为多个资产移除标签，若标签未被任何资产引用则自动删除（需登录）

    权限要求：已登录用户

    请求参数：
        data: List[dict]，每项格式：
            {
                "asset_id": int,         # 资产ID
                "tags": List[str]        # 要移除的标签名列表
            }
        允许同一资产多次出现，所有标签会自动合并去重。

    返回值：
        List[dict]，每项格式：
            {
                "asset_id": int,
                "tags": List[str]   # 该资产最新的全部标签
            }
        若某标签被所有资产移除，则自动从系统中删除。

    示例：
        POST /assets/tags/remove
        Body: [
            {"asset_id": 1, "tags": ["科技", "热门"]},
            {"asset_id": 2, "tags": ["蓝筹"]},
            {"asset_id": 1, "tags": ["蓝筹"]}
        ]
        返回：[
            {"asset_id": 1, "tags": []},
            {"asset_id": 2, "tags": []}
        ]
    常见错误响应：
        400 参数校验失败: {"detail": "asset_id 必须为正整数"}
        400 参数校验失败: {"detail": "tags 必须为非空字符串列表"}
        500 数据库异常: {"detail": "数据库错误: ..."}

    安全建议：
        - 推荐为本接口集成速率限制（Rate Limiting），防止恶意批量操作。
        - 可用 Redis 实现分布式限流（如 slowapi、limits、或自定义令牌桶算法等）。
        - 典型限流策略：每用户每分钟不超过N次，超限返回429。
        - 严格使用ORM查询和参数化，防止SQL注入。
        - 所有批量操作均需权限校验，防止越权访问。
        - 建议对批量操作行为进行日志审计，便于追溯和风控。
        - 对标签名等输入字段进行长度和内容校验，防止恶意注入和XSS。

    幂等性说明：
        本接口为幂等操作：
        - 同一资产、同一标签多次移除不会导致异常。
        - 同一请求中同一资产多次出现、tags 列表中同一标签多次出现，系统会自动去重，结果与合并后等价。
        - 重复请求不会产生副作用。
    典型幂等性场景：
        - [{"asset_id": 1, "tags": ["A", "A", "B"]}, {"asset_id": 1, "tags": ["B"]}] 结果等价于 [{"asset_id": 1, "tags": ["A", "B"]}]

    接口变更建议/版本化说明：
        - 如需未来扩展批量操作更多字段（如批量移除标签的附加属性），建议将 tags 字段扩展为对象列表，如 tags: List[TagRemove]。
        - 若需API升级，推荐采用URL版本号（如 /v2/assets/tags/remove），并保持向后兼容。
        - 变更需在docstring和OpenAPI文档中注明，便于前后端协作。

    国际化（i18n）设计建议：
        - 若需支持多语言错误信息，建议结合FastAPI的自定义异常处理和Accept-Language头，动态返回不同语言的错误内容。
        - 标签名等业务字段如需多语言展示，可在数据库中为标签增加多语言字段（如 name_en, name_zh），前端根据用户语言选择展示。
        - 推荐统一错误码和多语言消息映射，便于前后端协作和国际化维护。
    性能优化方向：
        - 如遇大批量操作或高并发场景，建议采用批量SQL（如 bulk_save_objects）、分批处理、异步任务队列（如Celery/RQ）等方式优化性能。
        - 可结合数据库索引优化标签/资产查询速度。
        - 对于极大批量操作，采用前端分批提交，后端异步处理并通知结果。
        - 监控慢查询和数据库锁，及时优化瓶颈。
    可测试性建议：
        - 推荐所有依赖（如数据库、用户认证）均通过FastAPI依赖注入，便于自动化测试时Mock。
        - 自动化测试应使用独立的测试数据库，测试前后清理数据，保证测试隔离。
        - 可通过覆盖 get_db/get_current_active_user 依赖，模拟不同用户和权限场景。
        - 建议为每个边界和异常场景编写自动化测试用例，提升代码健壮性。
    可观测性建议：
        - 推荐为本接口关键操作（如批量移除、异常、慢操作）记录结构化日志，便于追踪和分析。
        - 接口调用量、失败率、响应时间等应纳入监控体系（如Prometheus、Grafana、APM等）。
        - 重要异常和高延迟操作建议自动告警，便于及时响应。
        - 可结合trace_id、user_id等上下文信息，提升日志可追溯性。
    依赖关系说明：
        - 依赖数据库（如PostgreSQL、SQLite等）进行资产、标签、关联关系的持久化。
        - 依赖用户认证系统（如JWT、OAuth2）进行权限校验。
        - 可选依赖缓存服务（如Redis）用于限流、加速标签/资产查询。
        - 依赖FastAPI依赖注入机制（Depends）实现解耦和可测试性。
    团队协作与文档维护建议：
        - 每次接口变更（参数、行为、返回值等）需同步更新docstring和OpenAPI文档，保持文档与实现一致。
        - 代码评审时关注文档与实现的同步性，避免“文档漂移”。
        - 推荐使用自动化工具（如Swagger/OpenAPI生成、Sphinx等）生成和校验接口文档。
        - 鼓励团队成员在贡献新特性或修复bug时，补充/完善相关文档和注释。
        - 重要接口建议配套编写使用示例和FAQ，便于新成员快速上手。
    可扩展性建议：
        - 如需支持更多批量操作（如批量标签合并、批量标签转移、批量标签重命名等），建议采用操作类型参数（如 action: str）+参数对象的设计，或采用命令模式/插件机制实现批量操作扩展。
        - 推荐将批量操作逻辑解耦为独立服务或模块，便于后续维护和扩展。
        - 批量操作类型和参数建议在OpenAPI文档中详细说明，便于前后端协作。
    """
    try:
        if not data:
            return []
        # 合并同一资产的所有标签
        asset_tags_map = defaultdict(set)
        for item in data:
            asset_id = item.get("asset_id")
            tags = item.get("tags", [])
            # 参数校验
            if not isinstance(asset_id, int) or asset_id <= 0:
                raise HTTPException(status_code=400, detail="asset_id 必须为正整数")
            if not isinstance(tags, list) or not tags or not all(isinstance(t, str) and t.strip() for t in tags):
                raise HTTPException(status_code=400, detail="tags 必须为非空字符串列表")
            asset_tags_map[asset_id].update(tags)
        result = []
        removed_tag_names = set()
        for asset_id, tags in asset_tags_map.items():
            asset = db.query(Asset).filter(Asset.id == asset_id).first()
            if not asset:
                continue
            for tag_name in tags:
                tag = db.query(Tag).filter(Tag.name == tag_name).first()
                if tag and tag in asset.tags:
                    asset.tags.remove(tag)
                    removed_tag_names.add(tag_name)
            db.commit()
            result.append({"asset_id": asset.id, "tags": [t.name for t in asset.tags]})
        # 清理未被任何资产引用的标签
        for tag_name in removed_tag_names:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if tag and len(tag.assets) == 0:
                db.delete(tag)
        db.commit()
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库错误: {str(e)}") 