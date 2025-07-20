# 特征工程 API 文档

## 概述

特征工程平台是智能投资顾问系统的重要组成部分，用于管理和维护机器学习模型所需的特征数据。本文档记录了后端 API 的开发进度和功能实现。

## 开发任务记录

### 任务 1.1: 添加特征搜索功能 ✅

**完成时间**: 2024-07-19  
**状态**: 已完成

#### 功能描述
在 `GET /features/` 端点添加查询参数支持，实现按名称、类型、状态进行搜索。

#### 实现细节

**API 端点**:
```python
@router.get("/", response_model=List[FeatureResponse])
def get_features(
    name: Optional[str] = Query(None, description="特征名称搜索"),
    type: Optional[str] = Query(None, description="特征类型搜索"),
    status: Optional[str] = Query(None, description="特征状态搜索"),
    db: Session = Depends(get_db)
):
    """
    获取特征列表，支持按名称、类型、状态进行模糊搜索
    """
    query = db.query(Feature)
    
    # 按名称模糊搜索
    if name:
        query = query.filter(Feature.name.ilike(f"%{name}%"))
    
    # 按类型精确搜索
    if type:
        query = query.filter(Feature.type == type)
    
    # 按状态精确搜索
    if status:
        query = query.filter(Feature.status == status)
    
    return query.all()
```

#### 搜索功能特性

1. **名称模糊搜索**: 使用 `ilike` 进行模糊匹配，支持部分名称搜索
2. **类型精确搜索**: 按特征类型进行精确匹配
3. **状态精确搜索**: 按特征状态进行精确匹配
4. **组合搜索**: 支持多个条件同时使用
5. **向后兼容**: 无参数时返回所有特征

#### 使用示例

```bash
# 获取所有特征
GET /features/

# 按名称搜索
GET /features/?name=测试

# 按类型搜索
GET /features/?type=数值

# 按状态搜索
GET /features/?status=active

# 组合搜索
GET /features/?type=数值&status=active
```

#### 测试覆盖

创建了完整的测试套件 `test_features_search.py`，包含以下测试：

- `test_features_search_no_params`: 无参数搜索测试
- `test_features_search_by_name`: 名称搜索测试
- `test_features_search_by_type`: 类型搜索测试
- `test_features_search_by_status`: 状态搜索测试
- `test_features_search_combined`: 组合搜索测试
- `test_features_search_empty_result`: 空结果搜索测试

#### 技术实现

- **框架**: FastAPI + SQLAlchemy
- **数据库**: SQLite (测试环境)
- **测试**: pytest + TestClient
- **搜索算法**: SQLAlchemy ORM 查询构建

#### 文件变更

1. **backend/routers/features.py**: 添加搜索参数和查询逻辑
2. **backend/test_features_search.py**: 创建完整的测试套件

### 任务 1.2: 添加特征分页功能 ✅

**完成时间**: 2024-07-19  
**状态**: 已完成

#### 功能描述
在 `GET /features/` 端点添加分页参数，实现 limit/offset 分页，返回总数信息。

#### 实现细节

**分页响应模型**:
```python
class FeaturesResponse(BaseModel):
    """分页响应模型"""
    items: List[FeatureResponse]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool
```

**API 端点**:
```python
@router.get("/", response_model=FeaturesResponse)
def get_features(
    name: Optional[str] = Query(None, description="特征名称搜索"),
    type: Optional[str] = Query(None, description="特征类型搜索"),
    status: Optional[str] = Query(None, description="特征状态搜索"),
    limit: int = Query(10, ge=1, le=100, description="每页数量，默认10，最大100"),
    offset: int = Query(0, ge=0, description="偏移量，默认0"),
    db: Session = Depends(get_db)
):
    """
    获取特征列表，支持按名称、类型、状态进行模糊搜索，支持分页
    """
    # 构建基础查询
    query = db.query(Feature)
    
    # 应用搜索过滤
    if name:
        query = query.filter(Feature.name.ilike(f"%{name}%"))
    if type:
        query = query.filter(Feature.type == type)
    if status:
        query = query.filter(Feature.status == status)
    
    # 获取总数
    total = query.count()
    
    # 应用分页
    features = query.offset(offset).limit(limit).all()
    
    # 计算分页信息
    has_next = offset + limit < total
    has_prev = offset > 0
    
    return FeaturesResponse(
        items=features,
        total=total,
        limit=limit,
        offset=offset,
        has_next=has_next,
        has_prev=has_prev
    )
```

#### 分页功能特性

1. **默认分页**: limit=10, offset=0
2. **参数验证**: limit 范围 1-100, offset 必须 >= 0
3. **分页信息**: 返回总数、当前页信息、是否有下一页/上一页
4. **搜索兼容**: 分页与搜索功能完全兼容
5. **边界处理**: 正确处理 offset 超过总数的情况

#### 使用示例

```bash
# 默认分页（第1页，每页10条）
GET /features/

# 自定义每页数量
GET /features/?limit=5

# 指定偏移量
GET /features/?limit=5&offset=10

# 分页与搜索结合
GET /features/?name=测试&limit=3&offset=0
```

#### 响应格式

```json
{
  "items": [
    {
      "id": 1,
      "name": "测试特征1",
      "type": "数值",
      "version": "v1.0",
      "created_by": "用户1",
      "status": "active",
      "description": "测试描述",
      "lineage": "测试血缘",
      "created_at": "2024-07-19T10:00:00"
    }
  ],
  "total": 15,
  "limit": 10,
  "offset": 0,
  "has_next": true,
  "has_prev": false
}
```

#### 测试覆盖

创建了完整的测试套件 `test_features_pagination.py`，包含以下测试：

- `test_features_pagination_default`: 默认分页测试
- `test_features_pagination_custom_limit`: 自定义每页数量测试
- `test_features_pagination_offset`: 偏移量测试
- `test_features_pagination_last_page`: 最后一页测试
- `test_features_pagination_with_search`: 分页与搜索结合测试
- `test_features_pagination_edge_cases`: 边界情况测试
- `test_features_pagination_parameter_validation`: 参数验证测试
- `test_features_pagination_empty_result`: 空结果分页测试

#### 技术实现

- **分页算法**: SQLAlchemy offset/limit
- **总数计算**: query.count() 优化性能
- **参数验证**: FastAPI Query 参数验证
- **响应模型**: Pydantic 模型确保类型安全

#### 文件变更

1. **backend/routers/features.py**: 添加分页参数和响应模型
2. **backend/test_features_pagination.py**: 创建分页功能测试套件

### 任务 1.3: 添加特征排序功能 ✅

**完成时间**: 2024-07-19  
**状态**: 已完成

#### 功能描述
在 `GET /features/` 端点添加排序参数，支持按创建时间、名称、类型等字段排序。

#### 实现细节

**API 端点**:
```python
@router.get("/", response_model=FeaturesResponse)
def get_features(
    name: Optional[str] = Query(None, description="特征名称搜索"),
    type: Optional[str] = Query(None, description="特征类型搜索"),
    status: Optional[str] = Query(None, description="特征状态搜索"),
    limit: int = Query(10, ge=1, le=100, description="每页数量，默认10，最大100"),
    offset: int = Query(0, ge=0, description="偏移量，默认0"),
    sort_by: str = Query("created_at", description="排序字段：name, type, created_at, status"),
    sort_order: str = Query("desc", description="排序方向：asc, desc"),
    db: Session = Depends(get_db)
):
    """
    获取特征列表，支持按名称、类型、状态进行模糊搜索，支持分页和排序
    """
    # 构建基础查询
    query = db.query(Feature)
    
    # 应用搜索过滤
    if name:
        query = query.filter(Feature.name.ilike(f"%{name}%"))
    if type:
        query = query.filter(Feature.type == type)
    if status:
        query = query.filter(Feature.status == status)
    
    # 应用排序
    sort_field = getattr(Feature, sort_by, Feature.created_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_field))
    else:
        query = query.order_by(desc(sort_field))
    
    # 获取总数
    total = query.count()
    
    # 应用分页
    features = query.offset(offset).limit(limit).all()
    
    # 计算分页信息
    has_next = offset + limit < total
    has_prev = offset > 0
    
    # 将 SQLAlchemy 对象转换为 Pydantic 对象
    feature_responses = [FeatureResponse.model_validate(feature) for feature in features]
    
    return FeaturesResponse(
        items=feature_responses,
        total=total,
        limit=limit,
        offset=offset,
        has_next=has_next,
        has_prev=has_prev
    )
```

#### 排序功能特性

1. **支持字段**: name, type, created_at, status
2. **排序方向**: asc (升序), desc (降序)
3. **默认排序**: 按 created_at 降序（最新创建在前）
4. **容错处理**: 无效字段使用默认字段，无效方向使用降序
5. **大小写不敏感**: 排序方向参数大小写不敏感
6. **功能组合**: 排序与搜索、分页完全兼容

#### 使用示例

```bash
# 默认排序（按创建时间降序）
GET /features/

# 按名称升序排序
GET /features/?sort_by=name&sort_order=asc

# 按类型降序排序
GET /features/?sort_by=type&sort_order=desc

# 按状态升序排序
GET /features/?sort_by=status&sort_order=asc

# 排序与搜索结合
GET /features/?name=测试&sort_by=type&sort_order=desc

# 排序与分页结合
GET /features/?sort_by=name&sort_order=asc&limit=5&offset=0
```

#### 测试覆盖

创建了完整的测试套件 `test_features_sorting.py`，包含以下测试：

- `test_features_sort_by_name_asc`: 按名称升序排序测试
- `test_features_sort_by_name_desc`: 按名称降序排序测试
- `test_features_sort_by_type_asc`: 按类型升序排序测试
- `test_features_sort_by_type_desc`: 按类型降序排序测试
- `test_features_sort_by_status_asc`: 按状态升序排序测试
- `test_features_sort_by_status_desc`: 按状态降序排序测试
- `test_features_sort_by_created_at_default`: 默认按创建时间排序测试
- `test_features_sort_by_created_at_asc`: 按创建时间升序排序测试
- `test_features_sort_with_pagination`: 排序与分页结合测试
- `test_features_sort_with_search`: 排序与搜索结合测试
- `test_features_sort_invalid_field`: 无效排序字段测试
- `test_features_sort_invalid_order`: 无效排序方向测试
- `test_features_sort_case_insensitive`: 排序方向大小写不敏感测试

#### 技术实现

- **排序算法**: SQLAlchemy order_by + asc/desc
- **字段映射**: getattr() 动态获取字段，支持容错
- **参数验证**: FastAPI Query 参数自动验证
- **大小写处理**: lower() 方法处理排序方向

#### 文件变更

1. **backend/routers/features.py**: 添加排序参数和排序逻辑
2. **backend/test_features_sorting.py**: 创建排序功能测试套件

### 任务 2.1: 增强特征名称验证 ✅

**完成时间**: 2024-07-19  
**状态**: 已完成

#### 功能描述
在 Pydantic 模式中添加名称格式验证，支持中文、英文、数字，禁止特殊字符。

#### 实现细节

**验证规则**:
```python
@validator('name')
def validate_name(cls, v):
    """验证特征名称格式"""
    if not v or not v.strip():
        raise ValueError('特征名称不能为空')
    
    # 检查长度
    if len(v) < 1 or len(v) > 100:
        raise ValueError('特征名称长度必须在1-100字符之间')
    
    # 检查格式：只允许中文、英文、数字、下划线、中划线
    pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_-]+$'
    if not re.match(pattern, v):
        raise ValueError('特征名称只能包含中文、英文、数字、下划线(_)、中划线(-)')
    
    # 检查是否以数字开头
    if v[0].isdigit():
        raise ValueError('特征名称不能以数字开头')
    
    # 检查是否以特殊字符结尾
    if v.endswith('_') or v.endswith('-'):
        raise ValueError('特征名称不能以下划线或中划线结尾')
    
    return v.strip()
```

#### 验证规则特性

1. **字符支持**: 中文、英文、数字、下划线(_)、中划线(-)
2. **长度限制**: 1-100 字符
3. **格式限制**: 
   - 不能以数字开头
   - 不能以下划线或中划线结尾
   - 不能包含其他特殊字符
4. **自动处理**: 自动去除首尾空格
5. **更新兼容**: 更新时名称可选，但提供时需验证

#### 支持的名称格式

**有效名称**:
- `测试特征` (中文)
- `TestFeature` (英文)
- `测试Feature_123` (中英文混合)
- `test_feature_name` (下划线)
- `test-feature-name` (中划线)
- `Feature_123` (数字在中间)

**无效名称**:
- `` (空字符串)
- `   ` (空白字符)
- `123test` (以数字开头)
- `test_` (以下划线结尾)
- `test-` (以中划线结尾)
- `test@feature` (包含特殊字符)
- `test#feature` (包含特殊字符)

#### 使用示例

```bash
# 有效名称
POST /features/
{
  "name": "测试特征",
  "type": "数值",
  "version": "v1.0",
  "created_by": "用户"
}

# 无效名称（会返回422错误）
POST /features/
{
  "name": "test@feature",
  "type": "数值",
  "version": "v1.0",
  "created_by": "用户"
}
```

#### 测试覆盖

创建了完整的测试套件 `test_features_name_validation.py`，包含以下测试：

- `test_valid_name_chinese`: 中文名称验证
- `test_valid_name_english`: 英文名称验证
- `test_valid_name_mixed`: 中英文混合名称验证
- `test_valid_name_with_underscore`: 下划线名称验证
- `test_valid_name_with_hyphen`: 中划线名称验证
- `test_invalid_name_empty`: 空名称验证
- `test_invalid_name_whitespace`: 空白字符名称验证
- `test_invalid_name_too_long`: 过长名称验证
- `test_invalid_name_special_characters`: 特殊字符名称验证
- `test_invalid_name_starts_with_digit`: 数字开头名称验证
- `test_invalid_name_ends_with_underscore`: 下划线结尾名称验证
- `test_invalid_name_ends_with_hyphen`: 中划线结尾名称验证
- `test_valid_name_update`: 更新时有效名称验证
- `test_invalid_name_update`: 更新时无效名称验证
- `test_name_trimming`: 名称去空格验证

#### 技术实现

- **正则表达式**: 使用 `^[\u4e00-\u9fa5a-zA-Z0-9_-]+$` 匹配有效字符
- **Pydantic 验证器**: 使用 `@validator` 装饰器
- **错误处理**: 提供详细的错误信息
- **自动清理**: 自动去除首尾空格

#### 文件变更

1. **backend/schemas/features.py**: 添加名称验证规则
2. **backend/test_features_name_validation.py**: 创建名称验证测试套件

## 待完成任务

### 阶段二：数据验证增强

**任务 2.2: 添加特征版本格式验证**
- **开始**: 在 Pydantic 模式中添加版本号格式验证
- **结束**: 支持语义化版本号 (如 v1.0.0)
- **专注点**: 版本号格式验证

**任务 2.3: 添加特征类型枚举**
- **开始**: 定义特征类型的枚举值
- **结束**: 限制为预定义的类型（数值、分类、时序等）
- **专注点**: 枚举类型定义

## API 端点列表

### 基础 CRUD 操作

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/features/` | 获取特征列表（支持搜索、分页和排序） |
| POST | `/features/` | 创建新特征 |
| GET | `/features/{id}` | 获取单个特征详情 |
| PUT | `/features/{id}` | 更新特征信息 |
| DELETE | `/features/{id}` | 删除特征 |

### 查询参数

| 参数 | 类型 | 描述 | 示例 |
|------|------|------|------|
| name | string | 特征名称模糊搜索 | `?name=测试` |
| type | string | 特征类型精确搜索 | `?type=数值` |
| status | string | 特征状态精确搜索 | `?status=active` |
| limit | int | 每页数量（1-100） | `?limit=10` |
| offset | int | 偏移量（>=0） | `?offset=0` |
| sort_by | string | 排序字段 | `?sort_by=name` |
| sort_order | string | 排序方向 | `?sort_order=asc` |

## 数据模型

### Feature 模型

```python
class Feature(Base):
    __tablename__ = 'features'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)
    version = Column(String(20), nullable=False)
    created_by = Column(String(20), nullable=False)
    status = Column(String(20), default="active")
    description = Column(Text)
    lineage = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Pydantic 模式

```python
class FeatureBase(BaseModel):
    name: str
    type: str
    version: str
    created_by: str
    status: str = "active"
    description: Optional[str] = None
    lineage: Optional[str] = None

class FeatureCreate(FeatureBase):
    pass

class FeatureUpdate(BaseModel):
    name: Optional[str]
    type: Optional[str]
    version: Optional[str]
    created_by: Optional[str]
    status: Optional[str]
    description: Optional[str]
    lineage: Optional[str]

class FeatureResponse(FeatureBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class FeaturesResponse(BaseModel):
    """分页响应模型"""
    items: List[FeatureResponse]
    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool
```

## 运行测试

```bash
cd backend
# 搜索功能测试
python -m pytest test_features_search.py -v

# 分页功能测试
python -m pytest test_features_pagination.py -v

# 排序功能测试
python -m pytest test_features_sorting.py -v
```

## 注意事项

1. 所有 API 调用都需要 JWT 认证
2. 搜索、分页和排序功能向后兼容，不影响现有功能
3. 测试使用独立的测试数据库，不会影响生产数据
4. 搜索参数都是可选的，可以组合使用
5. 分页参数有合理的默认值和验证规则
6. 排序参数支持容错处理，无效值使用默认值
7. 所有功能可以完全组合使用，提供灵活的查询能力 