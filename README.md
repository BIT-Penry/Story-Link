# 🎬 StoryLink - 故事接力创作平台

> **一句话,AI 自动编故事;喜欢的故事,自动生成短片。**

StoryLink 是一个支持故事接力创作与 AI 增强的轻量级平台。用户可以创作故事、Fork 他人的故事续写、使用 AI 润色文本,并将喜欢的故事自动生成为短视频。

## ✨ 核心功能

- 📝 **发布原始故事** - 填写标题、昵称、正文,创建新故事
- 🍴 **Fork 并续写** - 在他人故事基础上创建新版本
- 🤖 **AI 文本润色** - 使用 GPT-4o-mini 优化故事表达
- 🎥 **自动生成视频** - 使用 Google Veo 将故事转换为短片
- 📺 **首页展示** - 浏览所有已发布的故事和视频

## 🏗️ 技术栈

### 后端
- **FastAPI** - 高性能 Python Web 框架
- **SQLite** - 轻量级数据库
- **OpenAI GPT-4o-mini** - 文本润色
- **Google Veo 3.1** - 视频生成

### 前端
- **React** - UI 框架
- **Vite** - 构建工具
- **Tailwind CSS** - 样式框架
- **React Router** - 路由管理

## 📦 项目结构

```
StoryLink/
├── backend/              # 后端代码
│   ├── main.py          # FastAPI 主应用
│   ├── ai_service.py    # AI 服务模块
│   ├── requirements.txt # Python 依赖
│   └── videos/          # 生成的视频文件
│
├── frontend/            # 前端代码
│   ├── src/
│   │   ├── pages/       # 页面组件
│   │   │   ├── HomePage.jsx        # 首页
│   │   │   ├── StoryDetailPage.jsx # 故事详情页
│   │   │   └── EditPage.jsx        # 编辑页
│   │   ├── api/         # API 调用
│   │   ├── App.jsx      # 主应用
│   │   └── main.jsx     # 入口文件
│   ├── package.json     # Node 依赖
│   └── vite.config.js   # Vite 配置
│
├── .env.example         # 环境变量示例
├── .gitignore
└── README.md
```

## 🚀 快速开始

### 1. 环境准备

确保已安装:
- Python 3.9+
- Node.js 18+
- pip 和 npm

### 2. 克隆项目

```bash
cd "/Applications/宋晗搏/黑客松/电影GitHub"
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写 API Key:

```bash
cp .env.example .env
```

编辑 `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. 启动后端

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动后端服务器 (端口 8000)
python main.py
```

后端将在 `http://localhost:8000` 运行

### 5. 启动前端

在新终端中:

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器 (端口 3000)
npm run dev
```

前端将在 `http://localhost:3000` 运行

### 6. 访问应用

打开浏览器访问: **http://localhost:3000**

## 📖 使用指南

### 创作新故事

1. 点击首页的"✨ 写新故事"按钮
2. 填写昵称、标题、故事内容
3. 点击"🚀 提交故事"

### Fork 并续写

1. 进入任意故事详情页
2. 点击"🍴 Fork 并续写"按钮
3. 编辑新版本并提交

### AI 润色

1. 在故事详情页点击"🤖 AI 润色"
2. 系统会使用 GPT-4o-mini 优化文本
3. 可以基于润色后的版本继续 Fork

### 发布为视频

1. 在故事详情页点击"🚀 发布为视频"
2. 系统会调用 Google Veo 生成视频(需要几分钟)
3. 生成完成后可以在线观看或重新生成

## 🔌 API 接口

### 后端 API (端口 8000)

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/stories` | 获取故事列表 |
| GET | `/api/stories/{id}` | 获取故事详情 |
| POST | `/api/stories` | 创建新故事 |
| POST | `/api/polish` | AI 文本润色 |
| POST | `/api/stories/{id}/approve` | 批准故事并生成视频 |
| POST | `/api/stories/{id}/regenerate` | 重新生成视频 |

### 数据库表结构

```sql
CREATE TABLE stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    parent_id INTEGER,
    is_approved BOOLEAN DEFAULT FALSE,
    video_url TEXT,
    video_status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES stories(id)
);
```

## 🎯 MVP 范围

### ✅ 已实现功能

- [x] 发布原始故事
- [x] Fork 故事并续写
- [x] AI 文本润色 (GPT-4o-mini)
- [x] 发布为视频按钮
- [x] 首页展示已批准故事
- [x] 视频生成 (Google Veo)
- [x] 视频状态轮询
- [x] 重新生成视频

### 🚧 预留功能 (未实现)

- [ ] 用户登录/注册系统
- [ ] 评论/点赞/分享
- [ ] 多版本对比/合并
- [ ] 语音配音
- [ ] PR (Pull Request) 功能

## 🧪 开发测试

### 后端测试

```bash
# 查看 API 文档
open http://localhost:8000/docs
```

### 前端测试

```bash
# 构建生产版本
cd frontend
npm run build

# 预览构建结果
npm run preview
```

## 🐛 故障排除

### 问题 1: 后端无法启动

**解决方案**:
```bash
# 检查 Python 版本
python --version  # 应为 3.9+

# 重新安装依赖
pip install --upgrade -r backend/requirements.txt
```

### 问题 2: 视频生成失败

**可能原因**:
- Google API Key 未配置或无效
- API 配额不足
- 网络连接问题

**解决方案**:
- 检查 `.env` 文件中的 `GOOGLE_API_KEY`
- 查看后端日志获取详细错误信息

### 问题 3: 前端页面空白

**解决方案**:
```bash
# 清除缓存
rm -rf frontend/node_modules
rm -rf frontend/dist

# 重新安装
cd frontend
npm install
npm run dev
```

## 📝 待办事项

- [ ] 添加用户认证系统
- [ ] 实现评论和点赞功能
- [ ] 支持多版本故事对比
- [ ] 优化视频生成速度
- [ ] 添加故事分类和标签
- [ ] 实现搜索功能
- [ ] 支持故事导出 (PDF/Markdown)

## 👥 团队分工建议

| 角色 | 任务 |
|------|------|
| **后端开发** | SQLite 表设计 + FastAPI 接口 + AI 代理 |
| **前端开发** | React 页面 + API 调用 + Tailwind 样式 |
| **AI 集成** | OpenAI/Google Veo 调用 + Prompt 工程 |
| **联调 & 演示** | 环境配置 + 代码整合 + 演示脚本 |

## 📄 许可证

MIT License

## 🙏 致谢

- OpenAI 提供的 GPT-4o-mini API
- Google 提供的 Veo 3.1 视频生成 API
- React、FastAPI、Tailwind CSS 等开源社区

---

**Made with ❤️ by StoryLink Team**

