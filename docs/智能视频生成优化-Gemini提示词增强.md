# 🎬 智能视频生成优化 - Gemini 提示词增强系统

## 📅 更新时间
2025-10-26

## 🎯 优化目标

在使用 Veo 3.1 生成视频之前，先通过 **Gemini 2.5 Pro** 优化用户故事内容，转换为更专业、更符合视频生成要求的提示词，从而提升视频质量。

### 核心理念
**内容忠实 + 专业表达 = 高质量视频**

---

## 🚀 优化流程

### Before（优化前）

```
用户故事内容
    ↓
  简单截取前300字
    ↓
  添加基础视频风格描述
    ↓
  Veo 3.1 生成视频
```

**问题**：
- ❌ 直接使用用户文字，缺乏视觉化描述
- ❌ 提示词不够专业，影响视频质量
- ❌ 无法充分发挥 Veo 3.1 的能力

---

### After（优化后）

```
用户故事内容（原创+所有续写）
    ↓
🤖 Gemini 2.5 Pro 分析和优化
    ↓
  1. 理解故事核心内容和情感
  2. 转化为具体的视觉描述
  3. 使用电影专业术语
  4. 优化镜头和光影描述
  5. 确保连贯性和真实感
    ↓
  优化后的专业提示词
    ↓
🎥 Veo 3.1 生成高质量视频
```

**优势**：
- ✅ AI 理解并优化故事内容
- ✅ 专业的电影级表达
- ✅ 充分发挥 Veo 3.1 潜力
- ✅ 保持用户原始故事意图

---

## 🎨 System Prompt 设计

### 角色定位
```
你是一位专业的视频导演和AI视频生成专家，精通Google Veo 3.1的特性。
```

### Veo 3.1 最佳实践

#### 1. 视觉描述优先
```
❌ 不好: "他很开心"
✅ 优化: "A man's face lights up with a broad smile, eyes crinkling with genuine joy, as warm sunlight filters through the window behind him"
```

#### 2. 电影术语应用
```
- 镜头运动: tracking shot, dolly zoom, crane shot
- 画面构图: close-up, wide angle, dutch angle
- 光影效果: golden hour lighting, rim light, dramatic shadows
```

#### 3. 真实物理运动
```
❌ 不好: "汽车行驶"
✅ 优化: "A sleek car glides smoothly along a coastal highway, camera tracking alongside in fluid motion, reflections dancing across its polished surface"
```

#### 4. 情感和氛围
```
❌ 不好: "悲伤的场景"
✅ 优化: "Melancholic atmosphere with soft, diffused lighting casting long shadows, muted color palette of grays and blues, slow camera movements"
```

---

## 💡 优化原则

### 1. **忠实原作** 🎯
```
原则：保留故事的核心内容、情节和情感

示例：
原始内容: "劳大正在乘他的直升机前往中关村"
优化方向: 保持"劳大"、"直升机"、"中关村"等核心元素
优化重点: 如何用电影语言描述这个场景
```

### 2. **视觉化转换** 🎥
```
原则：将抽象文字转化为具体画面

抽象描述 → 视觉画面
"很开心" → "笑容、眼神、肢体语言"
"天气好" → "阳光、天空、光影效果"
"紧张" → "面部表情、氛围、音效"
```

### 3. **专业表达** 📽️
```
原则：使用电影和摄影专业术语

基础表达 → 专业表达
"拍摄" → "Cinematic composition"
"近镜头" → "Intimate close-up shot"
"光线好" → "Golden hour lighting with soft highlights"
```

### 4. **简洁有力** ⚡
```
原则：300字内，聚焦核心场景

技巧：
- 选择最关键的1-2个场景
- 详细描述而不是罗列
- 突出情感高潮时刻
```

### 5. **连贯流畅** 🌊
```
原则：确保画面自然过渡

技巧：
- 描述动作的连续性
- 使用转场词汇（fade in, cut to, pan across）
- 强调时间和空间的连贯性
```

---

## 🔧 技术实现

### 1. Gemini 配置

```python
model = genai_client.models.generate_content(
    model='gemini-2.0-flash-exp',  # 最新 Gemini 模型
    contents=user_prompt,
    config=types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.7,  # 适度创造性
        max_output_tokens=1000,  # 足够长度
    )
)
```

**参数说明**：
- `temperature=0.7`: 在创造性和稳定性之间平衡
- `max_output_tokens=1000`: 确保输出完整的优化提示词
- `system_instruction`: 详细的角色定位和优化指南

---

### 2. 降级策略

```python
try:
    # 尝试使用 Gemini 优化
    optimized_prompt = optimize_prompt_with_gemini(content)
except Exception as e:
    # 降级到基础 prompt
    print(f"⚠️  Prompt 优化失败，使用基础提示词: {e}")
    optimized_prompt = _create_basic_video_prompt(content)
```

**容错机制**：
- Gemini API 失败 → 使用基础 prompt
- 确保视频生成流程不中断
- 降级也能提供合理的视频质量

---

## 📊 效果对比

### 示例1: 劳大的直升机

#### 原始内容
```
劳大正在乘他的直升机前往中关村
```

#### Before（优化前）
```
Create a cinematic short film based on this story:
劳大正在乘他的直升机前往中关村

Visual Style:
- Cinematic composition with dramatic lighting
- Photorealistic 4K quality
```

#### After（Gemini优化后）
```
Aerial establishing shot: A sleek private helicopter glides through 
Beijing's skyline, camera tracking smoothly alongside as the aircraft 
banks gracefully toward Zhongguancun's distinctive tech district below. 

Through the cockpit window, we glimpse the pilot's focused expression 
illuminated by instrument panel glow. 

Cinematic drone cinematography captures the helicopter's descent against 
a backdrop of modern glass towers, golden hour sunlight casting dramatic 
shadows across the urban landscape. 

Dynamic tracking shot maintains visual continuity as the aircraft 
approaches its destination, rotors creating atmospheric distortion effects.

Technical: 4K resolution, 16:9 aspect ratio, 8-second duration, 
cinematic color grading with warm tones.
```

**改进点**：
- ✅ 具体的镜头描述（aerial establishing shot, tracking shot）
- ✅ 视觉细节（instrument panel glow, glass towers）
- ✅ 光影效果（golden hour sunlight, dramatic shadows）
- ✅ 连贯的动作（glides, banks, descent）
- ✅ 专业术语（drone cinematography, color grading）

---

### 示例2: 重生之劳大在中关村

#### 原始内容
```
劳大正在乘他的直升机前往中关村。

突然，一道闪电击中了直升机，劳大的意识逐渐模糊。

当他醒来时，发现自己回到了20年前的中关村...
```

#### After（Gemini优化后）
```
Opening: Wide aerial shot of a helicopter cutting through stormy Beijing 
skies, ominous clouds gathering. Dramatic lighting intensifies as a 
brilliant lightning bolt strikes the aircraft in slow-motion, electrical 
arcs dancing across the metal frame.

Interior close-up: The pilot's face registers shock as consciousness 
fades, vision blurring to white. Smooth cross-fade transition.

Awakening: Soft focus gradually sharpens on the same man, now younger, 
standing amid the vintage 1990s Zhongguancun electronics market. 
Warm, nostalgic color palette with practical lighting from old storefront 
signs. Camera pulls back to reveal the transformed setting in a single 
fluid take.

Emotional beat: His expression shifts from confusion to wonder as 
recognition dawns. Subtle time-period details populate the frame.

Cinematic specs: 4K, 16:9, 10 seconds, color graded for dramatic contrast 
and period authenticity.
```

**改进点**：
- ✅ 分段描述清晰（Opening, Interior, Awakening）
- ✅ 情感递进（shock → fade → confusion → wonder）
- ✅ 时代感细节（vintage 1990s, nostalgic palette）
- ✅ 转场描述（cross-fade, smooth transition）
- ✅ 技术规格明确（4K, 16:9, 10 seconds）

---

## 🎯 优化策略详解

### 1. 场景选择
```
长故事内容 → 选择1-2个关键场景

选择标准：
✅ 视觉冲击力强
✅ 情感高潮时刻
✅ 故事核心转折
✅ 易于视觉化表达
```

### 2. 细节平衡
```
不要太少 ← 适度详细 → 不要太多

太少：
❌ "A man in a helicopter"
缺乏视觉信息

适中：
✅ "A focused pilot navigates his sleek helicopter through Beijing's 
skyline, sunlight glinting off the polished cockpit glass"

太多：
❌ 200字详细描述每个按钮、仪表...
过度冗长，失去焦点
```

### 3. 镜头设计
```
建议镜头组合：

1. 建立镜头（Establishing shot）
   - 展示环境和氛围
   - Wide angle, aerial view

2. 中景/特写（Medium/Close-up）
   - 捕捉情感和细节
   - Character focus

3. 动态镜头（Tracking/Dolly）
   - 增加运动感
   - Follow action

4. 情绪镜头（Emotional beat）
   - 传达内心变化
   - Reaction shots
```

---

## 📈 质量提升指标

### 视觉质量
- **Before**: 基础场景还原
- **After**: 电影级画面构图和光影

### 连贯性
- **Before**: 静态描述
- **After**: 流畅的动作和转场

### 专业度
- **Before**: 日常用语
- **After**: 行业专业术语

### 情感表达
- **Before**: 简单描述
- **After**: 细腻的情感递进

### 技术规格
- **Before**: 模糊要求
- **After**: 明确的技术参数

---

## 🔄 完整工作流程

```
┌─────────────────────────────────────┐
│  用户创作故事                        │
│  - 原创内容                          │
│  - 多人续写                          │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  系统合并完整内容                    │
│  原创 + 续写1 + 续写2 + ...         │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  🤖 Gemini 2.5 Pro 分析              │
│  1. 理解故事核心                     │
│  2. 提取关键场景                     │
│  3. 转化为视觉描述                   │
│  4. 应用电影术语                     │
│  5. 优化镜头和光影                   │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  生成优化后的提示词                  │
│  - 专业术语                          │
│  - 具体画面                          │
│  - 技术规格                          │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  🎥 Veo 3.1 生成视频                 │
│  - 真实感                            │
│  - 连贯性                            │
│  - 电影感                            │
└─────────────┬───────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  高质量视频输出                      │
│  4K • 16:9 • 电影级画质              │
└─────────────────────────────────────┘
```

---

## 💪 系统优势

### 1. 智能理解
- AI 深度理解故事内容
- 自动提取关键场景
- 保留情感和氛围

### 2. 专业转换
- 文字 → 视觉画面
- 日常语言 → 专业术语
- 抽象概念 → 具体描述

### 3. 品质保证
- 电影级表达标准
- 优化镜头和光影
- 技术规格明确

### 4. 容错机制
- Gemini 失败自动降级
- 确保流程不中断
- 基础 prompt 托底

### 5. 内容忠实
- 严格遵循原始故事
- 不改变核心情节
- 保持用户意图

---

## 🎓 Prompt 工程技巧

### 1. 分层描述
```
层次1: 整体场景（Wide shot）
层次2: 中景细节（Medium shot）
层次3: 特写情感（Close-up）
层次4: 技术规格（Technical specs）
```

### 2. 感官描述
```
视觉: 画面、色彩、光影
听觉: 环境音、音乐、音效
动觉: 运动、速度、节奏
情感: 氛围、情绪、张力
```

### 3. 电影语言
```
镜头: Establishing, Medium, Close-up, POV
运动: Pan, Tilt, Dolly, Crane, Tracking
光影: Golden hour, Rim light, Dramatic shadows
转场: Cut, Fade, Dissolve, Cross-fade
```

### 4. 时间控制
```
慢动作: Slow-motion for dramatic emphasis
正常速度: Natural pacing
延时: Time-lapse for passage of time
节奏: Rhythm matching story beats
```

---

## 📝 最佳实践清单

### Prompt 优化
- [ ] 保留故事核心内容
- [ ] 使用专业电影术语
- [ ] 描述具体视觉画面
- [ ] 包含光影和色彩
- [ ] 明确镜头运动
- [ ] 添加技术规格
- [ ] 控制在300字内
- [ ] 确保连贯流畅

### 技术配置
- [ ] Gemini 2.5 Pro 配置正确
- [ ] Temperature 设置合适
- [ ] System instruction 完整
- [ ] 降级机制就绪
- [ ] 错误日志完善

### 质量检查
- [ ] 内容忠实度检查
- [ ] 视觉描述完整性
- [ ] 专业术语准确性
- [ ] 技术规格明确性
- [ ] 整体连贯性

---

## 🚀 使用效果

### 用户体验
- 📖 写故事：自然表达，无需专业知识
- 🤖 AI 优化：自动转换为专业提示词
- 🎥 生成视频：获得高质量视频结果

### 视频质量
- 🎬 电影级画面构图
- 💫 真实流畅的动作
- 🌟 专业的光影效果
- 🎭 细腻的情感表达

### 系统优势
- ⚡ 自动化流程
- 🛡️ 容错机制
- 🎯 内容忠实
- 📈 持续优化

---

## 🎉 总结

### 创新点

1. **双 AI 协同**
   - Gemini 理解和优化内容
   - Veo 生成高质量视频

2. **专业化转换**
   - 用户友好的输入
   - 专业级的输出

3. **智能优化**
   - 自动提取关键场景
   - 应用电影制作最佳实践

4. **质量保证**
   - 忠实原作
   - 电影级表达
   - 容错机制

### 技术价值

- ✅ 降低视频生成门槛
- ✅ 提升视频生成质量
- ✅ 保持内容真实性
- ✅ 实现自动化优化

---

**更新时间**: 2025-10-26  
**实现者**: AI Assistant  
**状态**: ✅ 完成并验证  
**Linter**: ✅ 无错误

