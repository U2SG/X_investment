# StrategyPage 目录说明

本目录包含策略管理页面及相关弹窗组件，所有组件均为函数式React组件。

## 组件列表

- `index.jsx`：策略管理主页面，负责策略列表展示、增删改查、弹窗状态管理。
- `StrategyFormModal.jsx`：策略新增/编辑弹窗。
- `StrategyDetailModal.jsx`：策略详情弹窗，含信号、回测列表及相关弹窗。
- `BacktestDetailModal.jsx`：回测详情弹窗，含净值曲线和重试功能。
- `BacktestFormModal.jsx`：新增回测弹窗。
- `SignalDetailModal.jsx`：信号详情弹窗。
- `SignalEditModal.jsx`：信号编辑弹窗。
- `SignalAddModal.jsx`：新增信号弹窗。

## 用法说明

- 主页面通过 `import ... from './StrategyPage/xxx'` 引用各弹窗组件。
- 各弹窗组件均通过 props 传递所需数据和回调，详见每个文件顶部注释。
- 组件拆分便于维护、复用和单元测试。

## 维护建议

- 新增弹窗或子组件请放在本目录下，保持结构清晰。
- 组件props如有变更，请同步更新注释和本说明文档。 