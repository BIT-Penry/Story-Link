# UV环境设置和应用启动指南

本文档将指导您如何使用uv为StoryLink项目创建隔离的Python环境并启动应用。

## 环境要求

- Python 3.9+
- uv (推荐版本 0.8+)
- Node.js 18+

## 后端环境设置

### 方法一：使用lockfile（推荐）

1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 使用uv创建虚拟环境：
   ```bash
   uv venv
   ```
   这将在`backend/.venv`目录下创建一个新的虚拟环境。

3. 激活虚拟环境：
   ```bash
   source .venv/bin/activate
   ```

4. 使用lockfile安装Python依赖（更快更一致）：
   ```bash
   uv pip install -r requirements-lock.txt
   ```

### 方法二：从requirements.txt安装

如果您没有lockfile或者需要重新生成依赖列表：

1. 进入后端目录：
   ```bash
   cd backend
   ```

2. 使用uv创建虚拟环境：
   ```bash
   uv venv
   ```

3. 激活虚拟环境：
   ```bash
   source .venv/bin/activate
   ```

4. 安装Python依赖：
   ```bash
   uv pip install -r requirements.txt
   ```

## 前端环境设置

1. 进入前端目录：
   ```bash
   cd frontend
   ```

2. 安装Node.js依赖：
   ```bash
   npm install
   ```

注意：`package-lock.json` 文件会跟踪确切的依赖版本，确保在不同环境中的一致性。
该文件应该提交到版本控制中，以确保团队成员使用相同的依赖版本。

## 启动应用

### 启动后端服务

1. 确保您在`backend`目录并且虚拟环境已激活：
   ```bash
   cd backend
   source .venv/bin/activate
   ```

2. 启动后端服务：
   ```bash
   python main.py
   ```
   或者在后台运行：
   ```bash
   python main.py &
   ```

3. 后端服务将在 `http://localhost:8000` 运行
   - API文档: http://localhost:8000/docs

### 启动前端开发服务器

1. 确保您在`frontend`目录：
   ```bash
   cd frontend
   ```

2. 启动前端开发服务器：
   ```bash
   npm run dev
   ```
   或者在后台运行：
   ```bash
   npm run dev &
   ```

3. 前端开发服务器将在 `http://localhost:3000` 运行

## 验证服务运行

- 检查后端是否运行正常：
  ```bash
  curl http://localhost:8000/docs
  ```

- 检查前端是否运行正常：
  ```bash
  curl http://localhost:3000
  ```

## 停止服务

- 如果您在后台运行了服务，可以使用以下命令停止：

  查找进程：
  ```bash
  ps aux | grep main.py  # 查找后端进程
  ps aux | grep "npm run dev"  # 查找前端进程
  ```

  终止进程：
  ```bash
  kill -9 <进程ID>
  ```

## 更新lockfile

当项目的依赖发生变化时，需要更新lockfile：

1. 激活虚拟环境：
   ```bash
   cd backend
   source .venv/bin/activate
   ```

2. 更新requirements-lock.txt：
   ```bash
   uv pip compile requirements.txt -o requirements-lock.txt
   ```

## 故障排除

1. 如果遇到依赖安装问题，请确保您的uv版本是最新的：
   ```bash
   uv --version
   ```

2. 如果端口被占用，您可以修改启动端口：
   - 后端：在`backend/main.py`中修改端口
   - 前端：在`frontend/vite.config.js`中配置端口

3. 确保所有环境变量已正确配置，特别是API密钥。

4. 如果遇到前端依赖问题：
   - 删除 `frontend/node_modules` 目录和 `frontend/package-lock.json` 文件
   - 重新运行 `npm install`
   - 提交更新后的 `package-lock.json` 文件（如果确实有合法的依赖更新）