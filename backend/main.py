"""
MovieHub 后端 API
MVP 版本 - 支持故事创作、Fork、AI 润色和视频生成
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
import sqlite3
from datetime import datetime
import os
from pathlib import Path

# AI 模块
from ai_service import polish_text, generate_video

app = FastAPI(title="MovieHub API", version="1.0.0")

# CORS 配置(必须在挂载静态文件之前)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制为前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保视频目录存在
VIDEO_DIR = Path("videos")
VIDEO_DIR.mkdir(exist_ok=True)

# 挂载静态文件目录(视频)
app.mount("/videos", StaticFiles(directory="videos"), name="videos")

# 数据库配置
DB_PATH = "moviehub.db"

# ========== 数据库初始化 ==========
def init_db():
    """创建数据库表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            content TEXT NOT NULL,
            parent_id INTEGER,
            is_approved BOOLEAN DEFAULT FALSE,
            video_url TEXT,
            video_status TEXT DEFAULT 'none',
            max_contributors INTEGER DEFAULT 5,
            fork_count INTEGER DEFAULT 0,
            is_original BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES stories(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

def migrate_db():
    """迁移现有数据库"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(stories)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # 添加新字段
        if "max_contributors" not in columns:
            cursor.execute("ALTER TABLE stories ADD COLUMN max_contributors INTEGER DEFAULT 5")
            print("✅ 添加字段: max_contributors")
        if "fork_count" not in columns:
            cursor.execute("ALTER TABLE stories ADD COLUMN fork_count INTEGER DEFAULT 0")
            print("✅ 添加字段: fork_count")
        if "is_original" not in columns:
            cursor.execute("ALTER TABLE stories ADD COLUMN is_original BOOLEAN DEFAULT TRUE")
            print("✅ 添加字段: is_original")
        if "forked_from" not in columns:
            cursor.execute("ALTER TABLE stories ADD COLUMN forked_from INTEGER DEFAULT NULL")
            print("✅ 添加字段: forked_from")
        
        # 更新现有数据的 video_status
        cursor.execute("UPDATE stories SET video_status = 'none' WHERE video_status = 'pending'")
        
        conn.commit()
        print("✅ 数据库迁移完成")
    except Exception as e:
        print(f"⚠️  数据库迁移失败: {e}")
        conn.rollback()
    finally:
        conn.close()

# 启动时初始化数据库
init_db()
migrate_db()

# ========== Pydantic 模型 ==========
class StoryCreate(BaseModel):
    title: str
    author: str
    content: str
    parent_id: Optional[int] = None
    max_contributors: int = 5

class StoryResponse(BaseModel):
    id: int
    title: str
    author: str
    content: str
    parent_id: Optional[int]
    is_approved: bool
    video_url: Optional[str]
    video_status: str
    max_contributors: int
    fork_count: int
    is_original: bool
    forked_from: Optional[int]
    created_at: str

class PolishRequest(BaseModel):
    content: str

class GenerateVideoRequest(BaseModel):
    author: str

class ForkRequest(BaseModel):
    author: str

# ========== 数据库操作函数 ==========
def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def dict_from_row(row):
    """将 sqlite3.Row 转换为字典"""
    return {key: row[key] for key in row.keys()}

# ========== API 端点 ==========

@app.get("/")
def read_root():
    return {"message": "StoryLink API is running!", "version": "1.0.0"}

@app.post("/api/stories", response_model=StoryResponse)
def create_story(story: StoryCreate):
    """创建新故事（立即保存，不需要生成视频）"""
    try:
        # 验证参数
        if not story.title.strip():
            raise HTTPException(status_code=400, detail="标题不能为空")
        if not story.author.strip():
            raise HTTPException(status_code=400, detail="作者昵称不能为空")
        if not story.content.strip():
            raise HTTPException(status_code=400, detail="内容不能为空")
        if story.max_contributors < 1 or story.max_contributors > 5:
            raise HTTPException(status_code=400, detail="续写人数必须在1-5之间")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 如果是续写（有 parent_id）
        is_original = story.parent_id is None
        
        if not is_original:
            # 检查父故事是否存在
            cursor.execute("SELECT max_contributors, fork_count FROM stories WHERE id = ?", 
                         (story.parent_id,))
            parent = cursor.fetchone()
            
            if not parent:
                conn.close()
                raise HTTPException(status_code=404, detail="父故事不存在")
            
            # 检查是否超过续写人数限制
            if parent["fork_count"] >= parent["max_contributors"]:
                conn.close()
                raise HTTPException(
                    status_code=400, 
                    detail=f"该故事已达到最大续写人数限制（{parent['max_contributors']}人）"
                )
            
            # 更新父故事的续写计数
            cursor.execute(
                "UPDATE stories SET fork_count = fork_count + 1 WHERE id = ?",
                (story.parent_id,)
            )
        
        # 插入新故事
        cursor.execute(
            """
            INSERT INTO stories 
            (title, author, content, parent_id, max_contributors, is_original, video_status)
            VALUES (?, ?, ?, ?, ?, ?, 'none')
            """,
            (story.title, story.author, story.content, story.parent_id, 
             story.max_contributors, is_original)
        )
        
        conn.commit()
        story_id = cursor.lastrowid
        
        # 获取刚创建的故事
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        row = cursor.fetchone()
        conn.close()
        
        print(f"✅ 故事创建成功: id={story_id}, author={story.author}, is_original={is_original}")
        
        return dict_from_row(row)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建故事失败: {str(e)}")

@app.get("/api/stories", response_model=List[StoryResponse])
def get_stories(
    filter_by: str = "all",
    author: Optional[str] = None,
    sort_by: str = "created_at",
    limit: int = 50
):
    """
    获取故事列表（只返回原创故事，续写内容不单独显示）
    
    filter_by:
        - all: 所有原创故事（只显示真正的原创，不包括Fork的）
        - my: 我的故事（我创建的原创 + 我Fork的）
        - with_video: 有视频的原创故事
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 只查询原创故事（parent_id 为 NULL）
        where_clause = "WHERE parent_id IS NULL"
        
        if filter_by == "my" and author:
            # 我的故事：我创建的原创 + 我Fork的
            where_clause += f" AND author = '{author}'"
        elif filter_by == "all":
            # 全部故事：只显示真正的原创（不包括Fork的）
            where_clause += " AND forked_from IS NULL"
        elif filter_by == "with_video":
            where_clause += " AND video_status = 'completed'"
        
        # 验证排序字段
        if sort_by not in ["created_at", "fork_count"]:
            sort_by = "created_at"
        
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

@app.get("/api/stories/{story_id}", response_model=StoryResponse)
def get_story(story_id: int):
    """获取单个故事详情"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="故事不存在")
        
        return dict_from_row(row)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取故事失败: {str(e)}")

@app.post("/api/polish")
def polish_story(request: PolishRequest):
    """AI 文本润色"""
    try:
        polished_content = polish_text(request.content)
        return {"polished_content": polished_content}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文本润色失败: {str(e)}")

@app.post("/api/stories/{story_id}/generate-video")
def generate_video_for_story(
    story_id: int, 
    request: GenerateVideoRequest,
    background_tasks: BackgroundTasks
):
    """
    为故事生成视频（使用完整内容：原创+所有续写）
    只有原作者可以操作
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取原创故事信息
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        story = cursor.fetchone()
        
        if not story:
            conn.close()
            raise HTTPException(status_code=404, detail="故事不存在")
        
        # 如果是续写，获取原创故事
        if story["parent_id"] is not None:
            conn.close()
            raise HTTPException(status_code=400, detail="请在原创故事页面生成视频")
        
        # 验证作者身份（只有原作者可以生成视频）
        if story["author"] != request.author:
            conn.close()
            raise HTTPException(status_code=403, detail="只有故事原作者可以生成视频")
        
        # 检查是否已经在生成中
        if story["video_status"] == "generating":
            conn.close()
            raise HTTPException(status_code=400, detail="视频正在生成中，请稍候")
        
        # 获取完整内容（原创+所有续写）
        cursor.execute(
            "SELECT content FROM stories WHERE parent_id = ? ORDER BY created_at ASC",
            (story_id,)
        )
        contributions = cursor.fetchall()
        
        # 合并所有内容
        full_content = story["content"]
        for contrib in contributions:
            full_content += "\n\n" + contrib["content"]
        
        # 更新状态为生成中
        cursor.execute(
            "UPDATE stories SET video_status = 'generating' WHERE id = ?",
            (story_id,)
        )
        conn.commit()
        conn.close()
        
        # 后台任务：使用完整内容生成视频
        background_tasks.add_task(generate_video_task, story_id, full_content)
        
        print(f"🎬 视频生成任务已启动: story_id={story_id}, author={request.author}")
        print(f"📝 使用完整内容（包含 {len(contributions)} 个续写）")
        
        return {
            "message": f"视频生成任务已启动（包含 {len(contributions)} 个续写内容）",
            "story_id": story_id,
            "status": "generating",
            "total_contributions": len(contributions)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成视频失败: {str(e)}")

@app.get("/api/stories/{story_id}/can-fork")
def check_can_fork(story_id: int):
    """检查故事是否还能被续写"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT max_contributors, fork_count, title, author FROM stories WHERE id = ?",
            (story_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="故事不存在")
        
        can_fork = row["fork_count"] < row["max_contributors"]
        
        return {
            "can_fork": can_fork,
            "max_contributors": row["max_contributors"],
            "current_forks": row["fork_count"],
            "remaining": row["max_contributors"] - row["fork_count"],
            "title": row["title"],
            "author": row["author"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")

@app.get("/api/stories/{story_id}/full-content")
def get_full_story_content(story_id: int):
    """
    获取故事的完整内容（原创+所有续写）
    用于显示和生成视频
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 获取原创故事
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        original = cursor.fetchone()
        
        if not original:
            conn.close()
            raise HTTPException(status_code=404, detail="故事不存在")
        
        # 获取所有续写（按创建时间排序）
        cursor.execute(
            """
            SELECT id, author, title, content, created_at 
            FROM stories 
            WHERE parent_id = ? 
            ORDER BY created_at ASC
            """,
            (story_id,)
        )
        contributions = cursor.fetchall()
        conn.close()
        
        # 构建完整内容
        full_content = original["content"]
        contribution_list = []
        
        for contrib in contributions:
            full_content += "\n\n" + contrib["content"]
            contribution_list.append({
                "id": contrib["id"],
                "author": contrib["author"],
                "title": contrib["title"],
                "content": contrib["content"],
                "created_at": contrib["created_at"]
            })
        
        return {
            "story_id": story_id,
            "title": original["title"],
            "original_author": original["author"],
            "original_content": original["content"],
            "contributions": contribution_list,
            "full_content": full_content,
            "contribution_count": len(contribution_list),
            "max_contributors": original["max_contributors"],
            "video_url": original["video_url"],
            "video_status": original["video_status"],
            "created_at": original["created_at"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取完整内容失败: {str(e)}")

@app.post("/api/stories/{story_id}/fork", response_model=StoryResponse)
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
            raise HTTPException(status_code=404, detail="故事不存在或无法Fork（只能Fork原创故事）")
        
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
        
        # 4. 创建 Fork（复制原故事内容，但作者改为当前用户）
        cursor.execute(
            """
            INSERT INTO stories 
            (title, author, content, forked_from, max_contributors, video_status, parent_id, fork_count, is_original)
            VALUES (?, ?, ?, ?, ?, 'none', NULL, 0, TRUE)
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

def generate_video_task(story_id: int, content: str):
    """后台任务:生成视频"""
    try:
        # 调用 AI 视频生成服务
        video_path = generate_video(content, story_id)
        
        # 更新数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE stories 
            SET video_url = ?, video_status = 'completed'
            WHERE id = ?
            """,
            (video_path, story_id)
        )
        conn.commit()
        conn.close()
        
        print(f"✅ 视频生成完成: story_id={story_id}, video={video_path}")
    
    except Exception as e:
        # 标记为失败
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE stories SET video_status = 'failed' WHERE id = ?",
            (story_id,)
        )
        conn.commit()
        conn.close()
        
        print(f"❌ 视频生成失败: story_id={story_id}, error={str(e)}")

@app.post("/api/stories/{story_id}/regenerate")
def regenerate_video(story_id: int, background_tasks: BackgroundTasks):
    """重新生成视频"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        story = cursor.fetchone()
        
        if not story:
            conn.close()
            raise HTTPException(status_code=404, detail="故事不存在")
        
        # 更新状态为生成中
        cursor.execute(
            "UPDATE stories SET video_status = 'generating' WHERE id = ?",
            (story_id,)
        )
        conn.commit()
        conn.close()
        
        # 后台任务:重新生成视频
        background_tasks.add_task(generate_video_task, story_id, story["content"])
        
        return {"message": "视频重新生成中...", "story_id": story_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重新生成视频失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

