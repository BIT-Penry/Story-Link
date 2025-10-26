"""
StoryLink 后端 API
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

app = FastAPI(title="StoryLink API", version="1.0.0")

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
DB_PATH = "storylink.db"

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
            video_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES stories(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

# 启动时初始化数据库
init_db()

# ========== Pydantic 模型 ==========
class StoryCreate(BaseModel):
    title: str
    author: str
    content: str
    parent_id: Optional[int] = None

class StoryResponse(BaseModel):
    id: int
    title: str
    author: str
    content: str
    parent_id: Optional[int]
    is_approved: bool
    video_url: Optional[str]
    video_status: str
    created_at: str

class PolishRequest(BaseModel):
    content: str

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
    """创建新故事"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO stories (title, author, content, parent_id)
            VALUES (?, ?, ?, ?)
            """,
            (story.title, story.author, story.content, story.parent_id)
        )
        
        conn.commit()
        story_id = cursor.lastrowid
        
        # 获取刚创建的故事
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict_from_row(row)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建故事失败: {str(e)}")

@app.get("/api/stories", response_model=List[StoryResponse])
def get_stories(approved_only: bool = False):
    """获取故事列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if approved_only:
            cursor.execute(
                "SELECT * FROM stories WHERE is_approved = 1 ORDER BY created_at DESC"
            )
        else:
            cursor.execute("SELECT * FROM stories ORDER BY created_at DESC")
        
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

@app.post("/api/stories/{story_id}/approve")
def approve_story(story_id: int, background_tasks: BackgroundTasks):
    """批准故事并触发视频生成"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查故事是否存在
        cursor.execute("SELECT * FROM stories WHERE id = ?", (story_id,))
        story = cursor.fetchone()
        
        if not story:
            conn.close()
            raise HTTPException(status_code=404, detail="故事不存在")
        
        # 标记为已批准,状态为生成中
        cursor.execute(
            """
            UPDATE stories 
            SET is_approved = 1, video_status = 'generating'
            WHERE id = ?
            """,
            (story_id,)
        )
        conn.commit()
        conn.close()
        
        # 后台任务:生成视频
        background_tasks.add_task(generate_video_task, story_id, story["content"])
        
        return {
            "message": "故事已批准,视频正在生成中...",
            "story_id": story_id,
            "status": "generating"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批准故事失败: {str(e)}")

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

