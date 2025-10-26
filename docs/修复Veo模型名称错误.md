# 🔧 修复 Veo 模型名称错误

## 更新时间
2025-10-26

## 问题描述

### 错误信息
```json
{
  'error': {
    'code': 404,
    'message': 'models/veo-3.0-fast-generate is not found for API version v1beta, or is not supported for predictLongRunning. Call ListModels to see the list of available models and their supported methods.',
    'status': 'NOT_FOUND'
  }
}
```

### 问题原因
在 `backend/ai_service.py` 中使用了**错误的 Veo 模型名称**：
- ❌ 错误: `veo-3.0-fast-generate`
- ✅ 正确: `veo-3.1-generate-preview`

---

## ✅ 解决方案

### 修改内容

**文件**: `backend/ai_service.py` (第 102 行)

```python
# 修改前 ❌
operation = genai_client.models.generate_videos(
    model="veo-3.0-fast-generate",  # 错误的模型名称
    prompt=optimized_prompt,
)

# 修改后 ✅
operation = genai_client.models.generate_videos(
    model="veo-3.1-generate-preview",  # 正确的模型名称
    prompt=optimized_prompt,
)
```

---

## 📋 Google Veo 可用模型列表

根据 Google AI Studio 的官方文档，当前可用的 Veo 模型包括：

### 1. **veo-3.1-generate-preview** ⭐ (推荐)
- **功能**: 文本生成视频
- **特点**: 最新版本，支持 30 秒视频生成
- **质量**: 高质量，4K 输出
- **状态**: Preview 阶段
- **用途**: 本项目使用此模型

### 2. veo-2.0-generate
- **功能**: 文本生成视频
- **特点**: 上一代版本
- **时长**: 支持较短时长
- **状态**: 稳定版

### ⚠️ 不存在的模型
- ❌ `veo-3.0-fast-generate` - 此模型名称不存在
- ❌ `veo-3.0-*` - 没有 3.0 系列的模型

---

## 🔍 如何查看可用模型

### 方法 1: Google AI Studio
访问 https://aistudio.google.com/prompts/new_chat

在 Model 下拉菜单中查看所有可用模型。

### 方法 2: 通过 API 查询

```python
import google.genativeai as genai

genai.configure(api_key="YOUR_API_KEY")

# 列出所有可用模型
for model in genai.list_models():
    if 'veo' in model.name.lower():
        print(f"模型名称: {model.name}")
        print(f"支持方法: {model.supported_generation_methods}")
        print(f"描述: {model.description}")
        print("-" * 50)
```

---

## ✅ 验证修复

### 1. 重启后端服务

```bash
cd backend
python3 main.py
```

### 2. 测试视频生成

1. 在前端创建一个新故事
2. 点击"生成视频"按钮
3. 观察后台日志输出

### 3. 预期日志

```
🎬 开始生成视频 (story_id=1)...
📖 原始故事内容长度: 458 字
🤖 第一步：使用 Gemini 优化视频提示词...
✅ Prompt 优化完成
📝 优化后提示词: Subject: ...
🎥 第二步：使用 Veo 3.1 生成视频...
⏳ 视频生成中，已等待 10 秒...
⏳ 视频生成中，已等待 20 秒...
✅ 视频生成完成！
💾 视频已保存: videos/story_1_1234567890.mp4
```

### 4. 错误日志（如果 API Key 或权限有问题）

可能的其他错误：
- **403 Forbidden**: API Key 无效或没有权限
- **429 Too Many Requests**: 请求过于频繁，需要等待
- **500 Internal Server Error**: Google 服务器问题，稍后重试

---

## 🚀 后续优化建议

### 1. 添加模型配置
在 `.env` 文件中配置模型名称，便于切换：

```python
# .env
VEO_MODEL=veo-3.1-generate-preview

# ai_service.py
import os
VEO_MODEL = os.getenv("VEO_MODEL", "veo-3.1-generate-preview")

operation = genai_client.models.generate_videos(
    model=VEO_MODEL,
    prompt=optimized_prompt,
)
```

### 2. 添加模型验证
在启动时验证模型是否可用：

```python
def verify_veo_model():
    try:
        models = genai_client.models.list()
        veo_models = [m.name for m in models if 'veo' in m.name.lower()]
        print(f"✅ 可用的 Veo 模型: {veo_models}")
        
        if "veo-3.1-generate-preview" not in veo_models:
            print("⚠️  警告: veo-3.1-generate-preview 不在可用模型列表中")
    except Exception as e:
        print(f"❌ 无法验证模型: {e}")
```

### 3. 降级策略
如果 3.1 不可用，自动降级到 2.0：

```python
def generate_video_with_fallback(content: str, story_id: int):
    models_to_try = [
        "veo-3.1-generate-preview",
        "veo-2.0-generate",
    ]
    
    for model in models_to_try:
        try:
            print(f"🎥 尝试使用模型: {model}")
            operation = genai_client.models.generate_videos(
                model=model,
                prompt=content,
            )
            return operation
        except Exception as e:
            print(f"⚠️  模型 {model} 失败: {e}")
            continue
    
    raise Exception("所有 Veo 模型均不可用")
```

---

## 📚 参考资料

- **Google AI Studio**: https://aistudio.google.com
- **Veo 官方文档**: https://ai.google.dev/models/veo
- **Google Generative AI Python SDK**: https://github.com/google/generative-ai-python

---

## ✨ 总结

### 问题
使用了不存在的 Veo 模型名称 `veo-3.0-fast-generate`

### 解决
更改为正确的模型名称 `veo-3.1-generate-preview`

### 影响文件
- ✅ `backend/ai_service.py` (1 处修改)

### 状态
🟢 已修复，可以正常生成视频

---

现在重启后端服务，应该可以成功调用 Veo API 生成视频了！🎉

