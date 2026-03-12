# OnboardKit 快速启动指南

## 🚀 5分钟快速启动

### 前置要求

确保已安装：
- ✅ Docker Desktop (macOS/Windows) 或 Docker + Docker Compose (Linux)
- ✅ Git

### 步骤 1: 克隆项目

```bash
git clone https://github.com/yourusername/onboard-kit.git
cd onboard-kit
```

### 步骤 2: 一键初始化

```bash
chmod +x init.sh dev.sh deploy.sh
./init.sh
```

这个脚本会自动：
- ✅ 生成随机的安全密钥
- ✅ 创建环境配置文件
- ✅ 启动数据库服务
- ✅ 运行数据库迁移

### 步骤 3: 选择启动方式

#### 方式 A: 开发环境（推荐用于开发）

```bash
./dev.sh
```

然后在两个终端分别运行：

**终端 1 - 后端:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --reload
```

**终端 2 - 前端:**
```bash
cd frontend
npm install
npm run dev
```

访问:
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

#### 方式 B: Docker 生产环境（一键部署）

```bash
./deploy.sh
```

访问:
- 应用: http://localhost
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 步骤 4: 开始使用

1. **注册账号**
   - 访问 http://localhost:5173/register (开发) 或 http://localhost/register (生产)
   - 填写邮箱和密码
   - 自动获得14天试用

2. **创建第一个引导**
   - 登录后点击"新建引导"
   - 输入引导名称：例如"用户注册引导"
   - 输入目标URL：例如"https://example.com/signup"
   - 点击"分析页面"，等待智能分析完成
   - 添加引导步骤，选择页面元素
   - 保存并预览

3. **生成代码**
   - 在预览页面点击"生成代码"
   - 选择格式（HTML/JS/NPM）
   - 复制代码到你的项目

## 🎯 快速测试

### 测试后端API

```bash
# 健康检查
curl http://localhost:8000/health

# 查看API文档
open http://localhost:8000/docs  # macOS
# 或在浏览器访问 http://localhost:8000/docs
```

### 测试前端

1. 打开浏览器访问 http://localhost:5173
2. 应该看到登录页面
3. 注册一个测试账号
4. 登录后应该看到仪表板

## 🛠️ 常用命令

### 查看服务状态

```bash
docker-compose ps
```

### 查看日志

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

### 清理并重新开始

```bash
# 停止并删除所有容器和数据
docker-compose down -v

# 重新初始化
./init.sh
./deploy.sh
```

## 📊 验证安装

运行以下命令验证所有服务正常：

```bash
# 检查 PostgreSQL
docker-compose exec postgres psql -U postgres -c "\l"

# 检查 Redis
docker-compose exec redis redis-cli ping

# 检查后端
curl http://localhost:8000/health

# 检查数据库表
docker-compose exec postgres psql -U postgres -d onboardkit -c "\dt"
```

应该看到：
- PostgreSQL: 列出数据库
- Redis: 返回 PONG
- 后端: 返回 `{"status":"healthy"}`
- 数据库表: users, guides, steps, page_analyses, usage_logs

## 🐛 遇到问题？

### 端口被占用

```bash
# 查看端口占用
lsof -i :8000  # 后端
lsof -i :5173  # 前端开发
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# 修改端口（编辑 docker-compose.yml）
# 或停止占用端口的进程
```

### 数据库连接失败

```bash
# 检查PostgreSQL是否运行
docker-compose ps postgres

# 重启数据库
docker-compose restart postgres

# 查看数据库日志
docker-compose logs postgres
```

### Playwright 安装失败

```bash
# 使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
cd backend
source venv/bin/activate
playwright install chromium
```

### 前端页面空白

```bash
# 检查控制台错误
# 清除浏览器缓存
# 确保后端API正常运行
curl http://localhost:8000/health

# 检查CORS配置
# backend/.env 中的 BACKEND_CORS_ORIGINS 应包含前端地址
```

## 📚 下一步

- 📖 阅读[完整文档](docs/DEVELOPMENT.md)
- 🎨 自定义[主题样式](frontend/src/styles/)
- 🔧 配置[环境变量](backend/.env)
- 🚀 [部署到生产环境](DEPLOYMENT.md)

## 💡 提示

1. **开发环境** vs **生产环境**
   - 开发: 热重载，调试模式，详细日志
   - 生产: 优化构建，压缩资源，性能最佳

2. **数据持久化**
   - Docker volumes 用于存储数据
   - 删除 volumes (`docker-compose down -v`) 会清空所有数据

3. **环境变量**
   - 开发环境: `.env` 和 `.env.local`
   - 生产环境: `.env.production`
   - 永远不要提交包含敏感信息的 `.env` 文件到 Git

## 🆘 获取帮助

- 📖 [开发文档](docs/DEVELOPMENT.md)
- 🐛 [问题反馈](https://github.com/yourusername/onboard-kit/issues)
- 💬 [讨论区](https://github.com/yourusername/onboard-kit/discussions)
- 📧 Email: support@yourdomain.com

---

**祝你使用愉快！** 🎉

如果觉得有帮助，请给项目一个 ⭐️ Star！
