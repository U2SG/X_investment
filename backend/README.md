# backend

该目录用于存放后端服务相关的代码与配置。

## 开发环境启动指引
1. 安装依赖（建议使用虚拟环境）：
   ```sh
   pip install -r requirements.txt
   ```
2. 启动 FastAPI 服务（开发模式）：
   ```sh
   uvicorn main:app --reload
   ```
3. 访问接口文档：
   - Swagger UI: http://localhost:8000/docs
   - Redoc: http://localhost:8000/redoc 