"""
Screenshot Analyzer Service - Capture and analyze page screenshots
"""
import asyncio
from typing import Optional, List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
import io


class ScreenshotAnalyzerService:
    """Service for capturing and analyzing page screenshots"""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def capture_and_analyze(self, url: str) -> Dict[str, Any]:
        """
        Capture screenshot and analyze page for interactive elements
        """
        # Navigate to page
        await self.page.goto(url, wait_until='networkidle')
        
        # Get page dimensions
        viewport = await self.page.evaluate('''() => {
            return {
                width: document.documentElement.scrollWidth,
                height: document.documentElement.scrollHeight
            }
        }''')
        
        # Set viewport to full page height
        await self.page.set_viewport_size({
            'width': 1920,
            'height': min(viewport['height'], 5000)  # Limit max height
        })
        
        # Take screenshot
        screenshot_bytes = await self.page.screenshot(full_page=True)
        
        # Find interactive elements
        elements = await self.find_interactive_elements()
        
        return {
            'screenshot': screenshot_bytes,
            'width': viewport['width'],
            'height': min(viewport['height'], 5000),
            'suggested_regions': elements
        }
    
    async def find_interactive_elements(self) -> List[Dict[str, Any]]:
        """
        Find interactive elements on the page
        """
        elements = await self.page.evaluate('''() => {
            const interactiveSelectors = [
                'button', 'a', 'input', 'select', 'textarea',
                '[role="button"]', '[role="link"]', '[role="checkbox"]',
                '[role="radio"]', '[role="textbox"]', '[role="combobox"]',
                '[onclick]', '[class*="btn"]', '[class*="button"]'
            ];
            
            const elements = [];
            const seen = new Set();
            
            interactiveSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        const key = rect.x + ',' + rect.y + ',' + rect.width + ',' + rect.height;
                        if (!seen.has(key)) {
                            seen.add(key);
                            
                            // Generate selector
                            let selector = '';
                            if (el.id) {
                                selector = '#' + el.id;
                            } else if (el.className && typeof el.className === 'string') {
                                selector = '.' + el.className.split(' ')[0];
                            } else {
                                selector = el.tagName.toLowerCase();
                            }
                            
                            // Get element text
                            let title = '';
                            if (el.tagName === 'INPUT') {
                                title = el.placeholder || el.name || '输入框';
                            } else if (el.tagName === 'BUTTON') {
                                title = el.textContent.trim() || '按钮';
                            } else if (el.tagName === 'A') {
                                title = el.textContent.trim() || '链接';
                            } else {
                                title = el.textContent.trim().substring(0, 20) || '元素';
                            }
                            
                            elements.push({
                                x: Math.round(rect.x),
                                y: Math.round(rect.y),
                                width: Math.round(rect.width),
                                height: Math.round(rect.height),
                                element_type: el.tagName.toLowerCase(),
                                selector: selector,
                                title: title,
                                confidence: 0.8
                            });
                        }
                    }
                });
            });
            
            // Sort by confidence and limit results
            return elements.slice(0, 20);
        }''')
        
        return elements


async def analyze_page_with_screenshot(url: str) -> Dict[str, Any]:
    """
    Standalone function to analyze a page with screenshot
    """
    async with ScreenshotAnalyzerService() as service:
        return await service.capture_and_analyze(url)
