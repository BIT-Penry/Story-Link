# StoryLink MVP 开发规范文档

## 🌿 分支策略（Feature Branch + PR）

采用 **极简 Feature Branch 工作流**（小型团队最清晰、最安全的协作方式）：

### 1. main 分支规则

* 仅包含 **可演示、无崩溃** 的代码
* 禁止直接 push 代码
* 所有合并必须通过 Pull Request（PR）完成

### 2. 功能分支命名规范

从 main 分支拉出个人功能分支，命名格式：

`feat/<模块>-<姓名缩写>`

**示例**：

* `feat/backend-api-ly`（后端接口 - 李阳）
* `feat/frontend-ui-wz`（前端界面 - 王泽）
* `feat/ai-proxy-xy`（AI 代理 - 小雪）
* `feat/demo-deploy-zh`（演示部署 - 张海）

### 3. 合并流程

a. 功能开发完成 → push 到远程功能分支
b. 创建 PR → 标题注明状态（`[WIP]` 开发中 / `[Ready]` 可合并）
c. 至少 1 人快速 review（重点：能否跑通？是否破坏现有功能？）
d. 审核通过后，通过 **squash merge** 合并到 main 分支

> 💡 节省时间技巧：review 可口头确认，但 PR 必须创建（确保代码可追溯）



***

## 📂 项目结构

```
storylink-mvp/
├── backend/          # FastAPI 服务（后端代码）
├── frontend/         # React + Vite 应用（前端代码）
├── docs/             # 演示脚本、接口说明（可选）
├── .gitignore        # 忽略 node_modules、.env、__pycache__ 等
├── README.md         # 启动指南（必读！）
└── LICENSE           # 可选，建议 MIT 协议
```



***

## 🧾 提交（Commit）规范

使用 **语义化前缀** 提交，便于快速追踪变更：

| 前缀      | 说明             |
| ------- | -------------- |
| `feat`  | 新功能开发          |
| `fix`   | 修复 bug         |
| `docs`  | 文档更新（含注释）      |
| `chore` | 构建 / 依赖 / 配置调整 |

**示例**：

```
git commit -m "feat: add /stories POST endpoint"  # 新增故事提交接口
git commit -m "fix: handle empty nickname in form" # 修复表单空昵称问题
git commit -m "docs: update API docs in README"    # 更新 README 中的接口文档
git commit -m "chore: add vite config proxy"       # 配置 Vite 代理
```



***

## 🔐 敏感信息管理

1. 所有 API Key（如 OpenAI、T2V）必须通过 `.env` 文件加载
2. `.env` 文件 **必须加入 .gitignore**（禁止提交到仓库）
3. 在 `README.md` 中提供 `.env.example` 模板（示例如下）：

```
# .env.example（复制到 .env 后替换实际密钥）
OPENAI_API_KEY=sk-xxxx
T2V_API_KEY=tv-xxxx
```



***

## 🔄 集成与测试

核心原则：**早集成、早测试、少踩坑**

1. 每完成一个接口 / 页面，立即尝试联调
2. 后端：优先用 `curl` 或 `httpie` 验证接口可用性
3. 前端：无法联调时可用临时 mock 数据（必须标注 `// MOCK` 注释）
4. 每日集成检查点（至少 2 次）：
   * 时间：建议 12:00 和 16:00
   * 操作：
     1. 拉取最新 main 分支
     2. 合并自己的功能分支
     3. 验证本地能完整跑通核心流程



***

## 🚀 演示准备规范

确保演示环节零故障，需完成以下准备：

1. 一键启动要求：所有成员需在自己机器上 **一键启动全栈服务**（`README.md` 必须写清启动命令）
2. 公网链接生成：使用 `ngrok` 暴露服务
   * 前端：`ngrok http 5173`
   * 后端代理：`ngrok http 8000`
3. 备用方案：准备 **演示视频**（防止现场网络 / 服务异常）
4. 脚本统一：演示脚本放在 `docs/demo-script.md`（所有人遵循统一脚本）
```
