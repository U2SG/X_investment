# 策略路由模块拆分说明

## 概述

原来的 `routers/strategy.py` 文件过于庞大（1100+ 行），按照业务逻辑进行了模块化拆分，提升了代码的可维护性和可读性。

## 拆分结构

```
routers/strategy/
├── __init__.py              # 路由聚合器，导出主路由器
├── base.py                  # 策略基础管理
├── macro_timing.py          # 宏观择时模型
├── sector_rotation.py       # 行业轮动模型
├── multi_factor.py          # 多因子模型
├── signal.py                # 策略信号管理
├── backtest.py              # 回测管理
├── allocation.py            # 投资组合配置管理
├── factor_model.py          # 因子模型管理
└── market_regime.py         # 市场状态管理
```

## 模块功能说明

### 1. base.py - 策略基础管理
- 策略的增删改查
- 策略列表查询（支持筛选）
- 策略统计概览
- 单个策略详情

### 2. macro_timing.py - 宏观择时模型
- 宏观择时信号生成
- 历史信号查询
- 单个信号详情

### 3. sector_rotation.py - 行业轮动模型
- 行业轮动信号生成
- 历史信号查询
- 单个信号详情

### 4. multi_factor.py - 多因子模型
- 多因子信号生成
- 历史评分查询
- 单个评分详情

### 5. signal.py - 策略信号管理
- 策略信号的增删改查
- 信号列表查询（支持筛选）

### 6. backtest.py - 回测管理
- 回测结果的增删改查
- 回测结果列表查询

### 7. allocation.py - 投资组合配置管理
- 投资组合配置的增删改查
- 配置列表查询

### 8. factor_model.py - 因子模型管理
- 因子模型的增删改查
- 因子模型列表查询

### 9. market_regime.py - 市场状态管理
- 市场状态的增删改查
- 市场状态列表查询

## 路由聚合

在 `__init__.py` 中创建了主路由器，将所有子模块的路由器聚合在一起：

```python
router = APIRouter(prefix="/strategy", tags=["AI投资策略引擎"])

# 注册所有子模块的路由器
router.include_router(base_router, prefix="")
router.include_router(macro_timing_router, prefix="")
# ... 其他模块
```

## 接口路径保持不变

所有原有的API接口路径都保持不变，确保前端调用不受影响：

- `/strategy/` - 策略基础管理
- `/strategy/macro_timing_signal` - 宏观择时信号
- `/strategy/sector_rotation_signal` - 行业轮动信号
- `/strategy/multi_factor_signal` - 多因子信号
- `/strategy/signals` - 策略信号管理
- `/strategy/backtest` - 回测管理
- `/strategy/allocations` - 投资组合配置
- `/strategy/factors` - 因子模型管理
- `/strategy/regimes` - 市场状态管理

## 优势

1. **模块化**: 每个业务领域独立管理，职责清晰
2. **可维护性**: 代码分散到多个文件，便于维护和调试
3. **可扩展性**: 新增功能时只需修改对应模块
4. **可读性**: 代码结构更清晰，易于理解
5. **团队协作**: 不同开发者可以并行开发不同模块

## 注意事项

1. 所有子模块的 `prefix` 设置为空字符串，避免与主路由器的 `/strategy` 前缀重复
2. 每个模块都有独立的 `tags`，便于API文档分类
3. 原有的 `strategy.py` 文件保留，但内容已重构为路由聚合器
4. 所有功能保持不变，只是代码结构优化

## 测试

运行测试文件验证拆分是否成功：

```bash
cd backend
python test_strategy_split.py
```