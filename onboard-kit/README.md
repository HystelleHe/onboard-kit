# OnboardKit - 交互式用户引导工具

<div align="center">

![OnboardKit Logo](https://img.shields.io/badge/OnboardKit-v1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Vue](https://img.shields.io/badge/Vue-3.4-brightgreen)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal)

**B2B SaaS 产品 - 帮助产品团队创建交互式用户引导**

[在线演示](https://demo.onboardkit.com) · [使用文档](docs/DEVELOPMENT.md) · [问题反馈](https://github.com/HystelleHe/onboard-kit/issues)

</div>

---

## ✨ 产品特点

### 🎯 核心价值
将复杂的表单/页面拆解成分步引导流程，无需编程即可创建专业的用户引导体验。

### 🚀 主要功能

- **🎨 可视化编辑器** - 拖拽式步骤管理，所见即所得
- **🔍 智能页面分析** - 自动识别表单元素，AI 推荐引导步骤
- **👁️ 实时预览** - iframe 集成，即时查看引导效果
- **💻 代码生成** - 一键生成 HTML/JS/NPM 集成代码
- **📊 使用统计** - 记录用户行为，分析引导效果
- **🎁 14天免费试用** - 无需信用卡，立即体验

---

## 🏗️ 技术栈

### 前端
- **框架**: Vue 3 + TypeScript + Vite
- **UI**: Element Plus
- **引导库**: Driver.js
- **状态管理**: Pinia
- **路由**: Vue Router

### 后端
- **框架**: FastAPI + Python 3.11
- **ORM**: SQLAlchemy (异步)
- **页面分析**: Playwright + BeautifulSoup4
- **认证**: JWT

### 数据库 & 缓存
- **主数据库**: PostgreSQL 15
- **缓存**: Redis 7

### 部署
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx
- **反向代理**: 支持

---

## 🚀 快速开始

### 方式一：一键初始化（推荐）

```bash
# 克隆项目
git clone https://github.com/HystelleHe/onboard-kit.git
cd onboard-kit

# 运行初始化脚本
./init.sh

# 启动开发环境
./dev.sh
```

访问:
- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 方式二：Docker 一键部署

```bash
# 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，修改 SECRET_KEY 和数据库密码

# 启动所有服务
./deploy.sh
```

访问:
- 应用: http://localhost
- 后端API: http://localhost:8000

### 方式三：手动开发环境

#### 1. 启动数据库

```bash
docker-compose up -d postgres redis
```

#### 2. 后端服务

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 运行数据库迁移
alembic upgrade head

# 启动服务
uvicorn app.main:app --reload
```

#### 3. 前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

---

## 📁 项目结构

```
onboard-kit/
├── backend/                    # 后端服务
│   ├── alembic/               # 数据库迁移
│   │   └── versions/          # 迁移版本
│   ├── app/
│   │   ├── api/               # API 路由
│   │   │   ├── auth.py        # 认证
│   │   │   ├── users.py       # 用户管理
│   │   │   ├── guides.py      # 引导配置
│   │   │   └── pages.py       # 页面分析&代码生成
│   │   ├── core/              # 核心配置
│   │   │   ├── config.py      # 应用配置
│   │   │   └── database.py    # 数据库连接
│   │   ├── models/            # 数据模型
│   │   ├── schemas/           # Pydantic Schemas
│   │   ├── services/          # 业务逻辑
│   │   │   ├── page_analyzer.py    # 页面分析
│   │   │   └── code_generator.py   # 代码生成
│   │   └── main.py            # 应用入口
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                   # 前端应用
│   ├── src/
│   │   ├── api/               # API 客户端
│   │   ├── components/        # 通用组件
│   │   ├── stores/            # Pinia Stores
│   │   ├── types/             # TypeScript 类型
│   │   ├── views/             # 页面组件
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── GuideList.vue
│   │   │   ├── GuideEditor.vue
│   │   │   └── GuidePreview.vue
│   │   ├── router/            # 路由配置
│   │   ├── App.vue
│   │   └── main.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── nginx.conf
├── docs/                       # 文档
│   └── DEVELOPMENT.md         # 开发文档
├── docker-compose.yml         # Docker Compose 配置
├── init.sh                    # 初始化脚本
├── dev.sh                     # 开发环境脚本
├── deploy.sh                  # 部署脚本
└── README.md
```

---

## 🎮 使用指南

### 1. 注册账号

访问 http://localhost:5173/register，填写信息创建账号（自动获得14天试用）。

### 2. 创建引导

1. 点击"新建引导"
2. 输入引导名称和目标页面 URL
3. 点击"分析页面"，系统自动识别可引导元素
4. 添加引导步骤，配置提示内容
5. 保存并预览

### 3. 生成代码

1. 在预览页面点击"生成代码"
2. 选择集成方式（HTML/JS/NPM）
3. 复制代码到你的项目中
4. 按照说明完成集成

### 4. 查看效果

生成的引导可以直接在目标页面使用，支持：
- 元素高亮
- 步骤提示
- 进度显示
- 自定义样式

---

## 🔧 配置说明

### 环境变量

#### 后端 (`backend/.env`)

```bash
# 数据库（必须修改密码）
POSTGRES_PASSWORD=your_secure_password

# JWT密钥（必须修改）
SECRET_KEY=your-super-secret-key-min-32-characters

# CORS（生产环境需修改）
BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
```

#### 前端 (`frontend/.env.production`)

```bash
# API地址（生产环境需修改）
VITE_API_BASE_URL=https://api.yourdomain.com
```

---

## 📦 部署到生产环境

### 云服务器部署

**推荐配置**: 4核8GB，50GB SSD

```bash
# 1. 拉取代码
git clone https://github.com/HystelleHe/onboard-kit.git
cd onboard-kit

# 2. 配置环境变量
cp backend/.env.example backend/.env
# 编辑 backend/.env，修改敏感信息

# 3. 启动服务
./deploy.sh

# 4. 配置 Nginx（可选，用于自定义域名）
# 示例配置见 docs/nginx-example.conf
```

### 更新部署

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 🐛 常见问题

### Q: Playwright 安装失败？

```bash
# 使用国内镜像
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
```

### Q: 数据库连接失败？

检查:
1. PostgreSQL 是否启动: `docker-compose ps`
2. `.env` 文件中的数据库配置是否正确
3. 网络连接是否正常

### Q: 前端页面无法访问后端API？

检查:
1. 后端服务是否启动: http://localhost:8000/health
2. CORS 配置是否包含前端地址
3. Nginx 代理配置是否正确

---

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE)

---

## 💬 联系方式

- 项目主页: https://github.com/HystelleHe/onboard-kit
- 问题反馈: https://github.com/HystelleHe/onboard-kit/issues
- 邮箱: hystelle1223@163.com

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️ Star 支持一下！**

Made with ❤️ by OnboardKit Team

</div>
