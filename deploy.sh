#!/bin/bash

# OnboardKit 部署脚本

set -e

echo "🚀 开始部署 OnboardKit..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 请先安装 Docker Compose"
    exit 1
fi

# 创建.env文件（如果不存在）
if [ ! -f backend/.env ]; then
    echo "📝 创建环境配置文件..."
    cp backend/.env.example backend/.env
    echo "⚠️  请编辑 backend/.env 文件，修改数据库密码和SECRET_KEY"
    read -p "按回车继续..."
fi

# 停止旧容器
echo "🛑 停止旧容器..."
docker-compose down

# 构建镜像
echo "🔨 构建Docker镜像..."
docker-compose build

# 启动服务
echo "▶️  启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 初始化数据库
echo "🗄️  初始化数据库..."
docker-compose exec backend alembic upgrade head || echo "⚠️  数据库迁移失败，请手动执行"

echo ""
echo "✅ 部署完成！"
echo ""
echo "访问地址："
echo "  前端: http://localhost"
echo "  后端API: http://localhost:8000"
echo "  API文档: http://localhost:8000/docs"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止服务: docker-compose down"
