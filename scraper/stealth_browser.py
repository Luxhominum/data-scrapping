"""
Stealth Browser Engine with Playwright & Human Interaction Emulation
"""
import asyncio
import time
import random
import os
from typing import Optional
from scraper.config import USER_AGENTS, get_random_headers

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class StealthBrowserManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Any] = None
        self.context: Optional[Any] = None

    async def get_page(self):
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed. Install via `playwright install chromium`.")
        
        playwright = await async_playwright().start()
        user_agent = random.choice(USER_AGENTS)
        
        browser = await playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
                "--disable-dev-shm-usage",
                "--disable-browser-side-navigation",
                "--disable-gpu"
            ]
        )
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1440, "height": 900},
            locale="id-ID",
            timezone_id="Asia/Jakarta"
        )
        page = await context.new_page()
        
        # Inject evasion script to mask webdriver
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = {
                runtime: {}
            };
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['id-ID', 'id', 'en-US', 'en']
            });
        """)
        
        return playwright, browser, page

    @staticmethod
    async def human_delay(min_sec: float = 1.0, max_sec: float = 2.5):
        delay = random.uniform(min_sec, max_sec)
        await asyncio.sleep(delay)

    @staticmethod
    async def smooth_scroll(page: "Page", steps: int = 4):
        for _ in range(steps):
            scroll_amount = random.randint(250, 550)
            await page.evaluate(f"window.scrollBy(0, {scroll_amount});")
            await asyncio.sleep(random.uniform(0.3, 0.8))
