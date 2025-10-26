#!/bin/bash

echo "🎬 启动 StoryLink 平台..."
echo ""

# 检查环境变量
if [ ! -f .env ]; then
    echo "⚠️  警告: 未找到 .env 文件"
    echo "正在从 .env.example 创建 .env..."
    cp .env.example .env
    echo "✅ 请编辑 .env 文件填写 API Key"
    echo ""
fi

# 启动后端
echo "🚀 启动后端服务器 (端口 8000)..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🚀 启动前端开发服务器 (端口 3000)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ StoryLink 已启动!"
echo ""
echo "📍 访问地址:"
echo "   前端: http://localhost:3000"
echo "   后端 API: http://localhost:8000"
echo "   API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务..."

# 捕获 Ctrl+C
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 保持脚本运行
wait

