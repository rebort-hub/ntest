"""
测试访问目标网站
"""
import asyncio
from playwright.async_api import async_playwright

async def test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        url = "http://47.113.104.130:9966"
        print(f"测试访问: {url}")
        print(f"导航前 URL: {page.url}")
        
        try:
            response = await page.goto(url, timeout=60000)
            print(f"响应状态: {response.status if response else 'None'}")
            print(f"响应URL: {response.url if response else 'None'}")
            print(f"导航后 page.url: {page.url}")
            
            await asyncio.sleep(5)
            print(f"等待5秒后 page.url: {page.url}")
            
            title = await page.title()
            print(f"标题: '{title}'")
            
            # 尝试获取 HTML
            html = await page.content()
            print(f"HTML长度: {len(html)}")
            print(f"HTML前200字符: {html[:200]}")
            
        except Exception as e:
            print(f"错误: {e}")
        
        print("\n按任意键关闭浏览器...")
        await asyncio.sleep(10)
        await browser.close()

asyncio.run(test())
