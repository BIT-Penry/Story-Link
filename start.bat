@echo off
chcp 65001 >nul
echo 🎬 启动 StoryLink 平台...
echo.

REM 检查环境变量
if not exist .env (
    echo ⚠️  警告: 未找到 .env 文件
    echo 正在从 .env.example 创建 .env...
    copy .env.example .env
    echo ✅ 请编辑 .env 文件填写 API Key
    echo.
)

REM 启动后端
echo 🚀 启动后端服务器 (端口 8000)...
start "StoryLink Backend" cmd /k "cd backend && python main.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo 🚀 启动前端开发服务器 (端口 3000)...
start "StoryLink Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ StoryLink 已启动!
echo.
echo 📍 访问地址:
echo    前端: http://localhost:3000
echo    后端 API: http://localhost:8000
echo    API 文档: http://localhost:8000/docs
echo.
echo 关闭此窗口或按任意键退出...
pause >nul

