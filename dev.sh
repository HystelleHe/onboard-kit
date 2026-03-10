#!/bin/bash

# OnboardKit 开发环境启动脚本

set -e

echo "🚀 启动 OnboardKit 开发环境..."

# 检查是否在项目根目录
if [ ! -f "README.md" ]; then
    echo "❌ 请在项目根目录运行此脚本"
    exit 1
fi

# 启动数据库服务
echo "📦 启动数据库服务..."
docker-compose up -d postgres redis

# 等待数据库启动
echo "⏳ 等待数据库启动..."
sleep 5

# 后端开发
echo ""
echo "📘 后端开发指南："
echo "  cd backend"
echo "  python -m venv venv"
echo "  source venv/bin/activate  # Windows: venv\\Scripts\\activate"
echo "  pip install -r requirements.txt"
echo "  playwright install chromium"
echo "  cp .env.example .env  # 并修改配置"
echo "  uvicorn app.main:app --reload"
echo ""

# 前端开发
echo "📗 前端开发指南："
echo "  cd frontend"
echo "  npm install"
echo "  npm run dev"
echo ""

echo "✅ 数据库服务已启动"
echo "   PostgreSQL: localhost:5432"
echo "   Redis: localhost:6379"
echo ""
echo "停止数据库: docker-compose down"
