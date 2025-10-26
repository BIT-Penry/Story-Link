# 📡 StoryLink API 接口文档

**版本**: v1.0.0  
**基础 URL**: `http://localhost:8000/api`  
**更新时间**: 2025-10-26

---

## 📖 目录

- [通用说明](#通用说明)
- [故事相关接口](#故事相关接口)
- [评论相关接口](#评论相关接口)
- [点赞相关接口](#点赞相关接口)
- [AI 功能接口](#ai-功能接口)
- [错误码说明](#错误码说明)

---

## 通用说明

### 请求头

```http
Content-Type: application/json
```

### 响应格式

#### 成功响应

```json
{
  "id": 1,
  "title": "示例",
  ...
}
```

#### 错误响应

```json
{
  "detail": "错误描述信息"
}
```

### 时间格式

所有时间字段使用 ISO 8601 格式：`2025-10-26T10:30:00`

---

## 故事相关接口

### 1. 创建故事

**接口**: `POST /api/stories`

**请求体**:
```json
{
  "title": "故事标题",
  "author": "作者昵称",
  "content": "故事内容",
  "parent_id": null
}
```

**字段说明**:
- `title` (string, 必填): 故事标题，1-100字
- `author` (string, 必填): 作者昵称，1-20字
- `content` (string, 必填): 故事内容，10-10000字
- `parent_id` (int, 可选): 父故事ID（Fork时使用）

**响应示例** (201 Created):
```json
{
  "id": 1,
  "title": "故事标题",
  "author": "作者昵称",
  "content": "故事内容",
  "parent_id": null,
  "is_approved": false,
  "video_url": null,
  "video_status": "pending",
  "likes_count": 0,
  "comments_count": 0,
  "views_count": 0,
  "tags": "",
  "category": "general",
  "created_at": "2025-10-26T10:30:00"
}
```

---

### 2. 获取故事列表

**接口**: `GET /api/stories`

**查询参数**:
- `approved_only` (bool): 仅显示已批准的，默认 false
- `sort_by` (string): 排序字段，可选值:
  - `created_at` (默认): 创建时间
  - `likes_count`: 点赞数
  - `comments_count`: 评论数
  - `views_count`: 浏览数
- `order` (string): 排序方向，`asc` 或 `desc` (默认)
- `limit` (int): 返回数量，默认 20，最大 100
- `offset` (int): 偏移量，默认 0
- `category` (string): 故事分类，可选

**请求示例**:
```
GET /api/stories?approved_only=true&sort_by=likes_count&order=desc&limit=10
```

**响应示例** (200 OK):
```json
{
  "total": 50,
  "stories": [
    {
      "id": 1,
      "title": "奇幻之旅",
      "author": "张三",
      "content": "很久很久以前...",
      "parent_id": null,
      "is_approved": true,
      "video_url": "/videos/story_1.mp4",
      "video_status": "completed",
      "likes_count": 42,
      "comments_count": 15,
      "views_count": 230,
      "tags": "奇幻,冒险",
      "category": "fantasy",
      "created_at": "2025-10-26T10:00:00"
    }
  ]
}
```

---

### 3. 获取单个故事

**接口**: `GET /api/stories/{story_id}`

**路径参数**:
- `story_id` (int): 故事ID

**响应示例** (200 OK):
```json
{
  "id": 1,
  "title": "奇幻之旅",
  "author": "张三",
  "content": "很久很久以前，在一个遥远的王国...",
  "parent_id": null,
  "is_approved": true,
  "video_url": "/videos/story_1.mp4",
  "video_status": "completed",
  "likes_count": 42,
  "comments_count": 15,
  "views_count": 230,
  "created_at": "2025-10-26T10:00:00"
}
```

**错误响应** (404 Not Found):
```json
{
  "detail": "故事不存在"
}
```

---

### 4. 批准故事（触发视频生成）

**接口**: `POST /api/stories/{story_id}/approve`

**路径参数**:
- `story_id` (int): 故事ID

**响应示例** (200 OK):
```json
{
  "message": "故事已批准，视频正在生成中...",
  "story_id": 1,
  "status": "generating"
}
```

**说明**:
- 此接口会将故事标记为已批准
- 异步触发视频生成任务
- 视频生成可能需要 2-10 分钟

---

### 5. 重新生成视频

**接口**: `POST /api/stories/{story_id}/regenerate`

**路径参数**:
- `story_id` (int): 故事ID

**响应示例** (200 OK):
```json
{
  "message": "视频重新生成中...",
  "story_id": 1
}
```

---

### 6. 搜索故事

**接口**: `GET /api/stories/search`

**查询参数**:
- `q` (string, 必填): 搜索关键词
- `limit` (int): 返回数量，默认 20

**请求示例**:
```
GET /api/stories/search?q=奇幻&limit=10
```

**响应示例** (200 OK):
```json
{
  "total": 5,
  "stories": [...]
}
```

---

## 评论相关接口

### 1. 获取故事评论列表

**接口**: `GET /api/stories/{story_id}/comments`

**路径参数**:
- `story_id` (int): 故事ID

**查询参数**:
- `limit` (int): 返回数量，默认 50
- `offset` (int): 偏移量，默认 0

**响应示例** (200 OK):
```json
{
  "total": 23,
  "comments": [
    {
      "id": 1,
      "story_id": 5,
      "author": "张三",
      "content": "写得真好！期待续集！",
      "created_at": "2025-10-26T10:30:00"
    },
    {
      "id": 2,
      "story_id": 5,
      "author": "李四",
      "content": "情节很有张力，赞！",
      "created_at": "2025-10-26T11:15:00"
    }
  ]
}
```

---

### 2. 发表评论

**接口**: `POST /api/stories/{story_id}/comments`

**路径参数**:
- `story_id` (int): 故事ID

**请求体**:
```json
{
  "author": "张三",
  "content": "写得真好！期待续集！"
}
```

**字段说明**:
- `author` (string, 必填): 评论者昵称，1-20字
- `content` (string, 必填): 评论内容，1-500字

**响应示例** (201 Created):
```json
{
  "id": 1,
  "story_id": 5,
  "author": "张三",
  "content": "写得真好！期待续集！",
  "created_at": "2025-10-26T10:30:00"
}
```

**错误响应**:
- 400: 昵称或内容为空/过长
- 404: 故事不存在

---

## 点赞相关接口

### 1. 获取故事点赞信息

**接口**: `GET /api/stories/{story_id}/likes`

**路径参数**:
- `story_id` (int): 故事ID

**查询参数**:
- `user_id` (string): 用户标识，默认 "anonymous"

**响应示例** (200 OK):
```json
{
  "story_id": 5,
  "likes_count": 42,
  "user_liked": false
}
```

---

### 2. 点赞故事

**接口**: `POST /api/stories/{story_id}/like`

**路径参数**:
- `story_id` (int): 故事ID

**请求体**:
```json
{
  "user_identifier": "user_123"
}
```

**字段说明**:
- `user_identifier` (string): 用户标识，默认 "anonymous"

**响应示例** (200 OK):
```json
{
  "message": "点赞成功",
  "likes_count": 43
}
```

**错误响应**:
- 400: 已经点赞过了
- 404: 故事不存在

---

### 3. 取消点赞

**接口**: `DELETE /api/stories/{story_id}/like`

**路径参数**:
- `story_id` (int): 故事ID

**请求体**:
```json
{
  "user_identifier": "user_123"
}
```

**响应示例** (200 OK):
```json
{
  "message": "已取消点赞",
  "likes_count": 42
}
```

**错误响应**:
- 400: 您还没有点赞过
- 404: 故事不存在

---

## AI 功能接口

### 1. 文本润色

**接口**: `POST /api/polish`

**请求体**:
```json
{
  "content": "很久很久以前，有一个小村庄。",
  "style": "default"
}
```

**字段说明**:
- `content` (string, 必填): 待润色的文本
- `style` (string, 可选): 润色风格，默认 "default"
  - `default`: 默认优化
  - `humorous`: 幽默风格
  - `poetic`: 诗意风格
  - `dramatic`: 戏剧化
  - `simple`: 简洁明了

**响应示例** (200 OK):
```json
{
  "polished_content": "在很久很久以前，有一个被群山环绕的古老村庄。那里的人们过着简单而宁静的生活...",
  "style": "default"
}
```

**说明**:
- 响应时间: 3-10 秒
- 如果 API Key 未配置，返回示例文本

---

### 2. 获取续写建议

**接口**: `GET /api/stories/{story_id}/suggestions`

**路径参数**:
- `story_id` (int): 故事ID

**响应示例** (200 OK):
```json
{
  "story_id": 1,
  "suggestions": [
    "主角遇到了一个神秘的陌生人，对方似乎知道关于村庄的秘密...",
    "突然，天空中出现了异样的光芒，村民们纷纷走出家门...",
    "这时，一个意外的消息传来，改变了主角的命运..."
  ]
}
```

**说明**:
- 基于故事内容生成 3 个续写方向
- 响应时间: 5-15 秒

---

## 错误码说明

### HTTP 状态码

| 状态码 | 说明 | 示例 |
|-------|------|------|
| 200 | 成功 | 查询成功 |
| 201 | 创建成功 | 故事创建成功 |
| 400 | 请求错误 | 参数验证失败 |
| 404 | 资源不存在 | 故事不存在 |
| 500 | 服务器错误 | 数据库错误 |

### 常见错误信息

#### 400 错误

```json
{
  "detail": "作者昵称不能为空"
}
```

```json
{
  "detail": "评论内容不能超过500字"
}
```

```json
{
  "detail": "您已经点赞过了"
}
```

#### 404 错误

```json
{
  "detail": "故事不存在"
}
```

#### 500 错误

```json
{
  "detail": "创建故事失败: database is locked"
}
```

```json
{
  "detail": "文本润色失败: API timeout"
}
```

---

## 🧪 测试示例

### 使用 curl 测试

#### 1. 创建故事

```bash
curl -X POST http://localhost:8000/api/stories \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试故事",
    "author": "测试用户",
    "content": "这是一个测试故事的内容..."
  }'
```

#### 2. 获取故事列表

```bash
curl "http://localhost:8000/api/stories?approved_only=true&limit=5"
```

#### 3. 发表评论

```bash
curl -X POST http://localhost:8000/api/stories/1/comments \
  -H "Content-Type: application/json" \
  -d '{
    "author": "评论者",
    "content": "写得很好！"
  }'
```

#### 4. 点赞

```bash
curl -X POST http://localhost:8000/api/stories/1/like \
  -H "Content-Type: application/json" \
  -d '{
    "user_identifier": "user_123"
  }'
```

#### 5. 文本润色

```bash
curl -X POST http://localhost:8000/api/polish \
  -H "Content-Type: application/json" \
  -d '{
    "content": "很久很久以前，有一个小村庄。",
    "style": "poetic"
  }'
```

### 使用 JavaScript 测试

```javascript
// 创建故事
const response = await fetch('http://localhost:8000/api/stories', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    title: '测试故事',
    author: '测试用户',
    content: '这是一个测试故事的内容...'
  })
});

const story = await response.json();
console.log(story);
```

---

## 📊 数据模型

### Story 模型

```typescript
interface Story {
  id: number;
  title: string;
  author: string;
  content: string;
  parent_id: number | null;
  is_approved: boolean;
  video_url: string | null;
  video_status: 'pending' | 'generating' | 'completed' | 'failed';
  likes_count: number;
  comments_count: number;
  views_count: number;
  tags: string;
  category: string;
  created_at: string;
}
```

### Comment 模型

```typescript
interface Comment {
  id: number;
  story_id: number;
  author: string;
  content: string;
  created_at: string;
}
```

### Like 模型

```typescript
interface Like {
  id: number;
  story_id: number;
  user_identifier: string;
  created_at: string;
}
```

---

## 🔄 视频状态流转

```
pending (初始) 
  ↓
generating (生成中)
  ↓
completed (完成) / failed (失败)
```

**状态说明**:
- `pending`: 尚未触发视频生成
- `generating`: 视频生成中（2-10分钟）
- `completed`: 视频生成成功
- `failed`: 视频生成失败

---

## 📝 更新日志

### v1.0.0 (2025-10-26)

**新增功能**:
- ✅ 故事 CRUD 接口
- ✅ 评论功能接口
- ✅ 点赞功能接口
- ✅ AI 文本润色接口
- ✅ 视频生成接口
- ✅ 搜索功能接口
- ✅ 多风格润色支持
- ✅ 续写建议接口

**优化**:
- 添加了完整的错误处理
- 优化了查询性能
- 增加了参数验证

---

## 💡 最佳实践

### 1. 错误处理

```javascript
try {
  const response = await fetch('/api/stories/1');
  if (!response.ok) {
    const error = await response.json();
    console.error('错误:', error.detail);
    return;
  }
  const data = await response.json();
  console.log(data);
} catch (error) {
  console.error('网络错误:', error);
}
```

### 2. 轮询视频状态

```javascript
async function pollVideoStatus(storyId) {
  const checkStatus = async () => {
    const response = await fetch(`/api/stories/${storyId}`);
    const story = await response.json();
    
    if (story.video_status === 'completed') {
      console.log('视频生成完成！');
      return story.video_url;
    }
    
    if (story.video_status === 'failed') {
      console.error('视频生成失败');
      return null;
    }
    
    // 5秒后再次检查
    setTimeout(checkStatus, 5000);
  };
  
  await checkStatus();
}
```

### 3. 分页加载

```javascript
async function loadMoreStories(offset = 0, limit = 20) {
  const response = await fetch(
    `/api/stories?approved_only=true&limit=${limit}&offset=${offset}`
  );
  const data = await response.json();
  return data;
}
```

---

## 📞 技术支持

如有问题，请联系:
- 后端负责人（成员1）
- API 文档维护者

**在线 API 文档**: http://localhost:8000/docs

---

**最后更新**: 2025-10-26  
**维护者**: StoryLink 开发团队

