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
- **代码编辑器**: Monaco Editor（可选）

### 后端架构
- **框架**: FastAPI
- **ORM**: SQLAlchemy (异步)
- **数据库**: PostgreSQL + Redis
- **页面抓取**: Playwright
- **DOM解析**: BeautifulSoup4
- **认证**: JWT

### 数据库设计

#### 表结构

1. **users** - 用户表
   - id: 主键
   - email: 邮箱（唯一）
   - hashed_password: 加密密码
   - full_name: 姓名
   - company: 公司
   - is_trial: 是否试用
   - trial_expires_at: 试用到期时间
   - created_at: 创建时间

2. **guides** - 引导配置表
   - id: 主键
   - name: 引导名称
   - description: 描述
   - target_url: 目标URL
   - config: JSON 配置
   - is_published: 是否发布
   - owner_id: 所属用户
   - created_at: 创建时间

3. **steps** - 引导步骤表
   - id: 主键
   - guide_id: 所属引导
   - order: 顺序
   - title: 标题
   - description: 描述
   - element_selector: 元素选择器
   - position: 提示位置
   - config: JSON 配置

4. **page_analyses** - 页面分析表
   - id: 主键
   - url: 页面URL
   - html_content: HTML内容
   - analysis_result: 分析结果
   - suggested_elements: 建议元素

5. **usage_logs** - 使用日志表
   - id: 主键
   - user_id: 用户ID
   - action: 操作类型
   - details: 详细信息
   - created_at: 创建时间

### 目录结构

```
onboard-kit/
├── backend/                    # 后端服务
│   ├── alembic/               # 数据库迁移
│   │   ├── versions/          # 迁移版本
│   │   ├── env.py             # 迁移环境
│   │   └── script.py.mako     # 迁移模板
│   ├── app/
│   │   ├── api/               # API路由
│   │   │   ├── auth.py        # 认证相关
│   │   │   ├── users.py       # 用户管理
│   │   │   ├── guides.py      # 引导配置
│   │   │   └── pages.py       # 页面分析和代码生成
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # 数据模型
│   │   │   └── models.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   └── schemas.py
│   │   ├── services/          # 业务逻辑
│   │   │   ├── page_analyzer.py    # 页面分析
│   │   │   └── code_generator.py   # 代码生成
│   │   └── main.py            # 应用入口
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic.ini
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── api/              # API客户端
│   │   │   ├── client.ts     # Axios 实例
│   │   │   └── index.ts      # API 封装
│   │   ├── components/       # 公共组件
│   │   │   ├── Loading.vue
│   │   │   └── Empty.vue
│   │   ├── stores/           # Pinia stores
│   │   │   ├── auth.ts       # 认证状态
│   │   │   └── guide.ts      # 引导状态
│   │   ├── types/            # TypeScript类型
│   │   │   └── index.ts
│   │   ├── views/            # 页面组件
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── GuideList.vue
│   │   │   ├── GuideEditor.vue
│   │   │   └── GuidePreview.vue
│   │   ├── router/           # 路由配置
│   │   │   └── index.ts
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── init.sh                   # 初始化脚本
├── dev.sh                    # 开发环境脚本
├── deploy.sh                 # 部署脚本
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
   git clone https://github.com/yourusername/onboard-kit.git
   cd onboard-kit
   ```

### 快速启动

#### 使用初始化脚本（推荐）

```bash
# 一键初始化
./init.sh

# 启动开发环境
./dev.sh
```

#### 手动启动

**1. 启动数据库服务**

```bash
docker-compose up -d postgres redis
```

**2. 后端开发**

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器
playwright install chromium
playwright install-deps  # 安装系统依赖

# 配置环境变量
cp .env.example .env
# 编辑.env文件，修改数据库连接等配置

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 访问 http://localhost:8000
# API文档 http://localhost:8000/docs
```

**3. 前端开发**

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量（可选）
cp .env.example .env

# 运行开发服务器
npm run dev

# 访问 http://localhost:5173
```

### 数据库操作

#### 创建迁移

```bash
cd backend

# 自动生成迁移（基于模型变更）
alembic revision --autogenerate -m "描述"

# 手动创建迁移
alembic revision -m "描述"
```

#### 执行迁移

```bash
# 升级到最新版本
alembic upgrade head

# 升级到特定版本
alembic upgrade <revision>

# 回滚一个版本
alembic downgrade -1

# 查看迁移历史
alembic history

# 查看当前版本
alembic current
```

#### 重置数据库

```bash
# 停止服务
docker-compose down -v  # -v 会删除数据卷

# 重新启动
docker-compose up -d postgres redis

# 运行迁移
cd backend
alembic upgrade head
```

## API文档

启动后端服务后，访问:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要API端点

#### 认证
- `POST /api/v1/auth/register` - 注册
- `POST /api/v1/auth/login` - 登录
- `GET /api/v1/auth/me` - 获取当前用户

#### 引导配置
- `GET /api/v1/guides/` - 获取引导列表
- `POST /api/v1/guides/` - 创建引导
- `GET /api/v1/guides/{id}` - 获取引导详情
- `PUT /api/v1/guides/{id}` - 更新引导
- `DELETE /api/v1/guides/{id}` - 删除引导

#### 页面分析
- `POST /api/v1/pages/analyze` - 分析页面
- `POST /api/v1/pages/generate-code` - 生成代码
- `GET /api/v1/pages/preview/{id}` - 预览引导

## 部署指南

### Docker部署（推荐）

```bash
# 1. 配置环境变量
cp backend/.env.example backend/.env
# 编辑backend/.env，修改敏感信息:
# - POSTGRES_PASSWORD: 数据库密码
# - SECRET_KEY: JWT密钥（至少32字符）
# - BACKEND_CORS_ORIGINS: 允许的前端域名

# 2. 一键部署
./deploy.sh

# 3. 查看日志
docker-compose logs -f

# 4. 访问应用
# 前端: http://localhost
# 后端: http://localhost:8000
```

### 手动部署

**后端**
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**前端**
```bash
cd frontend
npm install
npm run build
# 部署dist目录到Nginx或其他Web服务器
```

### Nginx 配置示例

```nginx
# /etc/nginx/sites-available/onboardkit
server {
    listen 80;
    server_name yourdomain.com;

    # 前端
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket支持（如果需要）
    location /ws {
        proxy_pass http://127.0.0.1:8000/ws;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### SSL配置（推荐）

```bash
# 使用 Let's Encrypt
sudo certbot --nginx -d yourdomain.com
```

## 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=app tests/
```

### 前端测试

```bash
cd frontend

# 单元测试
npm run test:unit

# E2E测试
npm run test:e2e

# 生成覆盖率
npm run test:coverage
```

## 常见问题

### 1. Playwright安装失败

**问题**: 下载Chromium超时

**解决方案**:
```bash
# 使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### 2. 数据库连接失败

**问题**: `connection refused`

**检查清单**:
- PostgreSQL是否启动: `docker-compose ps`
- `.env`文件中的数据库配置是否正确
- 数据库是否创建: `docker-compose exec postgres psql -U postgres -l`

### 3. CORS错误

**问题**: 前端无法访问后端API

**解决方案**:
- 检查 `backend/.env` 中的 `BACKEND_CORS_ORIGINS`
- 确保前端地址在允许列表中
- 开发环境: `["http://localhost:5173"]`
- 生产环境: `["https://yourdomain.com"]`

### 4. Docker 容器无法启动

**问题**: 端口已被占用

**解决方案**:
```bash
# 查看端口占用
lsof -i :8000  # 后端
lsof -i :5173  # 前端开发
lsof -i :80    # Nginx

# 停止占用进程或修改docker-compose.yml中的端口映射
```

### 5. Alembic迁移失败

**问题**: 迁移时出现错误

**解决方案**:
```bash
# 查看当前版本
alembic current

# 查看迁移历史
alembic history

# 强制设置版本（谨慎使用）
alembic stamp head

# 重新运行迁移
alembic upgrade head
```

## 性能优化

### 前端优化

1. **代码分割**
   - 使用动态导入
   - 路由懒加载已配置

2. **资源优化**
   - 图片使用 WebP 格式
   - 启用 Gzip 压缩（Nginx已配置）
   - 静态资源CDN加速

3. **构建优化**
   ```bash
   # 分析构建大小
   npm run build -- --report
   ```

### 后端优化

1. **数据库查询**
   - 使用索引（已在模型中配置）
   - 使用 `selectinload` 预加载关联数据
   - 避免 N+1 查询

2. **缓存策略**
   - 页面分析结果缓存到Redis
   - 使用 `@lru_cache` 缓存配置

3. **并发处理**
   - 使用异步数据库操作
   - 页面分析使用后台任务

## 安全建议

### 必做项

1. **修改默认密钥**
   ```bash
   # 生成随机SECRET_KEY
   openssl rand -hex 32
   ```

2. **使用强密码**
   - 数据库密码: 至少16字符
   - Redis密码: 启用并设置强密码

3. **启用HTTPS**
   ```bash
   # 使用Let's Encrypt免费证书
   certbot --nginx -d yourdomain.com
   ```

4. **限制API请求频率**
   - 安装 `slowapi`
   - 配置速率限制

5. **定期更新依赖**
   ```bash
   # Python
   pip list --outdated
   pip install --upgrade <package>

   # Node.js
   npm outdated
   npm update
   ```

### 推荐项

- 启用数据库备份
- 配置防火墙规则
- 使用环境变量管理敏感信息
- 启用日志审计
- 定期安全扫描

## 贡献指南

### 开发流程

1. **Fork 项目**
2. **创建特性分支**
   ```bash
   git checkout -b feature/AmazingFeature
   ```

3. **提交更改**
   ```bash
   git commit -m 'Add some AmazingFeature'
   ```

4. **推送到分支**
   ```bash
   git push origin feature/AmazingFeature
   ```

5. **创建 Pull Request**

### 代码规范

#### Python
- 遵循 PEP 8
- 使用 `black` 格式化
- 使用 `pylint` 检查

#### TypeScript/Vue
- 遵循 Vue 3 风格指南
- 使用 ESLint
- 使用 Prettier 格式化

### 提交信息规范

使用语义化提交:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建/工具

示例:
```
feat: 添加页面分析缓存功能

- 使用Redis缓存分析结果
- 设置1小时过期时间
- 添加缓存键管理
```

## 许可证

MIT License

## 联系方式

- 项目地址: https://github.com/yourusername/onboard-kit
- 问题反馈: https://github.com/yourusername/onboard-kit/issues
