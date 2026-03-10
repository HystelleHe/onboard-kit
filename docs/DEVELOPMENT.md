# OnboardKit 开发文档

## 项目概述

OnboardKit 是一个 B2B SaaS 产品，帮助其他产品将复杂表单/页面拆解成分步引导流程。

### 核心功能

1. **配置编辑器** - 步骤管理、字段映射、文案编辑、样式配置
2. **实时预览器** - iframe加载外部页面、引导效果渲染、元素选择
3. **页面分析服务** - URL抓取(Playwright)、DOM解析、智能建议
4. **代码生成器** - 输出可集成的JS/HTML代码
5. **用户管理** - 试用记录、联系信息收集、使用统计

## 技术架构

### 前端架构
- **框架**: Vue 3 + TypeScript
- **构建工具**: Vite
- **UI组件**: Element Plus
- **路由**: Vue Router
- **状态管理**: Pinia
- **引导库**: Driver.js
- **代码编辑器**: Monaco Editor

### 后端架构
- **框架**: FastAPI
- **ORM**: SQLAlchemy
- **数据库**: PostgreSQL + Redis
- **页面抓取**: Playwright
- **DOM解析**: BeautifulSoup4
- **认证**: JWT

### 目录结构

```
onboard-kit/
├── backend/                 # 后端服务
│   ├── app/
│   │   ├── api/            # API路由
│   │   │   ├── auth.py     # 认证相关
│   │   │   ├── users.py    # 用户管理
│   │   │   ├── guides.py   # 引导配置
│   │   │   └── pages.py    # 页面分析和代码生成
│   │   ├── core/           # 核心配置
│   │   │   ├── config.py   # 应用配置
│   │   │   └── database.py # 数据库连接
│   │   ├── models/         # 数据模型
│   │   │   └── models.py
│   │   ├── schemas/        # Pydantic schemas
│   │   │   └── schemas.py
│   │   ├── services/       # 业务逻辑
│   │   │   ├── page_analyzer.py    # 页面分析
│   │   │   └── code_generator.py   # 代码生成
│   │   └── main.py         # 应用入口
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── api/           # API客户端
│   │   ├── components/    # 公共组件
│   │   ├── stores/        # Pinia stores
│   │   ├── types/         # TypeScript类型
│   │   ├── views/         # 页面组件
│   │   ├── router/        # 路由配置
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docker-compose.yml
├── deploy.sh
├── dev.sh
└── README.md
```

## 开发指南

### 环境准备

1. **安装依赖**
   - Node.js 20+
   - Python 3.11+
   - Docker & Docker Compose
   - PostgreSQL 15+ (或使用Docker)
   - Redis 7+ (或使用Docker)

2. **克隆项目**
   ```bash
   cd onboard-kit
   ```

### 本地开发

#### 方式一：使用Docker（推荐新手）

```bash
# 启动数据库服务
./dev.sh

# 或手动启动
docker-compose up -d postgres redis
```

#### 方式二：完全本地环境

**后端开发**

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium

# 配置环境变量
cp .env.example .env
# 编辑.env文件，修改数据库连接等配置

# 运行开发服务器
uvicorn app.main:app --reload

# 访问 http://localhost:8000
# API文档 http://localhost:8000/docs
```

**前端开发**

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 访问 http://localhost:5173
```

### 数据库迁移

```bash
cd backend

# 创建迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## API文档

启动后端服务后，访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要API端点

**认证**
- `POST /api/v1/auth/register` - 注册
- `POST /api/v1/auth/login` - 登录
- `GET /api/v1/auth/me` - 获取当前用户

**引导配置**
- `GET /api/v1/guides/` - 获取引导列表
- `POST /api/v1/guides/` - 创建引导
- `GET /api/v1/guides/{id}` - 获取引导详情
- `PUT /api/v1/guides/{id}` - 更新引导
- `DELETE /api/v1/guides/{id}` - 删除引导

**页面分析**
- `POST /api/v1/pages/analyze` - 分析页面
- `POST /api/v1/pages/generate-code` - 生成代码
- `GET /api/v1/pages/preview/{id}` - 预览引导

## 部署指南

### Docker部署（推荐）

```bash
# 1. 配置环境变量
cp backend/.env.example backend/.env
# 编辑backend/.env，修改敏感信息

# 2. 一键部署
./deploy.sh

# 3. 访问应用
# 前端: http://localhost
# 后端: http://localhost:8000
```

### 手动部署

**后端**
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**前端**
```bash
cd frontend
npm install
npm run build
# 部署dist目录到Nginx或其他Web服务器
```

## 测试

### 后端测试
```bash
cd backend
pytest
```

### 前端测试
```bash
cd frontend
npm run test
```

## 常见问题

### 1. Playwright安装失败
```bash
# 使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### 2. 数据库连接失败
- 检查PostgreSQL是否启动
- 检查.env文件中的数据库配置
- 确保数据库已创建

### 3. CORS错误
- 检查backend/.env中的BACKEND_CORS_ORIGINS配置
- 确保前端地址在允许列表中

## 性能优化

1. **前端优化**
   - 使用代码分割
   - 图片懒加载
   - CDN加速

2. **后端优化**
   - Redis缓存
   - 数据库索引
   - 异步任务队列

## 安全建议

1. 修改默认的SECRET_KEY
2. 使用强密码
3. 启用HTTPS
4. 定期更新依赖
5. 限制API请求频率

## 贡献指南

1. Fork项目
2. 创建特性分支
3. 提交变更
4. 推送到分支
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/yourusername/onboard-kit
- 问题反馈: https://github.com/yourusername/onboard-kit/issues
