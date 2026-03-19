from typing import Dict, Any, List
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import base64
import os


class PageAnalyzerService:
    """页面分析服务，截图并提取可交互元素"""

    def __init__(self):
        self.screenshot_dir = "/tmp/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        分析目标页面：截图 + 提取可交互元素
        
        Returns:
            {
                "screenshot": "base64_encoded_image",
                "suggested_elements": [...],
                "html_content": "...",
                "structure": {...}
            }
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1280, 'height': 800})
            
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_load_state('domcontentloaded')
                
                # 截图
                screenshot_path = f"{self.screenshot_dir}/{hash(url)}.png"
                await page.screenshot(path=screenshot_path, full_page=False)
                
                # 读取截图并转 base64
                with open(screenshot_path, 'rb') as f:
                    screenshot_base64 = base64.b64encode(f.read()).decode('utf-8')
                
                # 获取页面内容
                html_content = await page.content()
                
                # 分析可交互元素
                suggested_elements = await self._extract_interactive_elements(page)
                
                # 分析页面结构
                structure = await self._analyze_structure(page)
                
                await browser.close()
                
                # 清理临时文件
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)
                
                return {
                    "screenshot": screenshot_base64,
                    "suggested_elements": suggested_elements,
                    "html_content": html_content[:50000],  # 限制大小
                    "structure": structure
                }
                
            except Exception as e:
                await browser.close()
                raise Exception(f"Failed to analyze page: {str(e)}")

    async def _extract_interactive_elements(self, page) -> List[Dict[str, Any]]:
        """提取页面中的可交互元素"""
        elements = await page.evaluate('''() => {
            const interactiveSelectors = [
                'input:not([type="hidden"])',
                'button',
                'a[href]',
                'select',
                'textarea',
                '[role="button"]',
                '[role="link"]',
                '[onclick]',
                '.btn',
                '.button'
            ];
            
            const elements = [];
            const seen = new Set();
            
            interactiveSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach((el, index) => {
                    // 获取元素位置
                    const rect = el.getBoundingClientRect();
                    if (rect.width === 0 || rect.height === 0) return;
                    
                    // 生成唯一标识
                    const key = `${rect.top}-${rect.left}-${rect.width}-${rect.height}`;
                    if (seen.has(key)) return;
                    seen.add(key);
                    
                    // 获取元素信息
                    const id = el.id || '';
                    const classes = Array.from(el.classList).join(' ');
                    const text = el.textContent?.trim().substring(0, 50) || '';
                    const placeholder = el.placeholder || '';
                    const ariaLabel = el.getAttribute('aria-label') || '';
                    
                    // 生成推荐标题
                    let title = text || placeholder || ariaLabel || '';
                    if (!title) {
                        if (el.tagName === 'INPUT') {
                            const type = el.type || 'text';
                            title = `输入${type === 'password' ? '密码' : type === 'email' ? '邮箱' : '内容'}`;
                        } else if (el.tagName === 'BUTTON') {
                            title = '点击按钮';
                        } else if (el.tagName === 'A') {
                            title = '点击链接';
                        } else {
                            title = '交互元素';
                        }
                    }
                    
                    // 生成选择器
                    let selector = '';
                    if (id) {
                        selector = `#${id}`;
                    } else if (classes) {
                        const firstClass = classes.split(' ')[0];
                        // 检查class是否唯一
                        const sameClass = document.querySelectorAll(`.${firstClass}`).length;
                        if (sameClass === 1) {
                            selector = `.${firstClass}`;
                        } else {
                            selector = el.tagName.toLowerCase() + (classes ? `.${firstClass}` : '');
                        }
                    } else {
                        selector = el.tagName.toLowerCase();
                    }
                    
                    elements.push({
                        tag: el.tagName.toLowerCase(),
                        type: el.type || '',
                        id: id,
                        class: classes,
                        text: text,
                        title: title,
                        selector: selector,
                        rect: {
                            x: Math.round(rect.left),
                            y: Math.round(rect.top),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        },
                        center: {
                            x: Math.round(rect.left + rect.width / 2),
                            y: Math.round(rect.top + rect.height / 2)
                        }
                    });
                });
            });
            
            // 按位置排序（从上到下）
            return elements.sort((a, b) => a.rect.y - b.rect.y).slice(0, 10);
        }''')
        
        return elements

    async def _analyze_structure(self, page) -> Dict[str, Any]:
        """分析页面结构"""
        structure = await page.evaluate('''() => {
            return {
                title: document.title,
                url: window.location.href,
                forms: document.querySelectorAll('form').length,
                buttons: document.querySelectorAll('button').length,
                inputs: document.querySelectorAll('input').length,
                links: document.querySelectorAll('a').length
            };
        }''')
        return structure

    async def find_element_by_coordinate(self, page_url: str, x: int, y: int, width: int, height: int) -> Dict[str, Any]:
        """
        根据坐标找到对应的元素
        
        Args:
            page_url: 页面URL
            x, y: 区域左上角坐标
            width, height: 区域宽高
            
        Returns:
            元素信息，包括选择器
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1280, 'height': 800})
            
            try:
                await page.goto(page_url, wait_until='networkidle', timeout=30000)
                
                # 计算区域中心点
                centerX = x + width / 2
                centerY = y + height / 2
                
                # 在中心点执行 JS 获取元素
                element_info = await page.evaluate(f'''() => {{
                    const element = document.elementFromPoint({centerX}, {centerY});
                    if (!element) return null;
                    
                    // 获取元素信息
                    const rect = element.getBoundingClientRect();
                    const id = element.id || '';
                    const classes = Array.from(element.classList).join(' ');
                    const text = element.textContent?.trim().substring(0, 50) || '';
                    
                    // 生成选择器（优先级：id > data-testid > class > tag）
                    let selector = '';
                    if (id) {{
                        selector = `#${{id}}`;
                    }} else if (element.getAttribute('data-testid')) {{
                        selector = `[data-testid="${{element.getAttribute('data-testid')}}"]`;
                    }} else if (classes) {{
                        const classList = classes.split(' ').filter(c => c);
                        // 尝试找到能唯一标识的class组合
                        for (let i = 1; i <= classList.length; i++) {{
                            const testSelector = '.' + classList.slice(0, i).join('.');
                            if (document.querySelectorAll(testSelector).length === 1) {{
                                selector = testSelector;
                                break;
                            }}
                        }}
                        if (!selector) {{
                            selector = element.tagName.toLowerCase() + (classList[0] ? `.${{classList[0]}}` : '');
                        }}
                    }} else {{
                        // 使用路径
                        let path = element.tagName.toLowerCase();
                        let parent = element.parentElement;
                        let depth = 0;
                        while (parent && depth < 3) {{
                            const parentTag = parent.tagName.toLowerCase();
                            const siblings = Array.from(parent.children).filter(c => c.tagName === element.tagName);
                            if (siblings.length > 1) {{
                                const index = Array.from(parent.children).indexOf(element) + 1;
                                path = `${{parentTag}} > ${{path}}:nth-child(${{index}})`;
                            }} else {{
                                path = `${{parentTag}} > ${{path}}`;
                            }}
                            element = parent;
                            parent = element.parentElement;
                            depth++;
                        }}
                        selector = path;
                    }}
                    
                    return {{
                        tag: element.tagName.toLowerCase(),
                        id: id,
                        class: classes,
                        text: text,
                        selector: selector,
                        rect: {{
                            x: Math.round(rect.left),
                            y: Math.round(rect.top),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        }}
                    }};
                }}''')
                
                await browser.close()
                return element_info or {}
                
            except Exception as e:
                await browser.close()
                raise Exception(f"Failed to find element: {str(e)}")