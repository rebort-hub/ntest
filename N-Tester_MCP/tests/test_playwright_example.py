"""
测试 Playwright 访问 example.com
"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print(f"导航前 URL: {page.url}")
        await page.goto("http://example.com")
        print(f"导航后 URL: {page.url}")
        
        await asyncio.sleep(2)
        print(f"等待后 URL: {page.url}")
        
        title = await page.title()
        print(f"标题: {title}")
        
        await browser.close()

asyncio.run(test())
