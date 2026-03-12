#!/bin/bash

# OnboardKit 初始化脚本

set -e

echo "🚀 OnboardKit 初始化脚本"
echo "=========================="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装 Docker"
    echo "请访问 https://www.docker.com/get-started 安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未安装 Docker Compose"
    echo "请访问 https://docs.docker.com/compose/install/ 安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"
echo ""

# 生成随机 SECRET_KEY
generate_secret_key() {
    openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "please-change-this-secret-key-to-random-string"
}

# 检查 .env 文件
if [ ! -f backend/.env ]; then
    echo "📝 创建后端环境配置..."
    SECRET_KEY=$(generate_secret_key)

    cat > backend/.env << EOF
# 后端服务配置
PROJECT_NAME=OnboardKit
VERSION=1.0.0
API_V1_STR=/api/v1

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:3000","http://localhost"]

# 数据库配置
POSTGRES_SERVER=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=onboardkit_db_password_$(openssl rand -hex 8)
POSTGRES_DB=onboardkit

# Redis配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT配置
SECRET_KEY=${SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# Playwright配置
PLAYWRIGHT_TIMEOUT=30000
EOF
    echo "✅ 后端配置文件创建完成"
else
    echo "ℹ️  后端配置文件已存在"
fi

if [ ! -f frontend/.env ]; then
    echo "📝 创建前端环境配置..."
    cat > frontend/.env << EOF
# API 基础地址
VITE_API_BASE_URL=http://localhost:8000

# 应用配置
VITE_APP_TITLE=OnboardKit
VITE_APP_DESCRIPTION=交互式用户引导工具
EOF
    echo "✅ 前端配置文件创建完成"
else
    echo "ℹ️  前端配置文件已存在"
fi

echo ""
echo "🐳 启动 Docker 容器..."
docker-compose up -d postgres redis

echo ""
echo "⏳ 等待数据库启动..."
sleep 10

echo ""
echo "🗄️  运行数据库迁移..."
docker-compose run --rm backend alembic upgrade head || {
    echo "⚠️  数据库迁移失败，但这是正常的首次运行"
    echo "后续步骤会自动创建数据库表"
}

echo ""
echo "=========================="
echo "✅ 初始化完成！"
echo ""
echo "📖 接下来的步骤："
echo ""
echo "1️⃣  启动开发环境："
echo "   ./dev.sh"
echo ""
echo "2️⃣  或者使用 Docker 部署："
echo "   ./deploy.sh"
echo ""
echo "3️⃣  访问应用："
echo "   前端: http://localhost:5173 (开发) 或 http://localhost (生产)"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "=========================="
