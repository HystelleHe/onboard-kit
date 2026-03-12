# Changelog

所有重要的项目变更都将记录在此文件中。

本项目遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

## [1.0.0] - 2026-03-12

### 新增

#### 核心功能
- 用户认证系统（JWT）
- 14天免费试用机制
- 引导配置编辑器
- 实时预览功能
- 页面智能分析（Playwright + BeautifulSoup4）
- 代码生成器（HTML/JS/NPM三种格式）
- 使用统计记录

#### 前端
- Vue 3 + TypeScript 架构
- Element Plus UI 组件
- Driver.js 引导集成
- Pinia 状态管理
- 响应式设计
- 登录/注册页面
- 仪表板
- 引导列表页面
- 引导编辑器
- 引导预览页面

#### 后端
- FastAPI 异步框架
- SQLAlchemy 异步 ORM
- PostgreSQL 数据库
- Redis 缓存支持
- Alembic 数据库迁移
- RESTful API
- Swagger/ReDoc API 文档

#### 部署
- Docker 容器化
- Docker Compose 编排
- Nginx 反向代理
- 一键部署脚本
- 开发环境脚本
- 初始化脚本

#### 文档
- 完整的 README
- 开发文档 (DEVELOPMENT.md)
- 部署清单 (DEPLOYMENT.md)
- 贡献指南 (CONTRIBUTING.md)
- Nginx 配置示例
- CI/CD 工作流（GitHub Actions）

### 技术栈
- **前端**: Vue 3.4, TypeScript, Vite, Element Plus 2.5
- **后端**: Python 3.11, FastAPI 0.109, SQLAlchemy 2.0
- **数据库**: PostgreSQL 15, Redis 7
- **工具**: Playwright 1.41, Driver.js 1.3, Docker

### 已知问题
- 页面分析对于需要登录的页面支持有限
- iframe 跨域限制可能影响预览功能
- 暂不支持移动端优化

---

## 版本说明

### [1.0.0] - 初始版本
第一个正式发布版本，包含所有核心功能，可用于生产环境。

**支持的浏览器:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**服务器要求:**
- CPU: 4核+
- 内存: 8GB+
- 硬盘: 50GB SSD+
- OS: Ubuntu 20.04+ / CentOS 8+

---

[Unreleased]: https://github.com/HystelleHe/onboard-kit/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/HystelleHe/onboard-kit/releases/tag/v1.0.0
