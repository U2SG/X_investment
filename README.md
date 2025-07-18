# 智能投顾系统 (Smart Investment Advisor)

基于数据驱动和AI赋能的智能投顾平台，为基金公司及其客户提供高度个性化、动态、透明且合规的投资决策支持服务。

## 项目架构

本项目采用前后端分离架构：

- **前端**：React + Vite
- **后端**：FastAPI
- **基础设施**：Terraform

详细架构设计请参考 [architecture.md](architecture.md)。

## 快速开始

### 启动后端服务

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python -m uvicorn main:app --reload

# 访问API文档
# http://localhost:8000/docs
```

### 启动前端服务

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 访问前端页面
# http://localhost:5173
```

## 项目结构

```
/
├── backend/          # 后端服务代码
├── frontend/         # 前端应用代码
├── infrastructure/   # 基础设施即代码(IaC)
├── docs/             # 项目文档
├── architecture.md   # 架构设计文档
└── tasks.md          # 任务清单
```

## 开发状态

当前为MVP(最小可行产品)开发阶段，实现了基础的前后端通信和健康检查功能。 