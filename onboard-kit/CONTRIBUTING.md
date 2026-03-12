# OnboardKit 贡献指南

感谢你考虑为 OnboardKit 做出贡献！

## 行为准则

我们致力于为所有人提供一个友好、安全和受欢迎的环境。请尊重所有参与者。

## 如何贡献

### 报告 Bug

1. 在提交新 issue 之前，请先搜索现有 issues 确保问题尚未被报告
2. 使用清晰的标题和描述
3. 包含重现步骤、预期行为和实际行为
4. 提供环境信息（操作系统、浏览器、版本等）
5. 如果可能，提供截图或日志

### 功能请求

1. 清楚地描述新功能的用途和价值
2. 说明这个功能如何使其他用户受益
3. 提供具体的使用场景示例

### 提交代码

#### 准备工作

1. Fork 仓库
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 确保本地代码可以正常运行

#### 代码规范

**Python (后端)**
```bash
# 格式化代码
black app/

# 检查代码质量
pylint app/

# 排序 imports
isort app/
```

**TypeScript/Vue (前端)**
```bash
# ESLint 检查
npm run lint

# 格式化
npm run format
```

#### 提交信息规范

使用语义化提交信息：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- `feat`: 新功能
- `fix`: 修复 bug
- `docs`: 文档更新
- `style`: 代码格式（不影响代码运行的变动）
- `refactor`: 重构（既不是新增功能，也不是修复bug）
- `perf`: 性能优化
- `test`: 增加测试
- `chore`: 构建过程或辅助工具的变动

**示例:**
```
feat(auth): 添加 OAuth2 登录支持

- 实现 Google OAuth2 集成
- 添加 GitHub OAuth2 集成
- 更新用户模型以支持多种登录方式

Closes #123
```

#### 测试

- 为新功能添加测试
- 确保所有测试通过
- 保持或提高代码覆盖率

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm run test
```

#### Pull Request

1. 更新 README.md（如果需要）
2. 更新相关文档
3. 确保 CI 通过
4. 请求代码审查

**PR 标题格式:**
```
[类型] 简短描述

示例:
[Feature] 添加页面分析缓存
[Fix] 修复登录重定向问题
[Docs] 更新部署文档
```

**PR 描述应包含:**
- 变更的简要说明
- 相关 issue 链接
- 测试说明
- 截图（如果是UI变更）

## 开发流程

### 分支策略

- `main`: 生产环境代码
- `develop`: 开发环境代码
- `feature/*`: 功能开发分支
- `fix/*`: Bug 修复分支
- `hotfix/*`: 紧急修复分支

### 开发步骤

1. **创建分支**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **开发和测试**
   ```bash
   # 提交代码
   git add .
   git commit -m "feat: your feature description"

   # 保持分支最新
   git fetch origin
   git rebase origin/develop
   ```

3. **推送分支**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **创建 Pull Request**
   - 在 GitHub 上创建 PR
   - 选择 `develop` 作为目标分支
   - 填写 PR 描述
   - 请求审查

5. **代码审查**
   - 响应审查意见
   - 进行必要的修改
   - 更新 PR

6. **合并**
   - 在 PR 被批准后
   - 确保 CI 通过
   - 由维护者合并

## 代码审查指南

### 作为审查者

- 保持尊重和建设性
- 关注代码质量、可读性和可维护性
- 检查是否有测试覆盖
- 验证功能是否按预期工作

### 作为被审查者

- 接受建设性批评
- 解释你的设计决策
- 及时响应反馈
- 感谢审查者的时间

## 发布流程

1. 更新版本号（遵循 [语义化版本](https://semver.org/lang/zh-CN/)）
2. 更新 CHANGELOG.md
3. 创建发布 PR 到 main
4. 合并后创建 Git tag
5. 触发自动部署

## 联系方式

- GitHub Issues: https://github.com/HystelleHe/onboard-kit/issues
- 邮箱: hystelle1223@163.com

## 许可证

通过贡献代码，你同意你的贡献将在 MIT 许可证下发布。
