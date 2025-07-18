# frontend

该目录用于存放前端应用相关的代码与资源。

## 技术选型
本项目前端采用 [React](https://react.dev/) 进行开发，后续将使用 Create React App 或 Vite 进行初始化。

## 初始化指引
1. 进入本目录：`cd frontend`
2. 初始化项目（推荐使用 Vite）：
   ```sh
   npm create vite@latest . -- --template react
   ```
3. 安装依赖：
   ```sh
   npm install
   ```
4. 启动开发服务器：
   ```sh
   npm run dev
   ```

## 开发环境启动指引
1. 安装依赖：
   ```sh
   npm install
   ```
2. 启动开发服务器：
   ```sh
   npm run dev
   ```
3. 默认访问地址：
   - http://localhost:5173/

## 单元测试
使用 [Vitest](https://vitest.dev/) 进行前端单元测试：
```sh
npm install --save-dev vitest
```
