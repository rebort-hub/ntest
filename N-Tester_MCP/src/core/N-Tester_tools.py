# -*- coding: utf-8 -*-


# 加载 .env 文件（本地开发时使用）
from dotenv import load_dotenv
from pathlib import Path
import sys
import os

# 获取项目根目录（N-Tester_MCP/）
current_dir = Path(__file__).parent.parent.parent  # 从 src/core/ 回到根目录
config_dir = current_dir / 'config'

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(current_dir))

# 加载配置目录下的 .env 文件
load_dotenv(config_dir / '.env')

from fastmcp import FastMCP
import json
import requests
from typing import Any, Dict, List, Optional
import json
import ast  # ast 模块用于安全地解析 Python 字符串文字，因为您的输入使用了单引号而不是标准的 JSON 双引号
import doctest
import time
from pydantic import Field
from pydantic.v1.networks import host_regex
import logging

# 导入 Playwright
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

# 导入增强的 Playwright 集成
try:
    from src.integrations.playwright.enhanced_playwright_integration import PlaywrightIntegrationManager
    PLAYWRIGHT_INTEGRATION_AVAILABLE = True
    logging.info(" Playwright 集成模块已加载")
except ImportError as e:
    PLAYWRIGHT_INTEGRATION_AVAILABLE = False
    logging.warning(f" Playwright 集成模块未找到: {e}")
    logging.warning("将使用内置的 Playwright 功能")

# mcp 初始化
mcp = FastMCP(
    name="N-Tester_tools"
)

# 从环境变量读取后端地址
# 默认使用 Docker 网络中的 backend 服务名称
base_url = os.getenv("N-Tester_BACKEND_URL", "http://127.0.0.1:8018")

# 从环境变量读取 API Key
# 请在 .env 文件或环境变量中设置 N-Tester_API_KEY
api_key = os.getenv("N-Tester_API_KEY", "")

headers = {
    "accept": "application/json, text/plain,*/*",
    "X-API-Key": api_key
}

# Playwright 全局变量
_playwright = None
_browser: Optional[Browser] = None
_context: Optional[BrowserContext] = None
_page: Optional[Page] = None

# Playwright 集成管理器（用于调用官方 Playwright MCP）
_playwright_integration_manager: Optional[PlaywrightIntegrationManager] = None


async def get_browser():
    """获取或创建浏览器实例"""
    global _playwright, _browser
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,  # 无头模式，不显示窗口
            args=[
                '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
            ]
        )
    return _browser


async def get_page():
    """获取或创建页面实例"""
    global _context, _page
    if _page is None:
        browser = await get_browser()
        _context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        _page = await _context.new_page()
    return _page


async def cleanup_browser():
    """清理浏览器资源"""
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


def generate_custom_id():
    """
    生成一个基于毫秒级时间戳自增 + 静态 '00000' 的 ID。

    逻辑：
    1. 获取当前毫秒时间戳 current_ms。
    2. 如果 current_ms <= 上一次的 last_ts，则 last_ts += 1；否则 last_ts = current_ms。
    3. 返回 str(last_ts) + '00000'。

    Returns:
        str: 生成的 ID，例如 '171188304512300000000'.
    """
    # 第一次调用时初始化 last_ts
    if not hasattr(generate_custom_id, "last_ts"):
        generate_custom_id.last_ts = 0

    # 获取当前毫秒级时间戳
    current_ms = int(time.time() * 1000)

    # 自增逻辑：如果时间没走或者回退，就在上次基础上 +1
    if current_ms <= generate_custom_id.last_ts:
        generate_custom_id.last_ts += 1
    else:
        generate_custom_id.last_ts = current_ms

    # 拼接固定的 '00000'
    return str(generate_custom_id.last_ts) + "00000"


@mcp.tool(description="获取N-Tester平台项目的名称和对应id")
def get_project_name_and_id() -> str:
    """获取N-Tester平台项目的名称和对应id"""
    url = base_url + "/api/projects/"

    try:
        response = requests.get(url, headers=headers)
        
        # 检查 HTTP 状态码
        if response.status_code != 200:
            error_info = {
                "error": f"API 请求失败",
                "status_code": response.status_code,
                "url": url,
                "response_text": response.text[:500]
            }
            return json.dumps(error_info, indent=4, ensure_ascii=False)
        
        # 尝试解析 JSON
        data_dict = response.json()
        
    except requests.exceptions.ConnectionError:
        error_info = {
            "error": "无法连接到 API 服务器",
            "url": url,
            "base_url": base_url,
            "suggestion": "请检查后端服务是否启动，或检查 N-Tester_BACKEND_URL 环境变量配置"
        }
        return json.dumps(error_info, indent=4, ensure_ascii=False)
    except requests.exceptions.JSONDecodeError:
        error_info = {
            "error": "API 返回的不是有效的 JSON 格式",
            "status_code": response.status_code,
            "url": url,
            "response_text": response.text[:500]
        }
        return json.dumps(error_info, indent=4, ensure_ascii=False)
    except Exception as e:
        error_info = {
            "error": f"未知错误: {str(e)}",
            "url": url
        }
        return json.dumps(error_info, indent=4, ensure_ascii=False)

    # 用于存储提取出的 id 和 name 的列表
    extracted_data = []

    # 定义一个递归函数来处理嵌套的 children 列表
    def extract_info(nodes_list):
        if not isinstance(nodes_list, list):
            # 如果输入的不是列表，则停止或报错，取决于期望
            # 在您的结构中，data 和 children 应该是列表
            print("警告: 期望输入列表，但收到了非列表类型。")
            return

        for node in nodes_list:
            # 确保当前元素是字典
            if not isinstance(node, dict):
                print("警告: 期望列表元素是字典，但收到了非字典类型。")
                continue

            # 提取当前节点的 id 和 name
            # 使用 .get() 是安全的，即使键不存在也不会报错
            node_info = {
                "project_id": node.get("id"),
                "project_name": node.get("name")
            }
            extracted_data.append(node_info)

            # 如果当前节点有 children 且 children 是一个列表，则递归处理 children
            children = node.get("children")
            if isinstance(children, list):
                extract_info(children)  # 递归调用

    # 获取顶层 data 列表
    # 使用 .get('data') 是安全的，如果 'data' 键不存在，返回 None
    initial_nodes = data_dict.get('data')

    # 如果 initial_nodes 存在且是一个列表，则开始处理
    if isinstance(initial_nodes, list):
        extract_info(initial_nodes)
    else:
        print("获取到的数据结构不符合预期，未找到 'data' 列表。")

    # 将提取出的列表转换为 JSON 字符串
    # indent 参数用于格式化输出，ensure_ascii=False 保留中文字符和特殊字符
    output_json_string = json.dumps(extracted_data, indent=4, ensure_ascii=False)

    return output_json_string


@mcp.tool(description="根据N-Tester平台项目id去获取模块及id")
def module_to_which_it_belongs(project_id: int) -> str:
    """根据N-Tester平台项目id去获取模块及id"""
    url = base_url + f"/api/projects/{project_id}/testcase-modules/"

    data_dict = requests.get(url, headers=headers).json()

    # 用于存储提取出的 id 和 name 的列表
    extracted_data = []

    # 定义一个递归函数来处理嵌套的 children 列表
    def extract_info(nodes_list):
        if not isinstance(nodes_list, list):
            # 如果输入的不是列表，则停止或报错，取决于期望
            # 在您的结构中，data 和 children 应该是列表
            print("警告: 期望输入列表，但收到了非列表类型。")
            return

        for node in nodes_list:
            # 确保当前元素是字典
            if not isinstance(node, dict):
                print("警告: 期望列表元素是字典，但收到了非字典类型。")
                continue

            # 提取当前节点的 id 和 name
            # 使用 .get() 是安全的，即使键不存在也不会报错
            node_info = {
                "module_id": node.get("id"),
                "module_name": node.get("name")
            }
            extracted_data.append(node_info)

            # 如果当前节点有 children 且 children 是一个列表，则递归处理 children
            children = node.get("children")
            if isinstance(children, list):
                extract_info(children)  # 递归调用

    # 获取顶层 data 列表
    # 使用 .get('data') 是安全的，如果 'data' 键不存在，返回 None
    initial_nodes = data_dict.get('data')

    # 如果 initial_nodes 存在且是一个列表，则开始处理
    if isinstance(initial_nodes, list):
        extract_info(initial_nodes)
    else:
        print("获取到的数据结构不符合预期，未找到 'data' 列表。")

    # 将提取出的列表转换为 JSON 字符串
    # indent 参数用于格式化输出，ensure_ascii=False 保留中文字符和特殊字符
    output_json_string = json.dumps(extracted_data, indent=4, ensure_ascii=False)

    return output_json_string

@mcp.tool(description="获取N-Tester平台用例等级")
def obtain_use_case_level() -> list:
    """
    获取N-Tester平台用例等级
    """
    return ["P0","P1","P2","P3"]

@mcp.tool(description="获取N-Tester平台用例名称和对应id")
def get_the_list_of_use_cases(
        project_id: int = Field(description='项目id'),
        module_id: int= Field(description='模块id')):
    """获取N-Tester平台用例"""
    url = base_url + f"/api/projects/{project_id}/testcases/?page=1&page_size=1000&search=&module_id={module_id}"

    data_dict = requests.get(url, headers=headers).json()

    # 用于存储提取出的 id 和 name 的列表
    extracted_data = []

    for i in data_dict.get("data"):
        extracted_data.append({"case_id": i.get("id"), "case_name": i.get("name")})
    return  json.dumps(extracted_data, indent=4, ensure_ascii=False)


@mcp.tool(description="获取N-Tester平台用例详情")
def get_case_details(
        project_id: int = Field(description='项目id'),
        case_id: int= Field(description='用例id')):
    """获取N-Tester平台用例详情"""
    url = base_url + f"/api/projects/{project_id}/testcases/{case_id}/"

    data_dict = requests.get(url, headers=headers).json()

    # 用于存储提取出的 id 和 name 的列表
    extracted_data = data_dict.get("data")
    return json.dumps(extracted_data, indent=4, ensure_ascii=False)


@mcp.tool(description="N-Tester平台保存操作截图到对应用例中")
def save_operation_screenshots_to_the_application_case(
        project_id: int = Field(description='项目id'),
        case_id: int= Field(description='用例id'),
        file_path: str= Field(description='文件路径'),
        title: str = Field(description='截图标题'),
        description: str = Field(description='截图描述'),
        step_number: int = Field(description='步骤编号'),
        page_url: str = Field(description='截图页面URL')):
    """
    N-Tester平台保存操作截图到对应用例中
    """
    try:
        # 参数验证
        if not project_id:
            return "项目id不能为空"
        if not case_id:
            return "用例id不能为空"
        if not file_path:
            return "文件路径不能为空"
        if not title:
            return "截图标题不能为空"

        # 检查文件是否存在
        import os
        if not os.path.exists(file_path):
            return f"文件不存在: {file_path}"

        url = base_url + f"/api/projects/{project_id}/testcases/{case_id}/upload-screenshots/"

        # 根据文件扩展名确定 MIME 类型
        file_ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif'
        }
        content_type = mime_types.get(file_ext, 'image/png')  # 默认为 png

        # 准备文件和表单数据
        with open(file_path, 'rb') as file:
            files = {'screenshots': (os.path.basename(file_path), file, content_type)}

            # 只添加有值的字段
            data = {'title': title}  # title 是必填的

            if description and description.strip():
                data['description'] = description
            if step_number is not None:
                data['step_number'] = str(step_number)
            if page_url and page_url.strip():
                data['page_url'] = page_url

            # 发起请求 - 注意这里不使用json参数，而是用data参数
            response = requests.post(url, headers=headers, files=files, data=data)

            # 检查响应状态
            response.raise_for_status()

            # 处理响应
            if response.status_code in [200, 201]:
                return f"截图 '{title}' 上传成功"
            else:
                return f"上传失败，状态码: {response.status_code}, 响应: {response.text}"

    except FileNotFoundError:
        return f"文件未找到: {file_path}"
    except requests.exceptions.HTTPError as e:
        return f"HTTP错误: {e}, 响应内容: {response.text if 'response' in locals() else '无响应内容'}"
    except Exception as e:
        return f"上传截图时发生错误: {str(e)}"

@mcp.tool(description='保存N-Tester平台功能测试用例')
def add_functional_case(
        project_id: int = Field(description='项目id'),
        name: str = Field(description='用例名称'),
        precondition: str = Field(description='前置条件'),
        level: str = Field(description='用例等级'),
        module_id: int = Field(description='模块id'),
        steps: list = Field(description='用例步骤,示例：,[{"step_number": 1,"description": "步骤描述1","expected_result": "预期结果1"},{"step_number": 2,"description": "步骤描述2","expected_result": "预期结果2"}]'),
        notes: str = Field(description='备注')):
    """
    保N-Tester平台存N-Tester平台功能测试用例
    """
    try:
        if not project_id:
            return "项目id不能为空"
        if not name:
            return "用例名称不能为空"
        if not precondition:
            return "前置条件不能为空"
        if not level:
            return "用例等级不能为空"
        if not module_id:
            return "模块id不能为空"
        if not steps:
            return "用例步骤不能为空"

        url = base_url + f"/api/projects/{project_id}/testcases/"
        data = {
            "name": name,
            "precondition": precondition,
            "level": level,
            "module_id": module_id,
            "steps": steps,
            "notes": notes
        }

        # 发起请求
        response = requests.post(url, headers=headers, json=data)
        print("status =", response.status_code)
        print("content-type =", response.headers.get("Content-Type"))
        print("body-preview =", response.text[:200])
        # 如有非 2xx 状态码直接抛异常
        response.raise_for_status()
        # 201，代表成功保存
        if response.json().get("code") == 201:
            return f"用例：{name}保存成功"
        else:
            return "保存失败，请重试"
    except requests.exceptions.HTTPError as e:
        print("HTTPError =", e)
        return e

@mcp.tool(description='编辑N-Tester平台功能测试用例')
def edit_functional_case(
        project_id: int = Field(description='项目id'),
        case_id: int = Field(description='用例id'),
        name: str = Field(description='用例名称'),
        precondition: str = Field(description='前置条件'),
        level: str = Field(description='用例等级'),
        module_id: int = Field(description='模块id'),
        steps: list = Field(description='用例步骤,示例：,[{"step_number": 1,"description": "步骤描述1","expected_result": "预期结果1"},{"step_number": 2,"description": "步骤描述2","expected_result": "预期结果2"}]'),
        notes: str = Field(description='备注')):
    """
    编辑N-Tester平台功能测试用例
    """
    try:
        if not project_id:
            return "项目id不能为空"
        if not case_id:
            return "用例id不能为空"
        
        url = base_url + f"/api/projects/{project_id}/testcases/{case_id}/"
        data = {
                "name": name,
                "precondition": precondition,
                "level": level,
                "module_id": module_id,
                "steps": steps,
                "notes": notes
                }

        # 发起请求
        response = requests.patch(url, headers=headers, json=data)
        print("status =", response.status_code)
        print("content-type =", response.headers.get("Content-Type"))
        print("body-preview =", response.text[:200])
        # 如有非 2xx 状态码直接抛异常
        response.raise_for_status()
        # 200，代表成功编辑
        if response.json().get("code") == 200:
            return f"用例：{name}编辑成功"
        else:
            return "编辑失败，请重试"
    except requests.exceptions.HTTPError as e:
        print("HTTPError =", e)
        return e


# ============ Playwright 浏览器操作工具 ============

async def get_browser():
    """获取或创建浏览器实例"""
    global _browser, _playwright
    if _browser is None:
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
    return _browser


async def get_page():
    """获取或创建页面实例"""
    global _context, _page
    if _page is None:
        browser = await get_browser()
        _context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        _page = await _context.new_page()
    return _page


async def close_browser():
    """关闭浏览器"""
    global _browser, _context, _page, _playwright
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


@mcp.tool(description="导航到指定URL")
async def browser_navigate(url: str = Field(description='要访问的URL')) -> str:
    """导航到指定URL"""
    try:
        print(f"[DEBUG] browser_navigate 被调用: {url}")
        page = await get_page()
        print(f"[DEBUG] 页面对象已获取: {id(page)}")
        print(f"[DEBUG] 开始导航到: {url}")
        # 使用 domcontentloaded 而不是 networkidle，避免页面重定向问题
        response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        print(f"[DEBUG] 导航完成，响应状态: {response.status if response else 'None'}")
        print(f"[DEBUG] 当前 URL: {page.url}")
        return f"成功导航到: {url}"
    except Exception as e:
        print(f"[ERROR] 导航失败: {e}")
        return f"导航失败: {str(e)}"


@mcp.tool(description="获取页面快照（包含标题、URL、可见文本等）")
async def browser_snapshot() -> dict:
    """获取页面快照"""
    try:
        print(f"[DEBUG] browser_snapshot 被调用")
        page = await get_page()
        print(f"[DEBUG] 页面对象已获取: {id(page)}")
        print(f"[DEBUG] 当前 URL: {page.url}")
        
        # 获取页面信息
        title = await page.title()
        url = page.url
        print(f"[DEBUG] 页面标题: '{title}', URL: '{url}'")
        
        # 获取页面文本内容（限制长度）
        text_content = await page.evaluate('''() => {
            return document.body.innerText.substring(0, 2000);
        }''')
        print(f"[DEBUG] 文本内容长度: {len(text_content)}")
        
        # 获取所有链接
        links = await page.evaluate('''() => {
            const links = Array.from(document.querySelectorAll('a'));
            return links.slice(0, 20).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }));
        }''')
        
        # 获取所有按钮
        buttons = await page.evaluate('''() => {
            const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'));
            return buttons.slice(0, 20).map(btn => ({
                text: btn.innerText || btn.value || '',
                type: btn.type || 'button'
            }));
        }''')
        
        # 获取所有输入框
        inputs = await page.evaluate('''() => {
            const inputs = Array.from(document.querySelectorAll('input, textarea'));
            return inputs.slice(0, 20).map(input => ({
                type: input.type || 'text',
                name: input.name || '',
                placeholder: input.placeholder || ''
            }));
        }''')
        
        print(f"[DEBUG] 快照完成: {len(links)} 个链接, {len(buttons)} 个按钮, {len(inputs)} 个输入框")
        
        return {
            "title": title,
            "url": url,
            "text_content": text_content,
            "links": links,
            "buttons": buttons,
            "inputs": inputs
        }
    except Exception as e:
        return {"error": f"获取快照失败: {str(e)}"}


@mcp.tool(description="点击页面元素")
async def browser_click(
    selector: str = Field(description='元素选择器'),
    timeout: int = Field(default=5000, description='超时时间(毫秒)')
) -> str:
    """点击页面元素"""
    try:
        page = await get_page()
        await page.click(selector, timeout=timeout)
        return f"成功点击元素: {selector}"
    except Exception as e:
        return f"点击失败: {str(e)}"


@mcp.tool(description="在输入框中输入文本")
async def browser_type(
    selector: str = Field(description='输入框选择器'),
    text: str = Field(description='要输入的文本'),
    timeout: int = Field(default=5000, description='超时时间(毫秒)')
) -> str:
    """在输入框中输入文本"""
    try:
        page = await get_page()
        await page.fill(selector, text, timeout=timeout)
        return f"成功在 {selector} 中输入文本"
    except Exception as e:
        return f"输入失败: {str(e)}"


@mcp.tool(description="等待元素出现")
async def browser_wait_for(
    selector: str = Field(description='元素选择器'),
    timeout: int = Field(default=5000, description='超时时间(毫秒)')
) -> str:
    """等待元素出现"""
    try:
        page = await get_page()
        await page.wait_for_selector(selector, timeout=timeout)
        return f"元素已出现: {selector}"
    except Exception as e:
        return f"等待失败: {str(e)}"


@mcp.tool(description="截取页面截图")
async def browser_take_screenshot(
    path: str = Field(default="screenshot.png", description='截图保存路径')
) -> str:
    """截取页面截图"""
    try:
        page = await get_page()
        await page.screenshot(path=path, full_page=True)
        return f"截图已保存到: {path}"
    except Exception as e:
        return f"截图失败: {str(e)}"


@mcp.tool(description="获取当前页面截图（base64格式）")
async def browser_screenshot_base64(
    full_page: bool = Field(default=False, description='是否截取整个页面'),
    quality: int = Field(default=50, description='JPEG质量(1-100)，数值越小文件越小')
) -> str:
    """获取当前页面截图，返回 base64 编码的字符串"""
    import base64
    try:
        page = await get_page()
        
        # 等待页面稳定（确保所有动画和加载完成）
        await page.wait_for_load_state('networkidle', timeout=3000)
        
        # 使用 JPEG 格式并设置质量来压缩截图
        screenshot_bytes = await page.screenshot(
            type='jpeg',  # 使用 JPEG 格式（比 PNG 小很多）
            quality=quality,  # 质量参数（1-100）
            full_page=full_page
        )
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        # 获取当前 URL 用于调试
        current_url = page.url
        
        return json.dumps({
            "screenshot": screenshot_base64,
            "url": current_url,
            "timestamp": time.time(),
            "full_page": full_page,
            "quality": quality,
            "size": len(screenshot_base64),
            "original_bytes": len(screenshot_bytes)
        })
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "screenshot": "",
            "timestamp": time.time()
        })


@mcp.tool(description="执行JavaScript代码")
async def browser_evaluate(
    script: str = Field(description='要执行的JavaScript代码')
) -> Any:
    """执行JavaScript代码"""
    try:
        page = await get_page()
        result = await page.evaluate(script)
        return result
    except Exception as e:
        return f"执行失败: {str(e)}"


@mcp.tool(description="导航并获取页面快照（一步完成，避免页面重定向问题）")
async def browser_navigate_and_snapshot(url: str = Field(description='要访问的URL')) -> dict:
    """导航到指定URL并立即获取页面快照"""
    try:
        import base64
        import time
        
        start_time = time.time()
        print(f"[DEBUG] browser_navigate_and_snapshot 被调用: {url}")
        page = await get_page()
        print(f"[DEBUG] 页面对象已获取: {id(page)}")
        
        # 导航到URL
        print(f"[DEBUG] 开始导航到: {url}")
        response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        print(f"[DEBUG] 导航完成，响应状态: {response.status if response else 'None'}")
        print(f"[DEBUG] 导航后立即检查 URL: {page.url}")
        
        # 截图（base64编码）
        screenshot_bytes = await page.screenshot(type='png', full_page=False)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        print(f"[DEBUG] 截图完成，大小: {len(screenshot_base64)} 字符")
        
        # 立即获取快照（不等待）
        title = await page.title()
        page_url = page.url
        print(f"[DEBUG] 页面标题: '{title}', URL: '{page_url}'")
        
        text_content = await page.evaluate('''() => {
            return document.body.innerText.substring(0, 2000);
        }''')
        print(f"[DEBUG] 文本内容长度: {len(text_content)}")
        
        links = await page.evaluate('''() => {
            const links = Array.from(document.querySelectorAll('a'));
            return links.slice(0, 20).map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }));
        }''')
        
        buttons = await page.evaluate('''() => {
            const buttons = Array.from(document.querySelectorAll('button, input[type="button"], input[type="submit"]'));
            return buttons.slice(0, 20).map(btn => ({
                text: btn.innerText || btn.value || '',
                type: btn.type || 'button'
            }));
        }''')
        
        inputs = await page.evaluate('''() => {
            const inputs = Array.from(document.querySelectorAll('input, textarea'));
            return inputs.slice(0, 20).map(input => ({
                type: input.type || 'text',
                name: input.name || '',
                placeholder: input.placeholder || ''
            }));
        }''')
        
        duration = time.time() - start_time
        print(f"[DEBUG] 快照完成: {len(links)} 个链接, {len(buttons)} 个按钮, {len(inputs)} 个输入框, 耗时: {duration:.2f}秒")
        
        return {
            "title": title,
            "url": page_url,
            "text_content": text_content,
            "links": links,
            "buttons": buttons,
            "inputs": inputs,
            "screenshot": screenshot_base64,  # 添加截图
            "duration": duration,
            "timestamp": time.time()
        }
    except Exception as e:
        print(f"[ERROR] 导航并获取快照失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "error": str(e),
            "title": "",
            "url": "",
            "text_content": "",
            "links": [],
            "buttons": [],
            "inputs": [],
            "screenshot": "",
            "duration": 0,
            "timestamp": time.time()
        }


@mcp.tool(description="关闭浏览器")
async def browser_close() -> str:
    """关闭浏览器"""
    try:
        await cleanup_browser()
        return "浏览器已关闭"
    except Exception as e:
        return f"关闭失败: {str(e)}"


if __name__ == "__main__":
    import asyncio
    
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 初始化函数（在 mcp.run 之前调用）
    async def initialize_playwright_integration():
        """初始化 Playwright 集成"""
        global _playwright_integration_manager
        
        print("=" * 60)
        print("N-Tester MCP 增强版启动中...")
        print("=" * 60)
        
        # 检查是否启用 Playwright 集成
        enable_playwright_integration = os.getenv(
            "ENABLE_PLAYWRIGHT_INTEGRATION", "true"
        ).lower() == "true"
        
        if enable_playwright_integration and PLAYWRIGHT_INTEGRATION_AVAILABLE:
            print("\n初始化 Playwright 集成...")
            
            # 获取 Playwright MCP URL
            playwright_url = os.getenv("PLAYWRIGHT_HTTP_URL", "http://127.0.0.1:3000")
            
            try:
                # 创建集成管理器
                _playwright_integration_manager = PlaywrightIntegrationManager(playwright_url)
                
                # 初始化
                success = await _playwright_integration_manager.initialize()
                
                if success:
                    print(f" Playwright 集成初始化成功")
                    print(f" 连接地址: {playwright_url}")
                    
                    # 注册增强工具到 MCP 服务器
                    await _playwright_integration_manager.register_tools_to_mcp_server(mcp)
                    print(" 增强 Playwright 工具已注册")
                else:
                    print(" Playwright 集成初始化失败，将使用内置功能")
                    _playwright_integration_manager = None
                    
            except Exception as e:
                print(f" Playwright 集成初始化错误: {e}")
                print(" 将使用内置 Playwright 功能")
                _playwright_integration_manager = None
        else:
            if not enable_playwright_integration:
                print(" Playwright 集成已禁用（ENABLE_PLAYWRIGHT_INTEGRATION=false）")
            if not PLAYWRIGHT_INTEGRATION_AVAILABLE:
                print(" Playwright 集成模块不可用")
            print(" 使用内置 Playwright 功能")
        
        print("\n" + "=" * 60)
        print(" N-Tester MCP 服务已启动")
        print("=" * 60)
        print(f" 监听地址: http://0.0.0.0:8006")
        print(f" API Key: {api_key[:20]}..." if api_key else "🔑 API Key: 未设置")
        print(f" 后端地址: {base_url}")
        
        if _playwright_integration_manager:
            print(f" Playwright 集成: 已启用")
        else:
            print(f" Playwright 集成: 使用内置功能")
        
        print("=" * 60)
        print("\n按 Ctrl+C 停止服务\n")
    
    # 先运行初始化
    asyncio.run(initialize_playwright_integration())
    
    # 然后启动 MCP 服务器（mcp.run 会创建自己的事件循环）
    # 使用 streamable-http 传输方式
    # host="0.0.0.0" 允许从其他容器访问
    # port=8006 指定端口
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8006)