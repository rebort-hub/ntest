"""
Playwright执行器
执行Playwright自动化脚本
"""
import logging
import asyncio
import tempfile
import os
import sys
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import traceback

logger = logging.getLogger(__name__)


class PlaywrightRunner:
    """Playwright脚本执行器"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="playwright_")
        self.screenshots_dir = os.path.join(self.temp_dir, "screenshots")
        self.videos_dir = os.path.join(self.temp_dir, "videos")
        
        # 创建目录
        os.makedirs(self.screenshots_dir, exist_ok=True)
        os.makedirs(self.videos_dir, exist_ok=True)
    
    async def execute_script(
        self,
        script_content: str,
        target_url: Optional[str] = None,
        timeout: int = 30,
        headless: bool = True,
        browser_type: str = "chromium",
        viewport: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """执行Playwright脚本"""
        start_time = datetime.now()
        result = {
            "success": False,
            "message": "",
            "error": "",
            "execution_time": 0.0,
            "screenshots": [],
            "videos": [],
            "logs": [],
            "metadata": {}
        }
        
        try:
            # 准备脚本文件
            script_file = await self._prepare_script_file(
                script_content, target_url, timeout, headless, browser_type, viewport
            )
            
            # 执行脚本
            execution_result = await self._execute_script_file(script_file, timeout)
            
            # 处理结果
            result.update(execution_result)
            result["success"] = execution_result.get("return_code", 1) == 0
            
            # 收集截图和视频
            result["screenshots"] = await self._collect_screenshots()
            result["videos"] = await self._collect_videos()
            
            if result["success"]:
                result["message"] = "Script executed successfully"
            else:
                result["error"] = execution_result.get("stderr", "Unknown error")
            
        except Exception as e:
            logger.error(f"Playwright script execution failed: {e}")
            result["error"] = str(e)
            result["logs"].append(f"Exception: {e}")
            result["logs"].append(traceback.format_exc())
        
        finally:
            end_time = datetime.now()
            result["execution_time"] = (end_time - start_time).total_seconds()
            
            # 清理临时文件
            await self._cleanup_temp_files()
        
        return result
    
    async def _prepare_script_file(
        self,
        script_content: str,
        target_url: Optional[str],
        timeout: int,
        headless: bool,
        browser_type: str,
        viewport: Optional[Dict[str, int]]
    ) -> str:
        """准备脚本文件"""
        try:
            # 处理脚本内容，注入配置
            processed_script = await self._process_script_content(
                script_content, target_url, timeout, headless, browser_type, viewport
            )
            
            # 写入临时文件
            script_file = os.path.join(self.temp_dir, "test_script.py")
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(processed_script)
            
            return script_file
            
        except Exception as e:
            logger.error(f"Prepare script file failed: {e}")
            raise
    
    async def _process_script_content(
        self,
        script_content: str,
        target_url: Optional[str],
        timeout: int,
        headless: bool,
        browser_type: str,
        viewport: Optional[Dict[str, int]]
    ) -> str:
        """处理脚本内容，注入配置"""
        try:
            # 添加必要的导入
            imports = """
import asyncio
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 配置参数
SCREENSHOTS_DIR = r"{screenshots_dir}"
VIDEOS_DIR = r"{videos_dir}"
TARGET_URL = "{target_url}"
TIMEOUT = {timeout}
HEADLESS = {headless}
BROWSER_TYPE = "{browser_type}"
VIEWPORT = {viewport}

""".format(
                screenshots_dir=self.screenshots_dir,
                videos_dir=self.videos_dir,
                target_url=target_url or "https://example.com",
                timeout=timeout,
                headless=str(headless).lower(),
                browser_type=browser_type,
                viewport=json.dumps(viewport or {"width": 1920, "height": 1080})
            )
            
            # 添加辅助函数
            helper_functions = """
async def take_screenshot(page, name="screenshot"):
    \"\"\"截图辅助函数\"\"\"
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"{name}_{timestamp}.png")
        await page.screenshot(path=screenshot_path, full_page=True)
        logger.info(f"Screenshot saved: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        return None

async def wait_for_element(page, selector, timeout=TIMEOUT*1000):
    \"\"\"等待元素出现\"\"\"
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return True
    except Exception as e:
        logger.error(f"Wait for element failed: {e}")
        return False

"""
            
            # 处理原始脚本内容
            processed_content = script_content
            
            # 如果脚本中没有浏览器启动代码，添加标准的启动代码
            if "async_playwright()" not in processed_content:
                processed_content = self._wrap_script_with_playwright(processed_content)
            
            # 组合最终脚本
            final_script = imports + helper_functions + processed_content
            
            return final_script
            
        except Exception as e:
            logger.error(f"Process script content failed: {e}")
            raise
    
    def _wrap_script_with_playwright(self, script_content: str) -> str:
        """用Playwright启动代码包装脚本"""
        wrapper = """
async def main():
    async with async_playwright() as p:
        browser = await getattr(p, BROWSER_TYPE).launch(
            headless=HEADLESS,
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        try:
            context = await browser.new_context(
                viewport=VIEWPORT,
                record_video_dir=VIDEOS_DIR if VIDEOS_DIR else None
            )
            
            page = await context.new_page()
            
            # 设置默认超时
            page.set_default_timeout(TIMEOUT * 1000)
            
            # 执行用户脚本
{user_script}
            
            logger.info("Script execution completed successfully")
            
        except Exception as e:
            logger.error(f"Script execution failed: {{e}}")
            # 截图保存错误现场
            try:
                await take_screenshot(page, "error")
            except:
                pass
            raise
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
""".format(user_script=self._indent_script(script_content, 12))
        
        return wrapper
    
    def _indent_script(self, script: str, spaces: int) -> str:
        """给脚本添加缩进"""
        indent = " " * spaces
        lines = script.split('\n')
        indented_lines = [indent + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)
    
    async def _execute_script_file(self, script_file: str, timeout: int) -> Dict[str, Any]:
        """执行脚本文件"""
        try:
            # 准备执行环境
            env = os.environ.copy()
            env['PYTHONPATH'] = os.pathsep.join(sys.path)
            
            # 执行脚本
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=self.temp_dir
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout + 10  # 给额外的缓冲时间
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Script execution timeout after {timeout} seconds")
            
            return {
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore')
            }
            
        except Exception as e:
            logger.error(f"Execute script file failed: {e}")
            raise
    
    async def _collect_screenshots(self) -> List[str]:
        """收集截图文件"""
        try:
            screenshots = []
            if os.path.exists(self.screenshots_dir):
                for filename in os.listdir(self.screenshots_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        screenshots.append(os.path.join(self.screenshots_dir, filename))
            return screenshots
        except Exception as e:
            logger.error(f"Collect screenshots failed: {e}")
            return []
    
    async def _collect_videos(self) -> List[str]:
        """收集视频文件"""
        try:
            videos = []
            if os.path.exists(self.videos_dir):
                for filename in os.listdir(self.videos_dir):
                    if filename.lower().endswith(('.webm', '.mp4')):
                        videos.append(os.path.join(self.videos_dir, filename))
            return videos
        except Exception as e:
            logger.error(f"Collect videos failed: {e}")
            return []
    
    async def _cleanup_temp_files(self):
        """清理临时文件"""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception as e:
            logger.warning(f"Cleanup temp files failed: {e}")
    
    async def validate_script(self, script_content: str) -> Dict[str, Any]:
        """验证脚本语法"""
        try:
            # Python语法检查
            import ast
            ast.parse(script_content)
            
            # 检查Playwright相关导入
            has_playwright_import = (
                "from playwright" in script_content or
                "import playwright" in script_content
            )
            
            # 检查async/await使用
            has_async_await = (
                "async def" in script_content or
                "await " in script_content
            )
            
            warnings = []
            if not has_playwright_import:
                warnings.append("Script may be missing Playwright imports")
            if not has_async_await:
                warnings.append("Script may be missing async/await syntax")
            
            return {
                "valid": True,
                "message": "Script syntax is valid",
                "warnings": warnings
            }
            
        except SyntaxError as e:
            return {
                "valid": False,
                "error": f"Python syntax error: {e.msg}",
                "line": e.lineno,
                "column": e.offset
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
    
    async def get_browser_info(self) -> Dict[str, Any]:
        """获取浏览器信息"""
        try:
            # 检查Playwright是否安装
            try:
                from playwright.async_api import async_playwright
                playwright_installed = True
            except ImportError:
                playwright_installed = False
            
            # 检查浏览器是否安装
            browsers_info = {}
            if playwright_installed:
                try:
                    async with async_playwright() as p:
                        for browser_name in ['chromium', 'firefox', 'webkit']:
                            try:
                                browser = getattr(p, browser_name)
                                # 尝试启动浏览器
                                instance = await browser.launch(headless=True)
                                version = await instance.version()
                                await instance.close()
                                browsers_info[browser_name] = {
                                    "available": True,
                                    "version": version
                                }
                            except Exception as e:
                                browsers_info[browser_name] = {
                                    "available": False,
                                    "error": str(e)
                                }
                except Exception as e:
                    logger.error(f"Get browser info failed: {e}")
            
            return {
                "playwright_installed": playwright_installed,
                "browsers": browsers_info,
                "temp_dir": self.temp_dir
            }
            
        except Exception as e:
            logger.error(f"Get browser info failed: {e}")
            return {
                "playwright_installed": False,
                "browsers": {},
                "error": str(e)
            }


# 全局Playwright执行器实例
_playwright_runner = None


def get_playwright_runner() -> PlaywrightRunner:
    """获取Playwright执行器实例"""
    global _playwright_runner
    if _playwright_runner is None:
        _playwright_runner = PlaywrightRunner()
    return _playwright_runner


async def cleanup_playwright_runner():
    """清理Playwright执行器"""
    global _playwright_runner
    if _playwright_runner:
        await _playwright_runner._cleanup_temp_files()
        _playwright_runner = None