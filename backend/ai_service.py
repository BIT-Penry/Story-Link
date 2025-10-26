"""
AI 服务模块
包含文本润色和视频生成功能
"""
import os
import time
from pathlib import Path
from openai import OpenAI
from google import genai
from google.genai import types
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# ========== OpenAI 配置 ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# ========== Google Genai 配置 ==========
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyD91kz0udBl80_u8dcmObWfAMh25Uqpjjg")
genai_client = genai.Client(api_key=GOOGLE_API_KEY)

# 视频保存目录
VIDEO_DIR = Path("videos")
VIDEO_DIR.mkdir(exist_ok=True)


def polish_text(content: str) -> str:
    """
    使用 GPT-4o-mini 润色文本
    
    Args:
        content: 原始文本
        
    Returns:
        润色后的文本
    """
    # 如果没有配置 OpenAI API,返回简单的示例
    if not openai_client:
        return f"{content}\n\n[AI 润色示例:增加了更生动的描写和情感细节]"
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """你是一个专业的故事编辑。你的任务是:
1. 优化故事的语言表达,使其更生动、流畅
2. 增强情感渲染和细节描写
3. 保持原故事的核心情节和风格
4. 控制在原文 1.5 倍长度以内
5. 使用中文输出"""
                },
                {
                    "role": "user",
                    "content": f"请润色以下故事:\n\n{content}"
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        polished = response.choices[0].message.content.strip()
        return polished
    
    except Exception as e:
        print(f"❌ OpenAI 润色失败: {e}")
        return content


def generate_video(content: str, story_id: int) -> str:
    """
    使用 Google Veo 生成视频
    
    Args:
        content: 故事内容
        story_id: 故事 ID
        
    Returns:
        视频文件路径
    """
    try:
        # 1. 生成视频提示词(简化版,直接用故事内容前300字)
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
            print(f"❌ 视频生成超时（等待了 {retry_count * 10} 秒）")
            raise TimeoutError("视频生成超时")
        
        print(f"✅ 操作完成，正在检查结果...")
        
        # 检查是否有错误
        if hasattr(operation, 'error') and operation.error:
            error_msg = f"API 返回错误: {operation.error}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        # 检查响应是否存在
        if not operation.response:
            print(f"❌ API 返回空响应")
            print(f"📊 Operation 状态: done={operation.done}")
            raise RuntimeError("API 返回空响应，可能需要配置 API 密钥或检查配额")
        
        # 检查是否有生成的视频
        if not hasattr(operation.response, 'generated_videos') or not operation.response.generated_videos:
            print(f"❌ API 未返回生成的视频")
            print(f"📊 Response 内容: {operation.response}")
            raise RuntimeError("API 未返回生成的视频")
        
        # 4. 下载生成的视频
        generated_video = operation.response.generated_videos[0]
        video_filename = f"story_{story_id}_{int(time.time())}.mp4"
        video_path = VIDEO_DIR / video_filename
        
        genai_client.files.download(file=generated_video.video)
        generated_video.video.save(str(video_path))
        
        print(f"✅ 视频生成成功: {video_path}")
        
        # 返回相对路径(供前端访问)
        return f"/videos/{video_filename}"
    
    except Exception as e:
        print(f"❌ 视频生成失败: {e}")
        import traceback
        traceback.print_exc()
        # 返回 Mock 视频路径
        return "/videos/mock_video.mp4"


def _create_video_prompt(content: str) -> str:
    """
    根据故事内容生成视频提示词
    
    Args:
        content: 故事内容
        
    Returns:
        视频生成提示词
    """
    # 简化版:取故事前 300 字,加上视频风格描述
    story_summary = content[:300] if len(content) > 300 else content
    
    prompt = f"""
Create a cinematic short film based on this story:

{story_summary}

Visual Style:
- Cinematic composition with dramatic lighting
- Photorealistic 4K quality
- Emotional and atmospheric
- Natural color grading
- Professional cinematography

Requirements:
- Duration: 5-10 seconds
- Aspect ratio: 16:9
- Show key emotional moments
- Include ambient sound design
""".strip()
    
    return prompt


# ========== Mock 数据(用于测试) ==========
def create_mock_video():
    """创建 Mock 视频文件(用于开发测试)"""
    mock_path = VIDEO_DIR / "mock_video.mp4"
    
    if not mock_path.exists():
        # 创建一个最小的有效 MP4 文件
        # 这是一个 1 秒的黑色视频的最小 MP4 结构
        minimal_mp4 = bytes([
            0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70,
            0x69, 0x73, 0x6F, 0x6D, 0x00, 0x00, 0x02, 0x00,
            0x69, 0x73, 0x6F, 0x6D, 0x69, 0x73, 0x6F, 0x32,
            0x6D, 0x70, 0x34, 0x31, 0x00, 0x00, 0x00, 0x08,
            0x66, 0x72, 0x65, 0x65
        ])
        
        mock_path.write_bytes(minimal_mp4)
        print(f"✅ 创建 Mock 视频: {mock_path}")


# 初始化时创建 Mock 视频
create_mock_video()

