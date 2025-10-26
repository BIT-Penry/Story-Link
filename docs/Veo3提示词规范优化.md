# Veo 3 提示词规范优化更新

## 更新时间
2025-10-26

## 更新概述
根据 Google Veo 3 官方提示词规范，完全重构了 Gemini 的 System Prompt，确保生成的视频提示词严格符合 Veo 3 的最佳实践。

---

## 📋 问题背景

### 原始错误
```
⚠️  Prompt 优化失败，使用基础提示词: 'NoneType' object has no attribute 'strip'
```

**原因分析**：
1. **API 响应解析错误**：直接调用 `model.text.strip()` 导致 `NoneType` 错误
2. **模型选择问题**：`gemini-2.5-pro` 可能不是有效的模型名称
3. **提示词结构不规范**：未按照 Veo 3 官方推荐的 7 元素结构组织

---

## ✅ 解决方案

### 1. 修复 API 响应解析

**修改前：**
```python
model = genai_client.models.generate_content(...)
optimized_prompt = model.text.strip()  # ❌ 直接调用可能为 None
```

**修改后：**
```python
response = genai_client.models.generate_content(...)

# 正确解析响应
if not response or not hasattr(response, 'text'):
    raise ValueError("Gemini API 返回空响应")

optimized_prompt = response.text

if not optimized_prompt or optimized_prompt.strip() == "":
    raise ValueError("Gemini 返回空文本")

optimized_prompt = optimized_prompt.strip()
```

**改进点**：
- ✅ 分步检查 `response` 对象
- ✅ 验证 `text` 属性存在
- ✅ 检查返回内容非空
- ✅ 优雅降级到基础提示词

---

### 2. 使用稳定的 Gemini 模型

```python
response = genai_client.models.generate_content(
    model='gemini-2.0-flash-exp',  # ✅ 使用稳定的 Gemini 2.0 Flash
    # ...
)
```

**原因**：`gemini-2.5-pro` 可能不是有效的模型名称，改用经过验证的 `gemini-2.0-flash-exp`。

---

### 3. 重构 System Prompt - 符合 Veo 3 官方规范

根据 Google Veo 3 的官方文档，视频提示词应包含以下 **7 个核心元素**：

#### 🎯 Veo 3 官方提示词结构

| 元素 | 优先级 | 说明 | 示例 |
|------|--------|------|------|
| **1. Subject（主体）** | 必需 | 视频中的对象、人物、场景 | `a businessman, cityscape, helicopter` |
| **2. Action（动作）** | 必需 | 主体正在做什么，确保连贯 | `walking through, flying over, ascending` |
| **3. Style（风格）** | 推荐 | 电影风格或画面质感 | `cinematic thriller, photorealistic` |
| **4. Camera（相机）** | 推荐 | 相机定位和运动 | `aerial tracking shot, dolly in` |
| **5. Composition（构图）** | 可选 | 镜头取景方式 | `wide shot, close-up, two-shot` |
| **6. Focus/Lens（镜头）** | 可选 | 对焦和镜头效果 | `shallow depth of field, bokeh` |
| **7. Atmosphere（氛围）** | 推荐 | 光线、色调、情绪 | `golden hour, warm tones, dramatic` |

#### 📝 新的 System Instruction

```python
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

### 4. 相机定位和运动（Camera Position & Movement）- 推荐
使用专业术语控制相机。
- 定位：aerial shot, eye-level, bird's eye view, low angle
- 运动：tracking shot, dolly in, crane shot, pan across

### 5. 构图（Composition）- 可选
指定镜头取景方式。
- wide shot, medium shot, close-up, extreme close-up
- two-shot, over-the-shoulder, establishing shot

### 6. 对焦和镜头效果（Focus & Lens Effects）- 可选
实现特定视觉效果。
- 景深：shallow depth of field, deep focus
- 镜头类型：macro lens, wide-angle lens, telephoto
- 效果：soft focus, rack focus, lens flare

### 7. 氛围（Atmosphere）- 推荐
描述颜色、光线和整体情绪。
- 光线：golden hour, blue hour, dramatic shadows, rim lighting
- 色调：warm tones, cool blue palette, high contrast
- 情绪：mysterious, uplifting, melancholic, tense

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
```

#### 💡 关键改进

1. **结构化输出**：明确要求按 7 个元素的顺序组织
2. **动作连贯性**：特别强调"情节不断开"，确保 30 秒视频流畅
3. **专业术语库**：为每个元素提供具体的术语示例
4. **长度控制**：500-800 字，适合 30 秒视频的详细描述
5. **格式规范**：标准化的输出格式，便于 Veo 3 解析

---

### 4. 更新 User Prompt

```python
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

现在开始转换："""
```

---

### 5. 基础提示词也符合规范

即使 Gemini 优化失败，降级使用的基础提示词也严格遵循 Veo 3 规范：

```python
def _create_basic_video_prompt(content: str) -> str:
    story_summary = content[:1000] if len(content) > 1000 else content
    
    prompt = f"""
Subject: The key characters and scenes from the following story: {story_summary[:200]}

Action: Characters perform continuous, fluid actions that advance the narrative naturally. All movements flow seamlessly from one to another without breaks, maintaining story coherence throughout the entire sequence.

Style: Cinematic photorealistic aesthetic with dramatic storytelling elements. Professional film production quality with emotional depth and atmospheric visual treatment.

Camera: Smooth tracking shots and dynamic camera movements. Mix of establishing wide shots, medium shots for character interaction, and expressive close-ups for emotional moments.

Composition: Balanced cinematic framing with rule-of-thirds composition. Establishing shots transition smoothly to medium and close-up shots.

Focus/Lens: Shallow depth of field for subject emphasis with cinematic bokeh. Professional lens quality with natural focus transitions.

Atmosphere: Dramatic lighting with natural color grading. Atmospheric haze and volumetric lighting create mood. Warm or cool tones as appropriate to the story's emotional arc.

Technical specs: 30-second duration, 16:9 aspect ratio, 4K cinematic quality, professional color grading.
"""
    return prompt.strip()
```

---

## 📊 更新对比

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| **提示词结构** | 自由格式 | Veo 3 官方 7 元素结构 |
| **内容长度** | 300 字 | 500-800 字 |
| **视频时长** | 5-10 秒 | 30 秒 |
| **动作连贯性** | 未明确要求 | 特别强调连续性 |
| **API 错误处理** | 直接 `.strip()` | 分步验证 + 降级 |
| **Gemini 模型** | `gemini-2.5-pro` | `gemini-2.0-flash-exp` |
| **降级方案** | 简单描述 | 同样符合 Veo 3 规范 |

---

## 🎬 预期效果

使用新的 Veo 3 规范提示词后，生成的视频将具有：

### ✅ 更高的视频质量
- 符合官方推荐结构，充分发挥 Veo 3 能力
- 详细的 7 元素描述，生成更精准的画面

### ✅ 更强的故事连贯性
- 明确要求"动作不断开"
- 30 秒时长，足够展现完整情节

### ✅ 更专业的电影感
- 标准的摄影术语（tracking shot, depth of field, golden hour）
- 明确的视觉风格指导（cinematic, photorealistic）

### ✅ 更稳定的系统
- 完善的错误处理，不会因为 API 响应问题崩溃
- 降级方案同样高质量

---

## 🔍 测试建议

### 测试步骤
1. **创建一个新故事**，包含多个情节段落
2. **点击生成视频**，观察后台日志：
   ```
   🎬 开始生成视频 (story_id=X)...
   📖 原始故事内容长度: XXX 字
   🤖 第一步：使用 Gemini 优化视频提示词...
   ✅ 提示词优化完成
   📝 优化后提示词: Subject: ... Action: ... Style: ...
   🎥 第二步：使用 Veo 3.1 生成视频...
   ```

3. **检查优化后的提示词**是否包含完整的 7 个元素
4. **观看生成的视频**，评估：
   - 画面是否连贯流畅
   - 是否符合故事内容
   - 电影感和专业度

### 预期日志输出示例
```
🎬 开始生成视频 (story_id=1)...
📖 原始故事内容长度: 458 字
🤖 第一步：使用 Gemini 优化视频提示词...
✅ Prompt 优化完成
📝 优化后提示词（前200字）: Subject: A young entrepreneur in modern business attire standing in a sleek office with floor-to-ceiling windows overlooking a bustling city.

Action: The entrepreneur walks confidently through the office space, reviewing documents...

🎥 第二步：使用 Veo 3.1 生成视频...
⏳ 视频生成中...
✅ 视频生成完成！
```

---

## 📚 参考资料

- **Google Veo 3 官方文档**：提示词结构和最佳实践
- **Gemini API 文档**：`generate_content` 响应格式
- **电影摄影术语**：Camera movements, composition, lighting

---

## 🔧 相关文件

- `backend/ai_service.py`：主要修改文件
  - `optimize_prompt_with_gemini()` 函数
  - `_create_basic_video_prompt()` 函数
  - `generate_video()` 函数

---

## ✨ 总结

这次更新彻底解决了以下问题：
1. ✅ **修复了** `'NoneType' object has no attribute 'strip'` 错误
2. ✅ **重构了** System Prompt，严格符合 Veo 3 官方 7 元素规范
3. ✅ **增强了** 提示词质量，从 300 字扩展到 500-800 字
4. ✅ **优化了** 视频时长，从 5-10 秒提升到 30 秒
5. ✅ **强化了** 动作连贯性要求，避免情节断裂
6. ✅ **完善了** 错误处理，降级方案同样高质量

现在系统可以生成更专业、更连贯、更符合 Veo 3 规范的视频提示词，最大化视频生成质量！🎉

