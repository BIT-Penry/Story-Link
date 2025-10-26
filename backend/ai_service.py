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
    
    流程：
    1. 使用 Gemini 2.5 Pro 优化故事内容为专业视频提示词
    2. 使用优化后的提示词调用 Veo 3.1 生成视频
    
    Args:
        content: 故事内容（原创+所有续写）
        story_id: 故事 ID
        
    Returns:
        视频文件路径
    """
    try:
        print(f"🎬 开始生成视频 (story_id={story_id})...")
        print(f"📖 原始故事内容长度: {len(content)} 字")
        
        # 1. 使用 Gemini 2.5 Pro 优化提示词
        print(f"🤖 第一步：使用 Gemini 优化视频提示词...")
        optimized_prompt = optimize_prompt_with_gemini(content)
        
        print(f"✅ 提示词优化完成")
        print(f"📝 优化后提示词: {optimized_prompt[:300]}...")
        
        # 2. 使用优化后的提示词调用 Google Veo API
        print(f"🎥 第二步：使用 Veo 3.1 生成视频...")
        operation = genai_client.models.generate_videos(
            model="veo-3.1-generate-preview",
            prompt=optimized_prompt,
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


def optimize_prompt_with_gemini(content: str) -> str:
    """
    使用 Gemini 2.5 Pro 优化视频生成提示词
    
    将用户的故事内容转换为更适合 Veo 3.1 的专业视频提示词
    
    Args:
        content: 用户创作的故事内容（原创+所有续写）
        
    Returns:
        优化后的视频生成提示词
    """
    try:
        # System Prompt: 指导 Gemini 如何优化 prompt
        system_instruction = """你是专业的电影导演和 AI 视频生成专家，精通 Google Veo 3 的提示词规范。

## 你的任务
将用户的故事转换为符合 Veo 3 官方规范的高质量视频生成提示词。

## Veo 3 官方提示词结构（必须严格遵循）

提示词必须包含以下元素，按顺序组织：

### 1. 主体（Subject）- 必需
描述视频中出现的对象、人物、动物或场景。
- 例如：a businessman, a helicopter, cityscape, modern buildings
- 具体明确，避免模糊描述

### 2. 动作（Action）- 必需
描述主体正在做什么。
- 例如：walking through, flying over, turning around, ascending
- 使用动态动词，描述连续的动作流程
- **关键**：确保动作连贯流畅，情节不断开

### 3. 风格（Style）- 推荐
指定创意方向和视觉风格。
- 电影风格：cinematic, sci-fi, noir, documentary, thriller
- 画面质感：photorealistic, dramatic, atmospheric, epic
- 例如：cinematic thriller style, photorealistic documentary aesthetic

### 4. 相机定位和运动（Camera Position & Movement）- 推荐
使用专业术语控制相机。
- 定位：aerial shot, eye-level, bird's eye view, low angle
- 运动：tracking shot, dolly in, crane shot, pan across, steady cam
- 例如：aerial tracking shot following the subject

### 5. 构图（Composition）- 可选
指定镜头取景方式。
- wide shot, medium shot, close-up, extreme close-up
- two-shot, over-the-shoulder, establishing shot
- 例如：wide establishing shot transitioning to medium close-up

### 6. 对焦和镜头效果（Focus & Lens Effects）- 可选
实现特定视觉效果。
- 景深：shallow depth of field, deep focus
- 镜头类型：macro lens, wide-angle lens, telephoto
- 效果：soft focus, rack focus, lens flare
- 例如：shallow depth of field with cinematic bokeh

### 7. 氛围（Atmosphere）- 推荐
描述颜色、光线和整体情绪。
- 光线：golden hour, blue hour, dramatic shadows, rim lighting
- 色调：warm tones, cool blue palette, high contrast
- 情绪：mysterious, uplifting, melancholic, tense
- 例如：golden hour lighting with warm atmospheric haze

## 优化原则

1. **内容忠实**：必须保留用户故事的核心情节和情感
2. **动作连贯**：确保描述的动作流畅连续，情节不断开
3. **结构规范**：严格按照上述 7 个元素的顺序组织
4. **具体明确**：避免抽象概念，使用具体的视觉描述
5. **专业术语**：使用电影和摄影的标准术语
6. **长度适中**：控制在 500-800 字，足够详细但不冗余

## 输出格式

直接输出英文提示词，按以下结构组织：

Subject: [主体描述]
Action: [动作描述，确保连贯]
Style: [风格定义]
Camera: [相机定位和运动]
Composition: [构图方式]
Focus/Lens: [对焦和镜头效果]
Atmosphere: [氛围和光线]

Technical specs: 30-second duration, 16:9 aspect ratio, 4K cinematic quality.

不要添加任何解释或前缀，直接输出优化后的提示词。"""

        user_prompt = f"""请将以下故事内容转换为符合 Veo 3 官方规范的视频生成提示词：

【故事内容】
{content}

【转换要求】
1. 严格按照 Veo 3 的 7 个元素结构输出（Subject, Action, Style, Camera, Composition, Focus/Lens, Atmosphere）
2. 确保情节连贯流畅，动作不断开
3. 保持故事的核心内容和情感完整性
4. 使用专业的电影和摄影术语
5. 控制在 500-800 字，足够详细
6. 技术规格：30秒时长，16:9 比例，4K 电影级画质
7. 直接输出英文提示词，按规定格式组织，无需额外解释

现在开始转换：
正例：一个广角镜头，拍摄的是雾气弥漫的太平洋西北森林。两名疲惫的徒步者（一男一女）在蕨类植物丛中艰难前行，突然，男士停下脚步，盯着一棵树。特写：树皮上留有新鲜的深爪印。男士：（手放在猎刀上）“那不是普通的熊。”Woman：（声音因恐惧而紧绷，目光扫视着树林）“那是什么？”粗糙的树皮、折断的树枝、潮湿泥土上的脚步声。一只孤零零的鸟在鸣叫。
反例：剪纸动画。新图书管理员：“禁书放在哪里？”老馆长：“我们没有。他们会留着我们。”"""

        # 使用 Gemini 2.5 Pro 优化
        print(f"🤖 使用 Gemini 2.5 Pro 优化视频提示词...")
        
        response = genai_client.models.generate_content(
            model='gemini-2.0-flash-exp',  # 使用 Gemini 2.0 Flash（更稳定）
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,  # 适度创造性
                max_output_tokens=1000,
            )
        )
        
        # 正确解析响应
        if not response or not hasattr(response, 'text'):
            print(f"⚠️  Gemini 返回空响应")
            raise ValueError("Gemini API 返回空响应")
        
        optimized_prompt = response.text
        
        if not optimized_prompt or optimized_prompt.strip() == "":
            print(f"⚠️  Gemini 返回空文本")
            raise ValueError("Gemini 返回空文本")
        
        optimized_prompt = optimized_prompt.strip()
        
        print(f"✅ Prompt 优化完成")
        print(f"📝 优化后的提示词（前200字）: {optimized_prompt[:1000]}...")
        
        return optimized_prompt
    
    except Exception as e:
        print(f"⚠️  Prompt 优化失败，使用基础提示词: {e}")
        # 如果优化失败，降级使用基础 prompt
        return _create_basic_video_prompt(content)


def _create_basic_video_prompt(content: str) -> str:
    """
    创建基础视频提示词（降级方案，符合 Veo 3 官方规范）
    
    Args:
        content: 故事内容
        
    Returns:
        基础视频生成提示词
    """
    # 取故事前 1000 字
    story_summary = content[:1000] if len(content) > 1000 else content
    
    # 使用 Veo 3 官方结构创建基础提示词
    prompt = f"""
Subject: The key characters and scenes from the following story: {story_summary[:200]}

Action: Characters perform continuous, fluid actions that advance the narrative naturally. All movements flow seamlessly from one to another without breaks, maintaining story coherence throughout the entire sequence.

Style: Cinematic photorealistic aesthetic with dramatic storytelling elements. Professional film production quality with emotional depth and atmospheric visual treatment.

Camera: Smooth tracking shots and dynamic camera movements. Mix of establishing wide shots, medium shots for character interaction, and expressive close-ups for emotional moments. Professional steadicam work with fluid transitions.

Composition: Balanced cinematic framing with rule-of-thirds composition. Establishing shots transition smoothly to medium and close-up shots, creating visual variety while maintaining narrative flow.

Focus/Lens: Shallow depth of field for subject emphasis with cinematic bokeh. Professional lens quality with natural focus transitions and subtle rack focus for visual storytelling.

Atmosphere: Dramatic lighting with natural color grading. Atmospheric haze and volumetric lighting create mood. Warm or cool tones as appropriate to the story's emotional arc, with high production value cinematography.

Technical specs: 30-second duration, 16:9 aspect ratio, 4K cinematic quality, professional color grading.
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

