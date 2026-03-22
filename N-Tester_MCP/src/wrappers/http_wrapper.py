"""
HTTP 包装器 - 为 N-Tester_MCP 提供简单的 HTTP API
解决 FastMCP streamable-http 调用复杂的问题
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import asyncio

# 导入 Playwright
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

app = FastAPI(title="N-Tester MCP HTTP Wrapper", version="1.0.0")

# 添加 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Playwright 全局变量
_playwright = None
_browser: Optional[Browser] = None
_context: Optional[BrowserContext] = None
_page: Optional[Page] = None


async def ensure_browser():
    """确保浏览器已启动"""
    global _playwright, _browser, _context, _page
    
    if _page is not None:
        return _page
    
    if _playwright is None:
        _playwright = await async_playwright().start()
    
    if _browser is None:
        # 启动浏览器，确保窗口可见
        _browser = await _playwright.chromium.launch(
            headless=False,
            args=[
                '--start-maximized',  # 最大化窗口
                '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
            ],
            slow_mo=500  # 每个操作延迟500毫秒，便于观察
        )
    
    if _context is None:
        # 创建上下文，设置视口大小
        _context = await _browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
    
    if _page is None:
        _page = await _context.new_page()
    
    return _page


async def close_browser():
    """关闭浏览器"""
    global _playwright, _browser, _context, _page
    
    if _page:
        await _page.close()
        _page = None
    
    if _context:
        await _context.close()
        _context = None
    
    if _browser:
        await _browser.close()
        _browser = None
    
    if _playwright:
        await _playwright.stop()
        _playwright = None


class NavigateRequest(BaseModel):
    url: str


class ClickRequest(BaseModel):
    selector: str
    timeout: Optional[int] = 30000


class TypeRequest(BaseModel):
    selector: str
    text: str
    timeout: Optional[int] = 30000


class WaitForRequest(BaseModel):
    selector: str
    timeout: Optional[int] = 30000


class ScreenshotRequest(BaseModel):
    path: str = "screenshot.png"


class EvaluateRequest(BaseModel):
    script: str


@app.get("/")
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": "N-Tester MCP HTTP Wrapper",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {"status": "healthy"}


@app.post("/api/browser/navigate")
async def api_navigate(request: NavigateRequest):
    """导航到指定URL"""
    try:
        page = await ensure_browser()
        await page.goto(request.url)
        return {"success": True, "result": f"已导航到 {request.url}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/browser/snapshot")
async def api_snapshot():
    """获取页面快照"""
    try:
        page = await ensure_browser()
        
        # 获取页面信息
        title = await page.title()
        url = page.url
        
        # 获取页面文本
        text_content = await page.evaluate("""
            () => document.body.innerText
        """)
        
        # 获取链接
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            })).filter(link => link.text)
        """)
        
        # 获取按钮
        buttons = await page.evaluate("""
            () => Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).map(btn => ({
                text: btn.innerText || btn.value || '',
                type: btn.tagName.toLowerCase()
            })).filter(btn => btn.text)
        """)
        
        # 获取输入框
        inputs = await page.evaluate("""
            () => Array.from(document.querySelectorAll('input:not([type="button"]):not([type="submit"]), textarea')).map(input => ({
                type: input.type || 'text',
                placeholder: input.placeholder || '',
                name: input.name || ''
            }))
        """)
        
        snapshot = {
            "title": title,
            "url": url,
            "text_content": text_content,
            "links": links,
            "buttons": buttons,
            "inputs": inputs
        }
        
        return {"success": True, "snapshot": snapshot}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browser/click")
async def api_click(request: ClickRequest):
    """点击元素"""
    try:
        page = await ensure_browser()
        await page.click(request.selector, timeout=request.timeout)
        return {"success": True, "result": f"已点击元素: {request.selector}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browser/type")
async def api_type(request: TypeRequest):
    """输入文本"""
    try:
        page = await ensure_browser()
        await page.fill(request.selector, request.text, timeout=request.timeout)
        return {"success": True, "result": f"已在 {request.selector} 中输入文本"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browser/wait")
async def api_wait(request: WaitForRequest):
    """等待元素"""
    try:
        page = await ensure_browser()
        await page.wait_for_selector(request.selector, timeout=request.timeout)
        return {"success": True, "result": f"元素 {request.selector} 已出现"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browser/screenshot")
async def api_screenshot(request: ScreenshotRequest):
    """截图"""
    try:
        page = await ensure_browser()
        await page.screenshot(path=request.path)
        return {"success": True, "result": f"截图已保存到 {request.path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browser/evaluate")
async def api_evaluate(request: EvaluateRequest):
    """执行 JavaScript"""
    try:
        page = await ensure_browser()
        result = await page.evaluate(request.script)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/browser/close")
async def api_close():
    """关闭浏览器"""
    try:
        await close_browser()
        return {"success": True, "result": "浏览器已关闭"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/explore")
async def api_explore(url: str, max_depth: int = 2):
    """
    一键探索 - 导航并获取快照
    这是后端最常用的接口
    """
    try:
        print(f"[DEBUG] 开始探索: {url}")
        page = await ensure_browser()
        print(f"[DEBUG] 浏览器已准备, page对象: {id(page)}")
        
        # 1. 导航到URL（等待 DOM 加载完成即可，不等待网络空闲）
        print(f"[DEBUG] 开始导航到: {url}")
        response = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        print(f"[DEBUG] 导航完成，响应状态: {response.status if response else 'None'}")
        print(f"[DEBUG] 导航后立即检查URL: {page.url}")
        
        # 2. 立即获取快照（不等待，避免页面被重定向）
        print(f"[DEBUG] 开始获取快照, page对象: {id(page)}")
        title = await page.title()
        page_url = page.url
        print(f"[DEBUG] 页面标题: '{title}', URL: '{page_url}'")
        
        text_content = await page.evaluate("() => document.body.innerText")
        print(f"[DEBUG] 文本内容长度: {len(text_content)}")
        if text_content:
            print(f"[DEBUG] 文本内容前100字符: {text_content[:100]}")
        
        links = await page.evaluate("""
            () => Array.from(document.querySelectorAll('a')).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            })).filter(link => link.text)
        """)
        
        buttons = await page.evaluate("""
            () => Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]')).map(btn => ({
                text: btn.innerText || btn.value || '',
                type: btn.tagName.toLowerCase()
            })).filter(btn => btn.text)
        """)
        
        inputs = await page.evaluate("""
            () => Array.from(document.querySelectorAll('input:not([type="button"]):not([type="submit"]), textarea')).map(input => ({
                type: input.type || 'text',
                placeholder: input.placeholder || '',
                name: input.name || ''
            }))
        """)
        
        snapshot = {
            "title": title,
            "url": page_url,
            "text_content": text_content,
            "links": links,
            "buttons": buttons,
            "inputs": inputs
        }
        
        print(f"[DEBUG] 快照完成: {len(links)} 个链接, {len(buttons)} 个按钮, {len(inputs)} 个输入框")
        
        return {
            "success": True,
            "url": url,
            "snapshot": snapshot
        }
    except Exception as e:
        print(f"[ERROR] 探索失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("=" * 60)
    print("N-Tester MCP HTTP Wrapper")
    print("=" * 60)
    print("启动 HTTP API 服务...")
    print("端口: 8080")
    print("文档: http://127.0.0.1:8080/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
