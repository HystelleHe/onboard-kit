from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from app.core.config import settings


class PageAnalyzerService:
    """页面分析服务，使用Playwright抓取页面并分析DOM结构"""

    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        分析指定URL的页面

        Args:
            url: 目标页面URL

        Returns:
            包含页面分析结果的字典
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # 访问页面
                await page.goto(url, timeout=settings.PLAYWRIGHT_TIMEOUT)
                await page.wait_for_load_state("networkidle")

                # 获取HTML内容
                html_content = await page.content()

                # 分析页面结构
                structure = await self._analyze_structure(page)

                # 提取建议的引导元素
                suggested_elements = await self._extract_suggested_elements(page, html_content)

                return {
                    "html_content": html_content,
                    "structure": structure,
                    "suggested_elements": suggested_elements
                }

            finally:
                await browser.close()

    async def _analyze_structure(self, page) -> Dict[str, Any]:
        """分析页面结构"""
        return await page.evaluate("""
            () => {
                const structure = {
                    title: document.title,
                    forms: [],
                    buttons: [],
                    inputs: [],
                    sections: []
                };

                // 分析表单
                document.querySelectorAll('form').forEach((form, index) => {
                    structure.forms.push({
                        index: index,
                        id: form.id || null,
                        action: form.action || null,
                        method: form.method || 'get',
                        fields: Array.from(form.elements).map(el => ({
                            name: el.name || null,
                            type: el.type || null,
                            id: el.id || null,
                            required: el.required || false
                        }))
                    });
                });

                // 分析按钮
                document.querySelectorAll('button, input[type="submit"], input[type="button"]').forEach((btn, index) => {
                    structure.buttons.push({
                        index: index,
                        text: btn.textContent?.trim() || btn.value || '',
                        id: btn.id || null,
                        type: btn.type || null,
                        selector: btn.id ? `#${btn.id}` : null
                    });
                });

                // 分析输入框
                document.querySelectorAll('input, textarea, select').forEach((input, index) => {
                    structure.inputs.push({
                        index: index,
                        type: input.type || input.tagName.toLowerCase(),
                        id: input.id || null,
                        name: input.name || null,
                        placeholder: input.placeholder || null,
                        required: input.required || false,
                        selector: input.id ? `#${input.id}` : (input.name ? `[name="${input.name}"]` : null)
                    });
                });

                return structure;
            }
        """)

    async def _extract_suggested_elements(self, page, html_content: str) -> List[Dict[str, Any]]:
        """提取建议的引导元素"""
        soup = BeautifulSoup(html_content, 'lxml')
        suggestions = []

        # 建议1: 所有带有placeholder的输入框
        for idx, input_elem in enumerate(soup.find_all(['input', 'textarea'])):
            if input_elem.get('placeholder'):
                selector = f"#{input_elem.get('id')}" if input_elem.get('id') else f"input[placeholder='{input_elem.get('placeholder')}']"
                suggestions.append({
                    "type": "input",
                    "selector": selector,
                    "title": input_elem.get('placeholder', ''),
                    "description": f"请在此输入{input_elem.get('placeholder', '')}",
                    "priority": 8
                })

        # 建议2: 主要按钮
        for btn in soup.find_all('button'):
            if btn.get('type') in ['submit', None]:
                text = btn.get_text(strip=True)
                selector = f"#{btn.get('id')}" if btn.get('id') else f"button:contains('{text}')"
                suggestions.append({
                    "type": "button",
                    "selector": selector,
                    "title": f"点击{text}",
                    "description": f"完成填写后，点击{text}按钮继续",
                    "priority": 9
                })

        # 建议3: 表单
        for idx, form in enumerate(soup.find_all('form')):
            selector = f"#{form.get('id')}" if form.get('id') else f"form:nth-of-type({idx+1})"
            suggestions.append({
                "type": "form",
                "selector": selector,
                "title": "填写表单",
                "description": "请填写以下表单信息",
                "priority": 10
            })

        # 按优先级排序
        suggestions.sort(key=lambda x: x['priority'], reverse=True)

        return suggestions[:10]  # 返回前10个建议
