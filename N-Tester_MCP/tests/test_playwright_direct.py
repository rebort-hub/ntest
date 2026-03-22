"""
直接测试 Playwright 是否能正常工作
"""
import asyncio
from playwright.async_api import async_playwright

async def test_playwright():
    print("=" * 80)
    print("直接测试 Playwright")
    print("=" * 80)
    
    async with async_playwright() as p:
        print("\n1. 启动浏览器...")
        browser = await p.chromium.launch(headless=False)
        print("✓ 浏览器已启动")
        
        print("\n2. 创建上下文和页面...")
        context = await browser.new_context()
        page = await context.new_page()
        print(f"✓ 页面已创建, 当前URL: {page.url}")
        
        print("\n3. 导航到测试网站...")
        url = "http://47.113.104.130:9966"
        print(f"   目标URL: {url}")
        response = await page.goto(url, wait_until="load", timeout=30000)
        print(f"✓ 导航完成")
        print(f"   响应状态: {response.status if response else 'None'}")
        print(f"   当前URL: {page.url}")
        
        print("\n4. 等待3秒...")
        await asyncio.sleep(3)
        print(f"   等待后URL: {page.url}")
        
        print("\n5. 获取页面信息...")
        title = await page.title()
        text = await page.evaluate("() => document.body.innerText")
        print(f"   标题: '{title}'")
        print(f"   文本长度: {len(text)}")
        print(f"   文本前100字符: {text[:100]}")
        
        print("\n6. 关闭浏览器...")
        await browser.close()
        print("✓ 浏览器已关闭")
    
    print("\n" + "=" * 80)
    print("✓ 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_playwright())
