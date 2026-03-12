from typing import Dict, Any
from app.models.models import Guide as GuideModel


class CodeGeneratorService:
    """代码生成服务，根据引导配置生成可集成的代码"""

    def generate(self, guide: GuideModel, format: str = "html") -> Dict[str, Any]:
        """
        生成代码

        Args:
            guide: 引导配置对象
            format: 输出格式 (html, js, npm)

        Returns:
            包含代码和说明的字典
        """
        if format == "html":
            return self._generate_html(guide)
        elif format == "js":
            return self._generate_js(guide)
        elif format == "npm":
            return self._generate_npm(guide)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_html(self, guide: GuideModel) -> Dict[str, Any]:
        """生成HTML格式的代码（包含完整的页面和引导脚本）"""
        steps = sorted(guide.steps, key=lambda s: s.order)
        steps_js = self._format_steps_for_driver(steps)

        code = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{guide.name}</title>

    <!-- Driver.js CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/driver.js@1.3.1/dist/driver.css"/>
</head>
<body>
    <!-- 在这里嵌入您的页面内容 -->
    <iframe src="{guide.target_url}" width="100%" height="100%" frameborder="0"></iframe>

    <!-- Driver.js Script -->
    <script src="https://cdn.jsdelivr.net/npm/driver.js@1.3.1/dist/driver.js.iife.js"></script>

    <script>
        // 初始化引导
        const driver = window.driver.js.driver({{
            showProgress: true,
            steps: {steps_js}
        }});

        // 启动引导
        driver.drive();
    </script>
</body>
</html>"""

        instructions = """
使用说明：
1. 将此HTML代码保存为文件（如 guide.html）
2. 在浏览器中打开该文件
3. 引导将自动启动

注意：
- 请确保目标页面允许在iframe中加载
- 如果需要自定义样式，可以修改Driver.js的CSS
"""

        return {
            "code": code,
            "instructions": instructions
        }

    def _generate_js(self, guide: GuideModel) -> Dict[str, Any]:
        """生成纯JavaScript代码（可直接嵌入现有页面）"""
        steps = sorted(guide.steps, key=lambda s: s.order)
        steps_js = self._format_steps_for_driver(steps)

        code = f"""// OnboardKit 引导代码
// 确保已在页面中引入 Driver.js

// CDN引入方式:
// <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/driver.js@1.3.1/dist/driver.css"/>
// <script src="https://cdn.jsdelivr.net/npm/driver.js@1.3.1/dist/driver.js.iife.js"></script>

(function() {{
    // 初始化引导
    const driver = window.driver.js.driver({{
        showProgress: true,
        steps: {steps_js}
    }});

    // 启动引导
    driver.drive();
}})();
"""

        instructions = """
使用说明：
1. 在您的页面中引入 Driver.js 的CSS和JS文件（见代码注释）
2. 将此JS代码添加到页面底部或在适当的时机执行
3. 引导将在代码执行时启动

自定义：
- 可以将 driver.drive() 绑定到按钮点击等事件
- 可以调整配置选项，详见 Driver.js 文档
"""

        return {
            "code": code,
            "instructions": instructions
        }

    def _generate_npm(self, guide: GuideModel) -> Dict[str, Any]:
        """生成NPM包方式的代码（适用于现代前端项目）"""
        steps = sorted(guide.steps, key=lambda s: s.order)
        steps_config = []

        for step in steps:
            steps_config.append({
                "element": step.element_selector,
                "popover": {
                    "title": step.title,
                    "description": step.description or "",
                    "side": step.position
                }
            })

        import json
        steps_json = json.dumps(steps_config, indent=2, ensure_ascii=False)

        code = f"""// 1. 安装依赖
// npm install driver.js

// 2. 在您的组件中使用
import {{ driver }} from "driver.js";
import "driver.js/dist/driver.css";

export function initOnboardGuide() {{
    const driverObj = driver({{
        showProgress: true,
        steps: {steps_json}
    }});

    return driverObj;
}}

// 3. 使用示例
// const guide = initOnboardGuide();
// guide.drive();  // 启动引导
"""

        instructions = """
使用说明：
1. 在项目中安装 driver.js: npm install driver.js
2. 将此代码添加到您的项目中
3. 在需要的地方导入并调用 initOnboardGuide()

React 示例:
```jsx
import { useEffect } from 'react';
import { initOnboardGuide } from './guide';

function App() {
  useEffect(() => {
    const guide = initOnboardGuide();
    guide.drive();
  }, []);

  return <div>Your App</div>;
}
```

Vue 3 示例:
```vue
<script setup>
import { onMounted } from 'vue';
import { initOnboardGuide } from './guide';

onMounted(() => {
  const guide = initOnboardGuide();
  guide.drive();
});
</script>
```
"""

        return {
            "code": code,
            "instructions": instructions
        }

    def _format_steps_for_driver(self, steps) -> str:
        """将步骤格式化为Driver.js配置"""
        steps_list = []
        for step in steps:
            steps_list.append(f"""{{
                element: '{step.element_selector}',
                popover: {{
                    title: '{step.title}',
                    description: '{step.description or ""}',
                    side: '{step.position}'
                }}
            }}""")

        return "[\n        " + ",\n        ".join(steps_list) + "\n    ]"
