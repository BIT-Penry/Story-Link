# 🍴 Fork 故事功能设计

## 🎯 功能需求

用户可以将别人的优秀故事 **Fork** 到自己的仓库：
- ✅ Fork 后成为独立的新故事
- ✅ Fork 者成为新故事的"原作者"
- ✅ 可以在 Fork 的故事上续写
- ✅ 可以为 Fork 的故事生成视频
- ✅ 保留原始故事的链接（forked_from）

## 📊 与现有功能的区别

| 功能 | 协作续写 | Fork 故事 |
|------|----------|-----------|
| 故事数量 | 1个原创故事 | 原创 + N个Fork副本 |
| 显示位置 | 详情页显示所有续写 | 首页各自独立显示 |
| 作者关系 | 原作者 + 续写者 | Fork者成为新作者 |
| 视频生成 | 只有原作者 | 各自的作者都可以 |
| 内容关系 | 在同一故事上协作 | 独立发展 |

## 🗄️ 数据库设计

### 方案：添加 `forked_from` 字段

```sql
ALTER TABLE stories ADD COLUMN forked_from INTEGER DEFAULT NULL;
-- forked_from: 如果是 Fork 的故事，记录原故事的 ID

-- 示例数据结构：
-- 原故事: {id: 1, title: "中关村", author: "ssh", forked_from: NULL}
-- Fork 故事: {id: 5, title: "中关村", author: "Alice", forked_from: 1}
-- Fork 故事: {id: 6, title: "中关村", author: "Bob", forked_from: 1}
```

### 字段说明

- `parent_id`: 用于续写关系（添加到某个故事）
- `forked_from`: 用于 Fork 关系（从某个故事复制）

### 数据模型示例

```
原故事（ssh）
├── 续写1（B）         ← parent_id = 1
├── 续写2（C）         ← parent_id = 1
└── Fork1（Alice）     ← forked_from = 1, parent_id = NULL
    ├── 续写1（David） ← parent_id = 5
    └── 续写2（Eve）   ← parent_id = 5
```

---

## 🔧 后端实现

### 1. 数据库迁移

```python
def migrate_db():
    """添加 forked_from 字段"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(stories)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "forked_from" not in columns:
            cursor.execute("ALTER TABLE stories ADD COLUMN forked_from INTEGER DEFAULT NULL")
            print("✅ 添加 forked_from 字段")
        
        conn.commit()
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()
```

### 2. 新增 Fork 接口

```python
@app.post("/api/stories/{story_id}/fork")
def fork_story(story_id: int, fork_request: ForkRequest):
    """
    Fork 一个故事到自己的仓库
    
    Args:
        story_id: 要 Fork 的故事 ID
        fork_request: {author: "当前用户昵称"}
    
    Returns:
        新创建的故事信息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. 获取原故事（只能 fork 原创故事，不能 fork 续写）
        cursor.execute(
            "SELECT * FROM stories WHERE id = ? AND parent_id IS NULL",
            (story_id,)
        )
        original = cursor.fetchone()
        
        if not original:
            conn.close()
            raise HTTPException(status_code=404, detail="故事不存在或无法Fork")
        
        # 2. 检查是否自己 fork 自己的故事
        if original["author"] == fork_request.author:
            conn.close()
            raise HTTPException(status_code=400, detail="不能Fork自己的故事")
        
        # 3. 检查是否已经 fork 过
        cursor.execute(
            """
            SELECT id FROM stories 
            WHERE forked_from = ? AND author = ? AND parent_id IS NULL
            """,
            (story_id, fork_request.author)
        )
        existing_fork = cursor.fetchone()
        
        if existing_fork:
            conn.close()
            raise HTTPException(status_code=400, detail="你已经Fork过这个故事了")
        
        # 4. 创建 Fork（复制原故事内容）
        cursor.execute(
            """
            INSERT INTO stories 
            (title, author, content, forked_from, max_contributors, video_status, parent_id)
            VALUES (?, ?, ?, ?, ?, 'none', NULL)
            """,
            (
                original["title"],
                fork_request.author,
                original["content"],
                story_id,
                5  # 默认允许5人续写
            )
        )
        
        new_story_id = cursor.lastrowid
        
        # 5. 获取新创建的故事
        cursor.execute("SELECT * FROM stories WHERE id = ?", (new_story_id,))
        new_story = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        print(f"🍴 故事已Fork: {fork_request.author} fork了 {original['author']} 的《{original['title']}》")
        
        return dict_from_row(new_story)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fork失败: {str(e)}")


class ForkRequest(BaseModel):
    author: str
```

### 3. 修改故事列表接口

```python
@app.get("/api/stories", response_model=List[StoryResponse])
def get_stories(
    filter_by: str = "all",
    author: Optional[str] = None,  # 新增：按作者筛选
    sort_by: str = "created_at",
    limit: int = 50
):
    """
    获取故事列表
    
    filter_by:
        - all: 所有原创故事（包括Fork）
        - my: 我的故事（我创建的 + 我Fork的）
        - with_video: 有视频的故事
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 只查询原创故事（parent_id 为 NULL）
        where_clause = "WHERE parent_id IS NULL"
        
        if filter_by == "my" and author:
            # 我的故事：我创建的原创 + 我Fork的
            where_clause += f" AND author = '{author}'"
        elif filter_by == "with_video":
            where_clause += " AND video_status = 'completed'"
        
        query = f"""
            SELECT * FROM stories 
            {where_clause}
            ORDER BY {sort_by} DESC 
            LIMIT ?
        """
        
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict_from_row(row) for row in rows]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取故事列表失败: {str(e)}")
```

### 4. 新增获取原始故事信息接口

```python
@app.get("/api/stories/{story_id}/origin")
def get_origin_story(story_id: int):
    """
    获取故事的原始来源信息
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        story = cursor.fetchone()
        
        if not story:
            conn.close()
            raise HTTPException(status_code=404, detail="故事不存在")
        
        # 如果是 Fork 的故事，获取原始故事信息
        origin_info = None
        if story["forked_from"]:
            cursor.execute(
                "SELECT id, title, author, created_at FROM stories WHERE id = ?",
                (story["forked_from"],)
            )
            origin = cursor.fetchone()
            if origin:
                origin_info = {
                    "id": origin["id"],
                    "title": origin["title"],
                    "author": origin["author"],
                    "created_at": origin["created_at"]
                }
        
        conn.close()
        
        return {
            "story_id": story_id,
            "is_forked": story["forked_from"] is not None,
            "origin": origin_info
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取原始信息失败: {str(e)}")
```

---

## 🎨 前端实现

### 1. API 客户端 (`api.js`)

```javascript
// Fork 故事
export const forkStory = async (id, author) => {
  const response = await api.post(`/stories/${id}/fork`, { author })
  return response.data
}

// 获取原始故事信息
export const getOriginInfo = async (id) => {
  const response = await api.get(`/stories/${id}/origin`)
  return response.data
}
```

### 2. 首页 (`HomePage.jsx`)

```jsx
// 添加筛选选项
{[
  { value: 'all', label: '全部故事', icon: '📖' },
  { value: 'my', label: '我的故事', icon: '📁' },
  { value: 'with_video', label: '有视频', icon: '🎥' }
].map(filter => (
  <button
    key={filter.value}
    onClick={() => setFilterBy(filter.value)}
  >
    {filter.icon} {filter.label}
  </button>
))}

// 修改加载故事
const loadStories = async () => {
  try {
    setLoading(true)
    const params = new URLSearchParams({ filter_by: filterBy, limit: 50 })
    
    // 如果是"我的故事"，传递作者参数
    if (filterBy === 'my' && userNickname) {
      params.append('author', userNickname)
    }
    
    const response = await axios.get(`/api/stories?${params}`)
    setStories(response.data)
  } catch (err) {
    setError('加载故事失败')
  } finally {
    setLoading(false)
  }
}
```

### 3. 故事详情页 (`StoryDetailPage.jsx`)

```jsx
import { forkStory, getOriginInfo } from '../api/api'

function StoryDetailPage() {
  const [originInfo, setOriginInfo] = useState(null)
  const [forking, setForking] = useState(false)
  
  // 加载原始信息
  useEffect(() => {
    const loadOriginInfo = async () => {
      try {
        const info = await getOriginInfo(id)
        setOriginInfo(info)
      } catch (err) {
        console.error('获取原始信息失败:', err)
      }
    }
    loadOriginInfo()
  }, [id])
  
  // Fork 故事
  const handleFork = async () => {
    if (!userNickname) {
      alert('请先设置昵称')
      return
    }
    
    if (fullStory.original_author === userNickname) {
      alert('不能Fork自己的故事')
      return
    }
    
    if (!confirm(`确认要Fork《${fullStory.title}》到你的仓库吗？`)) {
      return
    }
    
    try {
      setForking(true)
      const newStory = await forkStory(id, userNickname)
      alert(`Fork成功！现在你可以在"我的故事"中找到它`)
      navigate(`/story/${newStory.id}`)
    } catch (err) {
      alert(err.response?.data?.detail || 'Fork失败')
      console.error(err)
    } finally {
      setForking(false)
    }
  }
  
  return (
    <div>
      {/* 显示原始来源 */}
      {originInfo?.is_forked && originInfo.origin && (
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-4">
          <p className="text-blue-300 text-sm">
            🍴 Forked from{' '}
            <Link 
              to={`/story/${originInfo.origin.id}`}
              className="underline hover:text-blue-200"
            >
              {originInfo.origin.author} 的《{originInfo.origin.title}》
            </Link>
          </p>
        </div>
      )}
      
      {/* Fork 按钮 */}
      {fullStory.original_author !== userNickname && (
        <button
          onClick={handleFork}
          disabled={forking}
          className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
        >
          {forking ? '⏳ Fork中...' : '🍴 Fork 到我的仓库'}
        </button>
      )}
    </div>
  )
}
```

---

## 📊 用户流程示例

### 场景：Alice Fork ssh 的故事

```
Step 1: ssh 创建《中关村》
  stories: {id: 1, title: "中关村", author: "ssh", forked_from: NULL}

Step 2: Alice 浏览发现很喜欢
  - 点击详情页
  - 点击"🍴 Fork 到我的仓库"

Step 3: 系统创建 Fork
  stories: {id: 5, title: "中关村", author: "Alice", forked_from: 1}
  
Step 4: Alice 可以续写和生成视频
  - Alice 对 id=5 续写
  - Alice 可以为 id=5 生成视频
  - 这不影响 ssh 的原故事 id=1
```

### 首页显示

```
全部故事:
  - 中关村 (ssh)
  - 中关村 (Alice) 🍴

我的故事 (ssh):
  - 中关村

我的故事 (Alice):
  - 中关村 🍴
```

### 详情页显示

```
Alice 查看 id=5:
┌─────────────────────────────────┐
│ 🍴 Forked from ssh 的《中关村》 │
├─────────────────────────────────┤
│ 中关村                          │
│ 👤 Alice (Fork自ssh)            │
│                                 │
│ [原创内容...]                   │
│ [Alice的续写...]                │
│                                 │
│ [🎬 生成视频] ← Alice可以生成   │
└─────────────────────────────────┘
```

---

## 🔍 与协作续写的配合

两个功能可以同时存在：

1. **协作续写**: B 和 C 在 ssh 的原故事上续写
   - 首页只显示一个"中关村(ssh)"
   - 详情页显示 ssh + B + C 的内容
   - 只有 ssh 能生成视频

2. **Fork 故事**: Alice Fork 后独立发展
   - 首页显示两个故事："中关村(ssh)"和"中关村(Alice)"
   - Alice 的版本可以有自己的续写者
   - Alice 可以为自己的版本生成视频

---

## ✅ 实施检查清单

### 后端
- [ ] 数据库添加 `forked_from` 字段
- [ ] 实现 `/api/stories/{id}/fork` 接口
- [ ] 修改 `/api/stories` 支持 `my` 筛选
- [ ] 实现 `/api/stories/{id}/origin` 接口
- [ ] 更新 `StoryResponse` 模型包含 `forked_from`

### 前端
- [ ] 添加 `forkStory` API 调用
- [ ] 首页添加"我的故事"筛选
- [ ] 详情页添加 Fork 按钮
- [ ] 显示原始故事来源信息
- [ ] 优化 UI 显示 Fork 标识

### 测试
- [ ] 测试 Fork 功能
- [ ] 测试不能 Fork 自己的故事
- [ ] 测试不能重复 Fork
- [ ] 测试 Fork 后可以续写
- [ ] 测试 Fork 后可以生成视频
- [ ] 测试"我的故事"筛选

---

## 🎯 预期效果

用户体验：
1. 看到好故事 → 点击 Fork → 成为自己的故事
2. 可以在自己的版本上续写
3. 可以为自己的版本生成视频
4. 清楚显示 Fork 来源

这样既保留了协作续写的特性（多人在同一故事上协作），又增加了 Fork 的灵活性（独立发展）。

是否现在开始实现这个功能？

