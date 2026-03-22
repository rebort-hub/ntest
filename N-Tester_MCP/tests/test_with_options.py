"""
测试不同的浏览器选项
"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        url = "http://47.113.104.130:9966"
        print(f"测试访问: {url}")
        
        try:
            print("开始导航...")
            response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            print(f"响应状态: {response.status}")
            print(f"响应URL: {response.url}")
            print(f"page.url: {page.url}")
            
            # 立即获取 HTML
            html = await page.content()
            print(f"\n立即获取 HTML长度: {len(html)}")
            
            await asyncio.sleep(2)
            print(f"\n等待2秒后 page.url: {page.url}")
            
            html2 = await page.content()
            print(f"等待后 HTML长度: {len(html2)}")
            
            title = await page.title()
            print(f"标题: '{title}'")
            
            # 截图
            await page.screenshot(path="screenshot.png")
            print("已保存截图到 screenshot.png")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        
        await asyncio.sleep(5)
        await browser.close()

asyncio.run(test())
