# OnboardKit - 交互式用户引导工具

B2B SaaS产品，帮助其他产品将复杂表单/页面拆解成分步引导流程。

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite
- Element Plus
- Driver.js (引导库)
- Monaco Editor (代码编辑器)

### 后端
- Python FastAPI
- SQLAlchemy
- Playwright (页面抓取)
- BeautifulSoup4 (DOM解析)

### 数据库
- PostgreSQL
- Redis

### 部署
- Docker
- Nginx

## 项目结构

```
onboard-kit/
├── frontend/          # Vue 3 前端项目
├── backend/           # FastAPI 后端项目
├── docker/            # Docker 配置文件
├── docs/              # 项目文档
└── README.md
```

## 快速开始

### 本地开发

1. 启动后端服务:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. 启动前端服务:
```bash
cd frontend
npm install
npm run dev
```

### Docker 部署

```bash
docker-compose up -d
```

## 核心功能

1. 配置编辑器 - 步骤管理、字段映射、文案编辑、样式配置
2. 实时预览器 - iframe加载外部页面、引导效果渲染、元素选择
3. 页面分析服务 - URL抓取(Playwright)、DOM解析、智能建议
4. 代码生成器 - 输出可集成的JS/HTML代码
5. 用户管理 - 试用记录、联系信息收集、使用统计

