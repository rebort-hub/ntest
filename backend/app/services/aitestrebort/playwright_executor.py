"""
Playwright 执行器 - 独立进程版本

支持两种脚本格式：
1. 简单脚本：直接使用提供的 page 对象
2. 完整脚本：包含 sync_playwright() 和 run() 函数的独立脚本

对于完整脚本，会拦截 sync_playwright() 调用，注入截图功能。
"""

import base64
import json
import os
import sys
import tempfile
import time
import builtins
import threading
from contextlib import contextmanager

# 保存原始的 print 函数（必须在任何修改之前）
_original_print = builtins.print

# 线程锁，保护 stdout 输出，防止多个消息交错
_output_lock = threading.Lock()

# 获取 stdout 的文件描述符
_stdout_fd = sys.stdout.fileno()

# Frame 文件目录
_frame_dir = tempfile.mkdtemp(prefix='playwright_frames_')


def send_message(msg_type: str, data: dict):
    """发送消息到标准输出"""
    # 对于 frame 类型，将大数据写入文件，只传递文件路径
    if msg_type == 'frame' and 'data' in data:
        frame_data = data['data']
        # 创建临时文件保存 frame 数据
        frame_file = os.path.join(_frame_dir, f'frame_{time.time()}.b64')
        with open(frame_file, 'w', encoding='utf-8') as f:
            f.write(frame_data)
        # 发送文件路径而非数据
        message = json.dumps({'type': 'frame_file', 'path': frame_file}) + '\n'
    else:
        message = json.dumps({'type': msg_type, **data}) + '\n'
    
    message_bytes = message.encode('utf-8')
    with _output_lock:
        os.write(_stdout_fd, message_bytes)


def patched_print(*args, **kwargs):
    """补丁版本的 print，将输出转换为 JSON 日志消息"""
    # 生成打印内容
    output = ' '.join(str(arg) for arg in args)
    message = json.dumps({'type': 'log', 'message': output}) + '\n'
    message_bytes = message.encode('utf-8')
    with _output_lock:
        # 使用 os.write 直接写入 fd
        os.write(_stdout_fd, message_bytes)


def create_screenshot_page_wrapper(real_page, interval=0.1):
    """创建一个自动截图的 page 包装器"""
    last_screenshot_time = [0]
    frame_count = [0]
    
    def take_screenshot(silent=False):
        """执行截图并发送，silent=True 时不输出失败日志（用于脚本结束后的尝试截图）"""
        try:
            screenshot = real_page.screenshot(type='jpeg', quality=50)
            frame_data = base64.b64encode(screenshot).decode('utf-8')
            send_message('frame', {'data': frame_data})
            frame_count[0] += 1
            return True
        except Exception as e:
            if not silent:
                error_msg = str(e)
                # 如果是浏览器已关闭的错误，不输出日志
                if 'closed' not in error_msg.lower():
                    send_message('log', {'message': f'截图失败: {error_msg}'})
            return False
    
    def maybe_screenshot():
        """检查是否需要截图"""
        now = time.time()
        if now - last_screenshot_time[0] >= interval:
            take_screenshot()
            last_screenshot_time[0] = now
    
    class PageWrapper:
        """Page 对象包装器，在每次操作后自动截图"""
        
        # 标记这是一个包装器，用于 expect 函数识别
        _is_page_wrapper = True
        
        def __init__(self):
            self._real_page = real_page
        
        def _unwrap(self):
            """返回原始 page 对象，用于需要原始对象的场合（如 expect）"""
            return self._real_page
        
        def __getattr__(self, name):
            attr = getattr(self._real_page, name)
            if callable(attr):
                def wrapper(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    maybe_screenshot()
                    return result
                return wrapper
            return attr
        
        def screenshot(self, *args, **kwargs):
            """特殊处理 screenshot 方法 - 调试模式下不保存文件，只发送到前端"""
            # 移除 path 参数，调试模式下不保存文件
            kwargs.pop('path', None)
            # 截图并发送到前端
            screenshot_bytes = self._real_page.screenshot(*args, **kwargs)
            try:
                frame_data = base64.b64encode(screenshot_bytes).decode('utf-8')
                send_message('frame', {'data': frame_data})
                frame_count[0] += 1
            except Exception as e:
                send_message('log', {'message': f'发送截图帧失败: {str(e)}'})
            return screenshot_bytes
        
        # 显式定义常用方法，确保截图被触发
        def goto(self, *args, **kwargs):
            result = self._real_page.goto(*args, **kwargs)
            take_screenshot()  # goto 后强制截图
            return result
        
        def click(self, *args, **kwargs):
            result = self._real_page.click(*args, **kwargs)
            maybe_screenshot()
            return result
        
        def fill(self, *args, **kwargs):
            result = self._real_page.fill(*args, **kwargs)
            maybe_screenshot()
            return result
        
        def type(self, *args, **kwargs):
            result = self._real_page.type(*args, **kwargs)
            maybe_screenshot()
            return result
        
        def wait_for_selector(self, *args, **kwargs):
            result = self._real_page.wait_for_selector(*args, **kwargs)
            maybe_screenshot()
            return result
        
        def wait_for_load_state(self, *args, **kwargs):
            result = self._real_page.wait_for_load_state(*args, **kwargs)
            maybe_screenshot()
            return result
        
        def get_by_role(self, *args, **kwargs):
            return self._real_page.get_by_role(*args, **kwargs)
        
        def get_by_text(self, *args, **kwargs):
            return self._real_page.get_by_text(*args, **kwargs)
        
        def locator(self, *args, **kwargs):
            return self._real_page.locator(*args, **kwargs)
    
    return PageWrapper(), frame_count, take_screenshot


def create_patched_expect(original_expect):
    """创建一个能够处理 PageWrapper 的 expect 函数"""
    def patched_expect(actual, message=None):
        # 如果是 PageWrapper，解包获取原始 page
        if hasattr(actual, '_is_page_wrapper') and actual._is_page_wrapper:
            actual = actual._unwrap()
        if message:
            return original_expect(actual, message)
        return original_expect(actual)
    return patched_expect


def main():
    """主函数"""
    if len(sys.argv) < 2:
        send_message('status', {'status': 'error', 'message': '缺少参数'})
        sys.exit(1)
    
    # 从文件读取参数
    params_file = sys.argv[1]
    try:
        with open(params_file, 'r', encoding='utf-8') as f:
            params = json.load(f)
    except Exception as e:
        send_message('status', {'status': 'error', 'message': f'读取参数文件失败: {str(e)}'})
        sys.exit(1)
    
    script_content = params.get('script_content', '')
    target_url = params.get('target_url', '')
    headless = params.get('headless', False)
    fps = params.get('fps', 10)
    timeout_seconds = params.get('timeout_seconds', 60)
    
    screenshot_interval = 1 / fps
    total_frames = [0]
    
    # 替换全局 print 函数
    builtins.print = patched_print
    
    try:
        import playwright.sync_api as sync_api_module
        original_sync_playwright = sync_api_module.sync_playwright
        
        send_message('status', {'status': 'starting', 'message': '正在启动浏览器...'})
        
        # 检查脚本是否是完整脚本（包含 sync_playwright）
        is_full_script = 'sync_playwright' in script_content
        
        if is_full_script:
            # 完整脚本模式
            send_message('log', {'message': '检测到完整脚本模式'})
            
            # 存储所有创建的 page 对象和截图函数
            pages_and_screenshotters = []
            
            @contextmanager
            def patched_sync_playwright():
                """补丁版本的 sync_playwright"""
                with original_sync_playwright() as p:
                    original_chromium_launch = p.chromium.launch
                    
                    def patched_chromium_launch(*args, **kwargs):
                        kwargs['headless'] = headless
                        browser = original_chromium_launch(*args, **kwargs)
                        
                        original_new_context = browser.new_context
                        original_browser_new_page = browser.new_page
                        
                        def patched_new_context(*ctx_args, **ctx_kwargs):
                            context = original_new_context(*ctx_args, **ctx_kwargs)
                            original_context_new_page = context.new_page
                            
                            def patched_context_new_page(*page_args, **page_kwargs):
                                page = original_context_new_page(*page_args, **page_kwargs)
                                wrapped_page, frame_count, take_ss = create_screenshot_page_wrapper(
                                    page, screenshot_interval
                                )
                                pages_and_screenshotters.append((page, take_ss))
                                total_frames[0] = frame_count
                                return wrapped_page
                            
                            context.new_page = patched_context_new_page
                            return context
                        
                        def patched_browser_new_page(*page_args, **page_kwargs):
                            page = original_browser_new_page(*page_args, **page_kwargs)
                            wrapped_page, frame_count, take_ss = create_screenshot_page_wrapper(
                                page, screenshot_interval
                            )
                            pages_and_screenshotters.append((page, take_ss))
                            total_frames[0] = frame_count
                            return wrapped_page
                        
                        browser.new_context = patched_new_context
                        browser.new_page = patched_browser_new_page
                        return browser
                    
                    p.chromium.launch = patched_chromium_launch
                    yield p
            
            # 在模块级别打补丁，这样 from playwright.sync_api import sync_playwright 也会获取打补丁后的版本
            sync_api_module.sync_playwright = patched_sync_playwright
            
            # 准备执行环境
            exec_globals = {
                '__builtins__': builtins,
                'sync_playwright': patched_sync_playwright,
                'time': time,
                'sleep': time.sleep,
            }
            
            # 打补丁 expect 函数，使其支持 PageWrapper
            try:
                from playwright.sync_api import expect as original_expect
                patched_expect = create_patched_expect(original_expect)
                exec_globals['expect'] = patched_expect
                # 同时在模块级别打补丁
                sync_api_module.expect = patched_expect
            except ImportError:
                pass
            
            send_message('status', {'status': 'running', 'message': '开始执行脚本'})
            
            # 执行脚本
            exec(script_content, exec_globals)
            
            # 如果脚本定义了 run() 函数，调用它
            if 'run' in exec_globals and callable(exec_globals['run']):
                exec_globals['run']()
            
            # 最后再截几帧（静默模式，因为脚本可能已关闭浏览器）
            for page, take_ss in pages_and_screenshotters:
                try:
                    for _ in range(2):
                        take_ss(silent=True)
                        time.sleep(screenshot_interval)
                except Exception:
                    pass
            
            frame_count_value = total_frames[0][0] if isinstance(total_frames[0], list) else 0
            send_message('log', {'message': f'共发送 {frame_count_value} 帧'})
            send_message('status', {'status': 'completed', 'message': '脚本执行完成'})
            
        else:
            # 简单脚本模式
            send_message('log', {'message': '简单脚本模式'})
            
            with original_sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                page = browser.new_page()
                page.set_default_timeout(timeout_seconds * 1000)
                
                # 先创建包装器
                wrapped_page, frame_count, take_ss = create_screenshot_page_wrapper(
                    page, screenshot_interval
                )
                
                if target_url:
                    send_message('log', {'message': f'导航到: {target_url}'})
                    wrapped_page.goto(target_url)  # 使用包装器的 goto 以触发截图
                
                send_message('status', {'status': 'running', 'message': '开始执行脚本'})
                
                exec_globals = {
                    'page': wrapped_page,
                    'browser': browser,
                    '__builtins__': builtins,
                    'time': time,
                    'sleep': time.sleep,
                }
                
                exec(script_content, exec_globals)
                
                # 最后再截几帧
                for _ in range(3):
                    take_ss()
                    time.sleep(screenshot_interval)
                
                send_message('log', {'message': f'共发送 {frame_count[0]} 帧'})
                send_message('status', {'status': 'completed', 'message': '脚本执行完成'})
                
                browser.close()
        
    except Exception as e:
        import traceback
        send_message('log', {'message': traceback.format_exc()})
        send_message('status', {'status': 'error', 'message': f'执行出错: {str(e)}'})
        sys.exit(1)
    finally:
        # 恢复原始 print 函数
        builtins.print = _original_print
        # 恢复原始模块属性（如果做了猴子补丁）
        try:
            import playwright.sync_api as sync_api_module
            if 'original_sync_playwright' in dir():
                sync_api_module.sync_playwright = original_sync_playwright
            if 'original_expect' in dir():
                sync_api_module.expect = original_expect
        except Exception:
            pass


if __name__ == '__main__':
    main()