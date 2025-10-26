# 🔧 Bug 修复说明

## 问题描述

在运行过程中发现了以下问题：

1. **视频生成失败**: `'NoneType' object is not subscriptable`
   - 原因: Google Veo API 调用失败时没有正确处理错误

2. **视频文件 404**: `GET /videos/mock_video.mp4 HTTP/1.1" 404 Not Found`
   - 原因: FastAPI 没有配置静态文件服务

## 修复内容

### 1. 添加静态文件服务

在 `backend/main.py` 中添加:

```python
from fastapi.staticfiles import StaticFiles

# 挂载静态文件目录
app.mount("/videos", StaticFiles(directory="videos"), name="videos")
```

### 2. 创建有效的 Mock 视频

修改了 `backend/ai_service.py` 中的 `create_mock_video()` 函数，创建一个最小但有效的 MP4 文件。

### 3. 增强错误处理

添加了详细的错误追踪:

```python
except Exception as e:
    print(f"❌ 视频生成失败: {e}")
    import traceback
    traceback.print_exc()  # 打印完整错误堆栈
    return "/videos/mock_video.mp4"
```

## 如何应用修复

### 方法 1: 重启后端服务

```bash
# 停止当前后端服务 (Ctrl+C)

# 删除旧的 mock 视频
rm backend/videos/mock_video.mp4

# 重新启动后端
cd backend
python main.py
```

### 方法 2: 使用一键重启脚本

```bash
# 停止所有服务 (Ctrl+C)

# 重新运行
./start.sh
```

## 验证修复

1. **验证静态文件服务**:
   ```bash
   curl http://localhost:8000/videos/mock_video.mp4
   ```
   
   应该返回文件内容而不是 404

2. **验证视频生成**:
   - 创建一个故事
   - 点击"发布为视频"
   - 查看后端日志，应该显示详细的错误信息（如果失败）
   - 即使 API 失败，也会回退到 mock 视频

3. **验证视频播放**:
   - 在前端点击"观看视频"
   - 视频应该可以加载（虽然 mock 视频是空白的）

## 已知限制

### Mock 视频是最小文件

当前的 `mock_video.mp4` 是一个最小的有效 MP4 文件（约 40 字节），某些浏览器可能无法正确播放。

**解决方案**: 替换为真实视频

```bash
# 下载或复制一个真实的示例视频
cp /path/to/your/sample.mp4 backend/videos/mock_video.mp4

# 或使用提供的脚本创建
cd backend
python create_sample_video.py
```

### Google Veo API 调用可能失败

如果 Google API Key 未配置或无效，视频生成会自动回退到 mock 视频。

**解决方案**:

1. 确保 `.env` 文件配置正确:
   ```env
   GOOGLE_API_KEY=your_actual_api_key
   ```

2. 检查 API Key 的权限和配额

3. 查看详细错误日志:
   ```bash
   cd backend
   python main.py 2>&1 | tee backend.log
   ```

## 演示建议

由于视频生成需要时间（2-5 分钟），建议演示时：

### 选项 A: 提前生成视频

```bash
# 提前创建几个故事并生成视频
# 演示时直接展示已生成的视频
```

### 选项 B: 准备真实示例视频

```bash
# 准备一个 5-10 秒的示例视频
cp your_demo_video.mp4 backend/videos/mock_video.mp4

# 或者从网上下载示例
# 搜索: "free stock video clips" 或 "sample mp4 video"
```

### 选项 C: 展示生成过程

```bash
# 演示时点击"发布为视频"
# 讲解系统正在调用 Google Veo API
# 说明通常需要 2-5 分钟完成
# 然后切换到预先生成的视频展示最终效果
```

## 进一步优化

如果有时间，可以考虑：

1. **添加视频进度条**
   ```python
   # 返回生成进度百分比
   {"status": "generating", "progress": 45}
   ```

2. **WebSocket 实时推送**
   ```python
   # 视频生成完成后主动通知前端
   await websocket.send_json({"status": "completed", "url": "..."})
   ```

3. **队列管理**
   ```python
   # 使用 Celery 或 RQ 管理视频生成队列
   from celery import Celery
   ```

4. **缓存机制**
   ```python
   # 相同内容的故事共享同一个视频
   video_hash = hashlib.md5(content.encode()).hexdigest()
   ```

## 测试清单

- [x] 后端启动成功
- [x] 静态文件可访问 (`/videos/mock_video.mp4`)
- [x] 创建故事功能正常
- [x] AI 润色功能正常
- [x] Fork 功能正常
- [x] 发布为视频功能正常（回退到 mock）
- [x] 视频播放功能正常
- [ ] 真实视频生成测试（需要有效的 API Key）

## 联系支持

如果遇到其他问题，请检查：

1. **后端日志**: 查看 `python main.py` 的输出
2. **前端控制台**: 浏览器 F12 -> Console
3. **网络请求**: 浏览器 F12 -> Network

常见错误代码：
- `404`: 路径不存在，检查静态文件配置
- `500`: 服务器错误，查看后端日志
- `CORS`: 跨域问题，检查 CORS 配置

---

**修复完成!** 🎉

重启后端服务即可生效。

