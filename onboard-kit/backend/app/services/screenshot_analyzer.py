"""
V2 Screenshot Analysis Service - Using Playwright to capture and analyze pages
"""
import asyncio
import base64
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, ElementHandle


class SuggestedRegion:
    """Recommended interactive region"""
    def __init__(self, 
                 x: float, y: float, 
                 width: float, height: float,
                 element_type: str,
                 selector: str,
                 title: str,
                 confidence: float = 1.0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.element_type = element_type
        self.selector = selector
        self.title = title
        self.confidence = confidence
        self.is_added = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "element_type": self.element_type,
            "selector": self.selector,
            "title": self.title,
            "confidence": self.confidence,
            "is_added": self.is_added
        }


class ScreenshotAnalyzerService:
    """Screenshot analysis service"""
    
    INTERACTIVE_SELECTORS = [
        'input[type="email"]',
        'input[type="text"]:not([type="hidden"])',
        'input[type="password"]',
        'input[type="search"]',
        'input[type="tel"]',
        'input[type="url"]',
        'input[type="number"]',
        'textarea',
        'select',
        'button:not([type="submit"])',
        'button[type="submit"]',
        'input[type="submit"]',
        'input[type="button"]',
        'a.btn',
        'a.button',
        '[role="button"]',
        'a[href]:not([href^="#"])',
        '[role="link"]',
        '[role="textbox"]',
        '[role="combobox"]',
    ]
    
    def __init__(self):
        self.browser = None
        self.context = None
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1440, 'height': 900}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def capture_and_analyze(self, url: str) -> Dict[str, Any]:
        """Capture screenshot and analyze page"""
        page = await self.context.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle', timeout=30000)
            await page.wait_for_timeout(1000)
            viewport_size = page.viewport_size
            screenshot_bytes = await page.screenshot(type='png', full_page=True)
            suggested_regions = await self._analyze_interactive_elements(page)
            
            return {
                "screenshot": screenshot_bytes,
                "width": viewport_size['width'],
                "height": viewport_size['height'],
                "suggested_regions": [r.to_dict() for r in suggested_regions]
            }
        finally:
            await page.close()
    
    async def _analyze_interactive_elements(self, page: Page) -> List[SuggestedRegion]:
        """Analyze interactive elements in page"""
        regions = []
        seen_selectors = set()
        
        for selector in self.INTERACTIVE_SELECTORS:
            try:
                elements = await page.query_selector_all(selector)
                for i, element in enumerate(elements):
                    is_visible = await element.is_visible()
                    if not is_visible:
                        continue
                    
                    bbox = await element.bounding_box()
                    if not bbox or bbox['width'] < 20 or bbox['height'] < 20:
                        continue
                    
                    element_id = await element.get_attribute('id')
                    element_name = await element.get_attribute('name')
                    element_class = await element.get_attribute('class')
                    element_placeholder = await element.get_attribute('placeholder')
                    
                    if element_id:
                        unique_selector = f'#{element_id}'
                    elif element_name:
                        unique_selector = f'[name="{element_name}"]'
                    elif element_class:
                        classes = element_class.split()[:2]
                        unique_selector = f'.{".".join(classes)}'
                    else:
                        unique_selector = f'{selector}:nth-of-type({i+1})'
                    
                    if unique_selector in seen_selectors:
                        continue
                    seen_selectors.add(unique_selector)
                    
                    title = await self._generate_title(
                        element, selector, element_placeholder, element_id, element_name
                    )
                    element_type = self._get_element_type(selector, element_id, element_name)
                    
                    region = SuggestedRegion(
                        x=bbox['x'],
                        y=bbox['y'],
                        width=bbox['width'],
                        height=bbox['height'],
                        element_type=element_type,
                        selector=unique_selector,
                        title=title,
                        confidence=1.0 if element_id or element_name else 0.8
                    )
                    regions.append(region)
            except Exception as e:
                print(f"Error processing selector {selector}: {e}")
                continue
        
        regions.sort(key=lambda r: (r.y, r.x))
        return regions[:15]
    
    async def _generate_title(self, element: ElementHandle, 
                             selector: str, 
                             placeholder: Optional[str],
                             element_id: Optional[str],
                             element_name: Optional[str]) -> str:
        """Generate step title"""
        text = await element.text_content()
        if text and text.strip():
            text = text.strip()[:20]
            if len(text) > 0:
                return text
        
        if placeholder:
            return f"Enter {placeholder}"
        
        if 'email' in selector or (element_id and 'email' in element_id.lower()):
            return "Enter Email"
        elif 'password' in selector or (element_id and 'password' in element_id.lower()):
            return "Enter Password"
        elif 'search' in selector or (element_id and 'search' in element_id.lower()):
            return "Search"
        elif 'submit' in selector or 'button[type="submit"]' in selector:
            return "Click Submit"
        elif 'button' in selector:
            return "Click Button"
        elif selector.startswith('a'):
            return "Click Link"
        elif 'input' in selector:
            return "Fill Content"
        
        return "Interactive Element"
    
    def _get_element_type(self, selector: str, element_id: Optional[str], 
                         element_name: Optional[str]) -> str:
        """Get element type"""
        check_str = f"{selector} {element_id or ''} {element_name or ''}".lower()
        
        if 'email' in check_str:
            return 'email'
        elif 'password' in check_str:
            return 'password'
        elif 'search' in check_str:
            return 'search'
        elif 'submit' in check_str or 'button' in check_str:
            return 'button'
        elif 'input' in check_str:
            return 'input'
        elif selector.startswith('a'):
            return 'link'
        elif 'textarea' in check_str:
            return 'textarea'
        elif 'select' in check_str:
            return 'select'
        
        return 'unknown'
    
    @staticmethod
    def screenshot_to_base64(screenshot_bytes: bytes) -> str:
        """Convert screenshot to base64"""
        return base64.b64encode(screenshot_bytes).decode('utf-8')


async def analyze_page_with_screenshot(url: str) -> Dict[str, Any]:
    """Analyze page and return screenshot with suggested regions"""
    async with ScreenshotAnalyzerService() as service:
        return await service.capture_and_analyze(url)
