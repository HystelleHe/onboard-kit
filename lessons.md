# OnboardKit 开发经验与优化记录

## 2026-03-16 引导功能优化经验

### 问题描述
用户反馈引导功能有两个问题：
1. 引导弹窗位置不正确
2. 希望优化交互：高亮元素+遮罩，点击自动下一步

### 方案 B（已实施）- 轻量优化
**修改内容：**
- 后端：popover 配置添加 `align: "start"`，side 默认值改为 "bottom"
- 前端：driver 配置添加 `animate: true` 和 `overlayOpacity: 0.75`

**效果：**
- 弹窗位置修正
- 添加遮罩效果（75%透明度）
- 保持原有交互逻辑

### 方案 A（待实施）- 完整优化
**目标效果：**
- 高亮选中元素，其他区域置灰遮罩
- 点击高亮区域自动进入下一步
- 无需点击弹窗内 "Next"/"Done" 按钮

**实现思路：**
```typescript
const driverObj = driver({
  showProgress: true,
  animate: true,
  overlayOpacity: 0.75,
  steps: processedSteps,
  
  // 点击遮罩区域下一步
  onOverlayClick: () => {
    driverObj.moveNext()
  },
  
  // 步骤显示时给高亮元素添加点击事件
  onHighlighted: (element: Element) => {
    element.addEventListener("click", () => {
      driverObj.moveNext()
    }, { once: true })
  }
})
```

**注意事项：**
1. 需要处理 steps 配置，过滤掉无效元素
2. 考虑添加键盘事件支持（ESC退出，方向键切换）
3. 最后一步需要特殊处理（显示完成提示）

### 技术细节

#### Driver.js 配置参数
| 参数 | 说明 | 当前值 |
|------|------|--------|
| showProgress | 显示进度条 | true |
| animate | 启用动画 | true |
| overlayOpacity | 遮罩透明度 | 0.75 |
| side | 弹窗位置 | bottom/top/left/right |
| align | 对齐方式 | start/center/end |

#### 元素选择器说明
- `#id` - 通过 ID 选择元素
- `.class` - 通过 class 选择元素
- `tag[attr="value"]` - 通过属性选择元素

#### 常见问题
1. **引导卡死**：检查 element_selector 是否为空或无效
2. **位置偏移**：确保目标页面可访问，元素在可视区域内
3. **遮罩不显示**：检查 overlayOpacity 是否设置

### 后续优化建议
1. 添加引导步骤的实时预览（在编辑器中直接看到效果）
2. 支持拖拽调整弹窗位置
3. 添加更多引导模板（新手引导、功能介绍等）
4. 支持条件分支（根据用户选择显示不同步骤）

## 2026-03-16 数据库连接问题

### 问题现象
登录/注册报错：`InvalidPasswordError: password authentication failed for user "postgres"`

### 根本原因
PostgreSQL 容器数据卷损坏或密码状态不一致

### 修复步骤
```bash
# 1. 停止并删除 postgres 容器
docker compose stop postgres
docker compose rm -f postgres

# 2. 删除数据卷（会丢失数据！）
docker volume rm onboard-kit_postgres_data

# 3. 重新创建容器
docker compose up -d postgres

# 4. 初始化数据库表
docker exec onboardkit-backend python3 -c "
import asyncio
from app.core.database import engine
from app.models.models import Base
async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print(Database initialized)
asyncio.run(init())
"
```

### 预防措施
1. **定期备份**：运行 `./backup-db.sh` 备份数据库
2. **监控告警**：检查数据库连接状态
3. **使用外部数据库**：生产环境使用托管 PostgreSQL（如阿里云 RDS）

### 快速诊断命令
```bash
# 检查数据库日志
docker logs onboardkit-postgres

# 测试连接
docker exec onboardkit-postgres pg_isready -U postgres

# 查看后端数据库错误
docker logs onboardkit-backend | grep -i error
```

## 2024-03-17 引导编辑器交互流程优化

### 当前版本（V1）
- 左侧表单配置步骤
- 右侧演示区域使用固定 Demo 元素
- 底部生成代码

### 下一版本（V2）规划
基于截图的交互式引导配置

#### 核心流程
1. **分析页面**
   - 输入目标 URL
   - 后端 Playwright 截图 + 分析可交互元素
   - 返回推荐区域列表（坐标 + 推荐标题）

2. **推荐区域快速添加**
   - 截图上高亮显示推荐区域（蓝色虚线框 + 序号）
   - 每个区域显示 [+ 添加步骤] 按钮
   - 点击自动添加步骤到左侧列表
   - 已添加区域标记为绿色实线框 + ✓

3. **手动选择模式**
   - 顶部 [✋ 手动选择] 按钮
   - 进入框选模式：鼠标变十字准星
   - 用户拖拽框选截图区域
   - 弹出对话框填写步骤信息
   - 手动框选区域显示橙色实线框

#### 页面布局


#### 技术实现
- **截图**：后端 Playwright 截图保存
- **元素识别**：Playwright 分析可交互元素（输入框、按钮等）
- **坐标映射**：截图坐标与实际页面坐标比例换算
- **选择器生成**：优先 id > data-testid > class > 属性组合

#### 工作量评估
| 模块 | 时间 |
|------|------|
| 后端截图 API | 1h |
| 元素分析推荐 | 1.5h |
| 前端截图显示 + 框选 | 2h |
| 推荐区域交互 | 1.5h |
| 手动框选模式 | 1.5h |
| 步骤列表联动 | 1h |
| **总计** | **~8.5h** |

