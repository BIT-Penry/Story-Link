#!/bin/bash

echo "📦 StoryLink 项目初始化..."
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python 3,请先安装 Python 3.9+"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到 Node.js,请先安装 Node.js 18+"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo ""

# 安装后端依赖
echo "📥 安装后端依赖..."
cd backend
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ 后端依赖安装失败"
    exit 1
fi
cd ..
echo "✅ 后端依赖安装完成"
echo ""

# 安装前端依赖
echo "📥 安装前端依赖..."
cd frontend
npm install
if [ $? -ne 0 ]; then
    echo "❌ 前端依赖安装失败"
    exit 1
fi
cd ..
echo "✅ 前端依赖安装完成"
echo ""

# 创建环境变量文件
if [ ! -f .env ]; then
    echo "📝 创建环境变量文件..."
    cp .env.example .env
    echo "✅ 已创建 .env 文件,请填写 API Key"
else
    echo "✅ .env 文件已存在"
fi
echo ""

# 创建视频目录
mkdir -p backend/videos
echo "✅ 创建视频目录"
echo ""

echo "🎉 项目初始化完成!"
echo ""
echo "📝 下一步:"
echo "   1. 编辑 .env 文件,填写 API Key"
echo "   2. 运行 ./start.sh 启动项目"
echo "   3. 访问 http://localhost:3000"
echo ""

