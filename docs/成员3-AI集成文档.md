# 🤖 AI集成开发文档 - 成员3

**开发者**: AI集成工程师  
**分支名称**: `feat/ai-enhancement-<你的名字>`  
**开发周期**: 1-2天  
**核心职责**: AI功能增强、Prompt优化、视频生成优化

---

## 📋 任务清单

### 优先级 P0 (必须完成)

- [ ] 优化文本润色 Prompt
- [ ] 优化视频生成 Prompt
- [ ] 处理视频生成失败的重试机制
- [ ] 准备高质量的 Mock 视频
- [ ] 测试 API 调用稳定性

### 优先级 P1 (强烈建议)

- [ ] 实现多种润色风格（幽默、严肃、诗意）
- [ ] 添加故事续写建议功能
- [ ] 实现智能标题生成
- [ ] 优化 API 错误处理

### 优先级 P2 (时间充裕时)

- [ ] 实现故事相似度计算
- [ ] 添加内容安全检查
- [ ] 实现故事摘要生成
- [ ] 优化视频生成参数

---

## 🔌 当前 AI 服务架构

### 文件位置
`backend/ai_service.py`

### 当前函数

1. `polish_text(content: str) -> str` - 文本润色
2. `generate_video(content: str, story_id: int) -> str` - 视频生成
3. `_create_video_prompt(content: str) -> str` - 生成视频提示词
4. `create_mock_video()` - 创建 Mock 视频

---

## 🎨 任务1: 优化文本润色功能

### 1.1 多风格润色

在 `ai_service.py` 中添加：

```python
from enum import Enum

class PolishStyle(str, Enum):
    """润色风格枚举"""
    DEFAULT = "default"  # 默认：优化表达
    HUMOROUS = "humorous"  # 幽默风格
    POETIC = "poetic"  # 诗意风格
    DRAMATIC = "dramatic"  # 戏剧化
    SIMPLE = "simple"  # 简洁明了

def polish_text_with_style(content: str, style: PolishStyle = PolishStyle.DEFAULT) -> str:
    """
    使用指定风格润色文本
    
    Args:
        content: 原始文本
        style: 润色风格
        
    Returns:
        润色后的文本
    """
    if not openai_client:
        return f"{content}\n\n[AI 润色示例 - {style.value} 风格]"
    
    # 根据风格选择系统提示
    system_prompts = {
        PolishStyle.DEFAULT: """你是一个专业的故事编辑。你的任务是:
1. 优化故事的语言表达，使其更生动、流畅
2. 增强情感渲染和细节描写
3. 保持原故事的核心情节
4. 控制在原文 1.5 倍长度以内
5. 使用中文输出""",
        
        PolishStyle.HUMOROUS: """你是一个幽默的故事编辑。你的任务是:
1. 在保持故事主线的同时，加入幽默元素
2. 使用俏皮的语言、有趣的比喻
3. 适当添加轻松的对话或旁白
4. 保持积极、欢快的基调
5. 使用中文输出""",
        
        PolishStyle.POETIC: """你是一个文学编辑，擅长诗意化表达。你的任务是:
1. 使用优美、富有诗意的语言重写故事
2. 增加意境描写和情感细节
3. 运用修辞手法（比喻、拟人、排比等）
4. 营造唯美的氛围
5. 使用中文输出""",
        
        PolishStyle.DRAMATIC: """你是一个戏剧编辑。你的任务是:
1. 增强故事的戏剧张力和冲突
2. 强化情节的起承转合
3. 增加悬念和高潮
4. 使用更有力度的动词和形容词
5. 使用中文输出""",
        
        PolishStyle.SIMPLE: """你是一个追求简洁的编辑。你的任务是:
1. 用最简洁的语言重写故事
2. 删除冗余描写，保留核心情节
3. 使用短句，提高可读性
4. 控制在原文 0.8 倍长度以内
5. 使用中文输出"""
    }
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": system_prompts[style]
                },
                {
                    "role": "user",
                    "content": f"请润色以下故事:\n\n{content}"
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        polished = response.choices[0].message.content.strip()
        print(f"✅ 文本润色完成 (风格: {style.value})")
        return polished
    
    except Exception as e:
        print(f"❌ OpenAI 润色失败: {e}")
        return content

# 保持原函数兼容性
def polish_text(content: str) -> str:
    """默认风格润色（向后兼容）"""
    return polish_text_with_style(content, PolishStyle.DEFAULT)
```

### 1.2 更新后端 API

在 `backend/main.py` 中修改：

```python
class PolishRequest(BaseModel):
    content: str
    style: str = "default"  # default, humorous, poetic, dramatic, simple

@app.post("/api/polish")
def polish_story(request: PolishRequest):
    """AI 文本润色（支持多种风格）"""
    try:
        # 验证风格参数
        valid_styles = ["default", "humorous", "poetic", "dramatic", "simple"]
        if request.style not in valid_styles:
            raise HTTPException(
                status_code=400,
                detail=f"无效的风格参数，可选值: {', '.join(valid_styles)}"
            )
        
        # 调用润色函数
        from ai_service import polish_text_with_style, PolishStyle
        polished_content = polish_text_with_style(
            request.content,
            PolishStyle(request.style)
        )
        
        return {
            "polished_content": polished_content,
            "style": request.style
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文本润色失败: {str(e)}")
```

---

## 🎬 任务2: 优化视频生成

### 2.1 改进 Prompt 生成器

```python
def _create_video_prompt(content: str, duration: int = 5) -> str:
    """
    根据故事内容生成优化的视频提示词
    
    Args:
        content: 故事内容
        duration: 视频时长（秒），默认5秒
        
    Returns:
        优化的视频生成提示词
    """
    # 使用 GPT 生成优化的视频提示词
    if openai_client:
        try:
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """你是一个视频生成专家。根据故事内容，生成简洁但富有视觉表现力的英文视频提示词。

要求：
1. 使用简洁的英文描述关键视觉元素
2. 突出故事的情感氛围和核心场景
3. 包含具体的视觉细节（光线、颜色、构图）
4. 适合 5-10 秒的短视频
5. 避免过于复杂的叙事
6. 使用电影化的描述语言"""
                    },
                    {
                        "role": "user",
                        "content": f"故事内容：\n{content[:500]}\n\n请生成视频提示词："
                    }
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            core_prompt = response.choices[0].message.content.strip()
            print(f"📝 生成视频提示词: {core_prompt}")
        
        except Exception as e:
            print(f"⚠️  提示词优化失败，使用基础版本: {e}")
            core_prompt = content[:200]
    else:
        core_prompt = content[:200]
    
    # 添加技术参数
    prompt = f"""{core_prompt}

Visual Quality:
- Cinematic composition with professional framing
- Dramatic lighting and natural shadows
- Photorealistic 4K quality
- Smooth camera movement
- Rich color grading
- Atmospheric depth of field

Technical Requirements:
- Duration: {duration}-{duration+3} seconds
- Aspect ratio: 16:9
- Smooth transitions
- Ambient sound design
- Professional cinematography
""".strip()
    
    return prompt
```

### 2.2 添加视频生成重试机制

```python
import time
from typing import Optional

def generate_video_with_retry(
    content: str,
    story_id: int,
    max_retries: int = 3
) -> str:
    """
    带重试机制的视频生成
    
    Args:
        content: 故事内容
        story_id: 故事ID
        max_retries: 最大重试次数
        
    Returns:
        视频文件路径
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            print(f"🎬 尝试生成视频 (attempt {attempt + 1}/{max_retries})...")
            return _generate_video_core(content, story_id)
        
        except TimeoutError as e:
            last_error = e
            print(f"⏰ 生成超时，准备重试...")
            time.sleep(5)  # 等待5秒后重试
        
        except Exception as e:
            last_error = e
            print(f"❌ 生成失败: {e}")
            
            # 某些错误不需要重试
            if "API key" in str(e) or "quota" in str(e).lower():
                print("⚠️  API 配置问题，不再重试")
                break
            
            time.sleep(5)
    
    # 所有重试都失败，返回 Mock 视频
    print(f"❌ 视频生成失败（已重试 {max_retries} 次）: {last_error}")
    print("📺 使用 Mock 视频代替")
    return "/videos/mock_video.mp4"


def _generate_video_core(content: str, story_id: int) -> str:
    """
    核心视频生成逻辑（从原 generate_video 函数提取）
    """
    # 1. 生成视频提示词
    prompt = _create_video_prompt(content)
    
    print(f"🎬 开始生成视频 (story_id={story_id})...")
    print(f"提示词: {prompt[:200]}...")
    
    # 2. 调用 Google Veo API
    operation = genai_client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
    )
    
    # 3. 轮询等待视频生成完成
    retry_count = 0
    max_retries = 60  # 最多等待 10 分钟
    
    while not operation.done and retry_count < max_retries:
        print(f"⏳ 等待视频生成... ({retry_count * 10}s)")
        time.sleep(10)
        operation = genai_client.operations.get(operation)
        retry_count += 1
    
    if not operation.done:
        raise TimeoutError("视频生成超时（10分钟）")
    
    # 4. 检查是否有错误
    if hasattr(operation, 'error') and operation.error:
        raise Exception(f"视频生成失败: {operation.error}")
    
    # 5. 下载生成的视频
    if not hasattr(operation.response, 'generated_videos') or not operation.response.generated_videos:
        raise Exception("未返回生成的视频")
    
    generated_video = operation.response.generated_videos[0]
    video_filename = f"story_{story_id}_{int(time.time())}.mp4"
    video_path = VIDEO_DIR / video_filename
    
    # 下载视频文件
    genai_client.files.download(file=generated_video.video)
    generated_video.video.save(str(video_path))
    
    print(f"✅ 视频生成成功: {video_path}")
    
    # 返回相对路径
    return f"/videos/{video_filename}"


# 更新原函数，使用重试版本
def generate_video(content: str, story_id: int) -> str:
    """
    使用 Google Veo 生成视频（带重试机制）
    """
    return generate_video_with_retry(content, story_id, max_retries=3)
```

---

## 🎥 任务3: 准备高质量 Mock 视频

### 3.1 下载或创建示例视频

```python
import subprocess
from pathlib import Path

def create_sample_video_ffmpeg():
    """
    使用 ffmpeg 创建一个5秒的示例视频
    需要安装: brew install ffmpeg (macOS)
    """
    output_path = VIDEO_DIR / "mock_video.mp4"
    
    try:
        # 创建一个5秒的视频：渐变背景 + 文字
        subprocess.run([
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'color=c=blue:s=1920x1080:d=5',  # 蓝色背景，5秒
            '-vf', 'drawtext=text=\'StoryLink Demo Video\':fontsize=60:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2',
            '-y',  # 覆盖已存在的文件
            str(output_path)
        ], check=True, capture_output=True)
        
        print(f"✅ 使用 ffmpeg 创建示例视频: {output_path}")
        return True
    
    except FileNotFoundError:
        print("⚠️  ffmpeg 未安装，无法创建示例视频")
        return False
    except Exception as e:
        print(f"❌ 创建示例视频失败: {e}")
        return False


def download_sample_video():
    """
    从公共来源下载示例视频
    """
    import urllib.request
    
    # 使用公共域的示例视频
    video_urls = [
        "https://www.w3schools.com/html/mov_bbb.mp4",  # Big Buck Bunny
        "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
    ]
    
    output_path = VIDEO_DIR / "mock_video.mp4"
    
    for url in video_urls:
        try:
            print(f"📥 正在下载示例视频: {url}")
            urllib.request.urlretrieve(url, output_path)
            print(f"✅ 示例视频下载成功: {output_path}")
            return True
        except Exception as e:
            print(f"⚠️  下载失败: {e}")
            continue
    
    return False


def ensure_quality_mock_video():
    """
    确保有一个高质量的 Mock 视频
    """
    mock_path = VIDEO_DIR / "mock_video.mp4"
    
    # 检查是否已存在且足够大（大于 10KB）
    if mock_path.exists() and mock_path.stat().st_size > 10240:
        print(f"✅ Mock 视频已存在: {mock_path}")
        return
    
    # 尝试使用 ffmpeg 创建
    if create_sample_video_ffmpeg():
        return
    
    # 尝试下载
    if download_sample_video():
        return
    
    # 都失败了，创建最小的 Mock 视频
    print("⚠️  使用最小 Mock 视频")
    create_mock_video()


# 在模块加载时调用
ensure_quality_mock_video()
```

### 3.2 创建独立脚本

在 `backend/` 目录创建 `create_sample_video.py`:

```python
#!/usr/bin/env python3
"""
创建高质量的示例视频脚本
运行: python create_sample_video.py
"""
import subprocess
import sys
from pathlib import Path

VIDEO_DIR = Path("videos")
VIDEO_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = VIDEO_DIR / "mock_video.mp4"

def create_video_with_ffmpeg():
    """使用 ffmpeg 创建示例视频"""
    try:
        # 创建一个10秒的视频
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', 'color=c=#667eea:s=1920x1080:d=10:r=30',  # 渐变紫色背景
            '-f', 'lavfi',
            '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',  # 音频
            '-vf', (
                "drawtext=text='StoryLink':"
                "fontsize=80:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-50,"
                "drawtext=text='AI驱动的故事创作平台':"
                "fontsize=40:fontcolor=white@0.8:x=(w-text_w)/2:y=(h-text_h)/2+50"
            ),
            '-shortest',
            '-pix_fmt', 'yuv420p',  # 兼容性
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-t', '10',
            '-y',
            str(OUTPUT_FILE)
        ]
        
        print("🎬 正在创建示例视频...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ 视频创建成功: {OUTPUT_FILE}")
            print(f"📊 文件大小: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")
            return True
        else:
            print(f"❌ 创建失败: {result.stderr}")
            return False
    
    except FileNotFoundError:
        print("❌ 未找到 ffmpeg，请先安装:")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        return False
    except Exception as e:
        print(f"❌ 创建视频失败: {e}")
        return False


if __name__ == "__main__":
    success = create_video_with_ffmpeg()
    sys.exit(0 if success else 1)
```

给脚本添加执行权限：
```bash
chmod +x backend/create_sample_video.py
```

---

## 🎯 任务4: 添加故事续写建议

```python
def suggest_continuation(content: str, num_suggestions: int = 3) -> list:
    """
    基于故事内容生成续写建议
    
    Args:
        content: 当前故事内容
        num_suggestions: 建议数量
        
    Returns:
        续写建议列表
    """
    if not openai_client:
        return [
            "主角遇到了一个神秘的陌生人...",
            "突然，天空中出现了异样的光芒...",
            "这时，一个意外的消息传来..."
        ]
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"""你是一个创意故事顾问。基于给定的故事内容，提供 {num_suggestions} 个有趣的续写方向。

要求：
1. 每个建议 30-50 字
2. 要有悬念或转折
3. 多样化的发展方向
4. 激发读者的创作欲望
5. 使用中文
6. 只返回建议内容，用换行符分隔"""
                },
                {
                    "role": "user",
                    "content": f"故事内容:\n{content}\n\n请提供续写建议:"
                }
            ],
            temperature=0.9,
            max_tokens=300
        )
        
        suggestions_text = response.choices[0].message.content.strip()
        suggestions = [s.strip() for s in suggestions_text.split('\n') if s.strip()]
        
        # 清理编号
        suggestions = [s.lstrip('0123456789.、 ') for s in suggestions]
        
        print(f"💡 生成了 {len(suggestions)} 个续写建议")
        return suggestions[:num_suggestions]
    
    except Exception as e:
        print(f"❌ 生成续写建议失败: {e}")
        return []
```

### 4.1 添加 API 端点

在 `backend/main.py` 添加：

```python
@app.get("/api/stories/{story_id}/suggestions")
def get_story_suggestions(story_id: int):
    """获取故事续写建议"""
    try:
        # 获取故事内容
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT content FROM stories WHERE id = ?", (story_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="故事不存在")
        
        # 生成建议
        from ai_service import suggest_continuation
        suggestions = suggest_continuation(row["content"])
        
        return {
            "story_id": story_id,
            "suggestions": suggestions
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成建议失败: {str(e)}")
```

---

## 🔍 任务5: 内容安全检查

```python
def check_content_safety(content: str) -> dict:
    """
    检查内容是否安全（使用 OpenAI Moderation API）
    
    Args:
        content: 待检查的内容
        
    Returns:
        检查结果 {"safe": bool, "categories": dict}
    """
    if not openai_client:
        return {"safe": True, "categories": {}}
    
    try:
        response = openai_client.moderations.create(input=content)
        result = response.results[0]
        
        return {
            "safe": not result.flagged,
            "categories": result.categories.model_dump() if hasattr(result.categories, 'model_dump') else {}
        }
    
    except Exception as e:
        print(f"⚠️  内容安全检查失败: {e}")
        # 检查失败时默认通过
        return {"safe": True, "categories": {}}
```

---

## 🧪 测试指南

### 1. 测试润色功能

```bash
# 测试默认风格
curl -X POST http://localhost:8000/api/polish \
  -H "Content-Type: application/json" \
  -d '{"content":"很久很久以前，有一个小村庄。","style":"default"}'

# 测试幽默风格
curl -X POST http://localhost:8000/api/polish \
  -H "Content-Type: application/json" \
  -d '{"content":"很久很久以前，有一个小村庄。","style":"humorous"}'
```

### 2. 测试续写建议

```bash
curl http://localhost:8000/api/stories/1/suggestions
```

### 3. 测试视频生成

```python
# 在 Python 中测试
from ai_service import generate_video

video_url = generate_video("一个关于勇气的故事...", 1)
print(f"视频路径: {video_url}")
```

---

## 📝 开发规范

### Git 提交
```bash
git commit -m "feat: add multi-style text polishing"
git commit -m "feat: improve video prompt generation"
git commit -m "feat: add retry mechanism for video generation"
git commit -m "feat: add story continuation suggestions"
```

### 日志规范
```python
print("✅ 成功")  # 成功操作
print("⏳ 处理中")  # 进行中
print("❌ 失败")  # 错误
print("⚠️  警告")  # 警告
print("💡 提示")  # 提示信息
```

---

## 📞 联系方式

**需要对接**:
- 后端开发（成员1）- API 集成
- 前端开发（成员2）- UI 功能对接
- 联调负责人（成员4）- 功能测试

**完成时间**: 第1天下午完成核心优化

