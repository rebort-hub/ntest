"""
Playwright 脚本执行器
执行生成的自动化测试脚本并记录结果
"""
import subprocess
import sys
import tempfile
import os
import re
import shutil
import logging
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

from fastapi import HTTPException

logger = logging.getLogger(__name__)


# 录屏注入代码模板
VIDEO_INJECTION_IMPORTS = '''import os
'''

VIDEO_INJECTION_CODE = '''
        # 动态录屏配置（由执行器注入）
        video_dir = os.environ.get('PLAYWRIGHT_VIDEO_DIR', '')
        _context_options = {"ignore_https_errors": True}
        if video_dir:
            _context_options["record_video_dir"] = video_dir
            _context_options["record_video_size"] = {"width": 1280, "height": 720}
'''


class ScriptExecutor:
    """
    执行 Playwright Python 脚本
    """
    
    def __init__(
        self,
        work_dir: Optional[str] = None,
        timeout_seconds: int = 300,
        browser_type: str = 'chromium'
    ):
        self.work_dir = work_dir or tempfile.mkdtemp(prefix='playwright_')
        self.timeout_seconds = timeout_seconds
        self.browser_type = browser_type
    
    def _inject_headless_setting(self, script_content: str, headless: bool) -> str:
        """
        动态替换脚本中的 headless 参数
        """
        headless_str = 'True' if headless else 'False'
        # 匹配 headless=True 或 headless=False
        modified = re.sub(
            r'(\.launch\([^)]*headless=)(True|False)',
            rf'\g<1>{headless_str}',
            script_content
        )
        if modified != script_content:
            logger.info(f"[ScriptExecutor] 已设置 headless={headless_str}")
        return modified
    
    def _inject_video_recording(self, script_content: str) -> str:
        """
        在脚本中注入录屏配置代码
        
        匹配 browser.new_context(...) 调用并替换为使用录屏配置
        """
        # 确保导入 os 模块
        if 'import os' not in script_content:
            # 在 from playwright 导入之前插入 os 导入
            script_content = re.sub(
                r'(from playwright\.sync_api import)',
                VIDEO_INJECTION_IMPORTS + r'\1',
                script_content
            )
        
        # 匹配 browser.new_context(...) 调用并替换
        # 模式：browser.new_context(任意参数)
        pattern = r'(\s+)(context\s*=\s*browser\.new_context\([^)]*\))'
        
        def replace_context(match):
            indent = match.group(1)
            # 替换为使用动态配置的版本
            return f'''{indent}# 动态录屏配置（由执行器注入）
{indent}video_dir = os.environ.get('PLAYWRIGHT_VIDEO_DIR', '')
{indent}_context_options = {{"ignore_https_errors": True}}
{indent}if video_dir:
{indent}    _context_options["record_video_dir"] = video_dir
{indent}    _context_options["record_video_size"] = {{"width": 1280, "height": 720}}
{indent}context = browser.new_context(**_context_options)'''
        
        modified = re.sub(pattern, replace_context, script_content)
        
        # 如果没有匹配到，记录警告
        if modified == script_content:
            logger.warning("[ScriptExecutor] 未找到 browser.new_context() 调用，无法注入录屏配置")
        else:
            logger.info("[ScriptExecutor] 已注入录屏配置代码")
        
        return modified
    
    def execute_script(
        self,
        script_content: str,
        use_pytest: bool = True,
        headless: bool = True,
        record_video: bool = False
    ) -> Dict[str, Any]:
        """
        执行脚本并返回结果
        
        Args:
            script_content: 脚本内容
            use_pytest: 是否使用 pytest 执行
            headless: 是否无头模式
            record_video: 是否录制视频
        
        Returns:
            执行结果字典
        """
        result = {
            'success': False,
            'output': '',
            'error_message': '',
            'stack_trace': '',
            'screenshots': [],
            'videos': [],  # 新增：视频列表
            'execution_time': 0,
            'started_at': datetime.now(),
            'completed_at': None
        }
        
        logger.info(f"[ScriptExecutor] 开始执行脚本, use_pytest={use_pytest}, headless={headless}, record_video={record_video}")
        logger.info(f"[ScriptExecutor] 工作目录: {self.work_dir}")
        
        # 动态替换 headless 设置
        script_content = self._inject_headless_setting(script_content, headless)
        
        # 如果需要录屏，动态注入录屏配置代码
        if record_video:
            script_content = self._inject_video_recording(script_content)
        
        logger.debug(f"[ScriptExecutor] 脚本内容预览:\n{script_content[:500]}...")
        
        try:
            # 创建临时脚本文件
            script_path = Path(self.work_dir) / 'test_script.py'
            script_path.write_text(script_content, encoding='utf-8')
            logger.info(f"[ScriptExecutor] 脚本文件已写入: {script_path}")
            
            # 确定执行命令 - 不使用可能不存在的插件参数
            if use_pytest:
                cmd = [
                    sys.executable, '-m', 'pytest',
                    str(script_path),
                    '-v',
                    '--tb=short',
                ]
            else:
                cmd = [sys.executable, str(script_path)]
            
            logger.info(f"[ScriptExecutor] 执行命令: {' '.join(cmd)}")
            
            # 设置环境变量
            env = os.environ.copy()
            env['PLAYWRIGHT_HEADLESS'] = '1' if headless else '0'
            env['PWDEBUG'] = '0'  # 禁用调试模式
            env['PYTHONIOENCODING'] = 'utf-8'  # 解决 Windows GBK 编码问题
            
            # 录屏目录（通过环境变量传递给脚本）
            video_dir = ''
            if record_video:
                video_dir = str(Path(self.work_dir) / 'videos')
                Path(video_dir).mkdir(parents=True, exist_ok=True)
                env['PLAYWRIGHT_VIDEO_DIR'] = video_dir
                logger.info(f"[ScriptExecutor] 录屏目录: {video_dir}")
            
            # 执行脚本
            start_time = datetime.now()
            logger.info(f"[ScriptExecutor] 开始执行, 超时时间: {self.timeout_seconds}秒")
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=self.timeout_seconds,
                cwd=self.work_dir,
                env=env
            )
            
            end_time = datetime.now()
            
            result['output'] = process.stdout or ''
            result['execution_time'] = (end_time - start_time).total_seconds()
            result['completed_at'] = datetime.now()
            
            logger.info(f"[ScriptExecutor] 执行完成, 返回码: {process.returncode}, 耗时: {result['execution_time']:.2f}秒")
            logger.info(f"[ScriptExecutor] 标准输出({len(result['output'])}字符):\n{result['output']}")
            if process.stderr:
                logger.info(f"[ScriptExecutor] 标准错误({len(process.stderr)}字符):\n{process.stderr}")
            
            if process.returncode == 0:
                result['success'] = True
                logger.info("[ScriptExecutor] ✅ 执行成功")
            else:
                result['error_message'] = process.stderr or '执行失败'
                result['stack_trace'] = process.stderr
                logger.error(f"[ScriptExecutor] ❌ 执行失败, stderr:\n{process.stderr}")
            
            # 收集截图并移动到持久化目录
            result['screenshots'] = self._persist_screenshots()
            logger.info(f"[ScriptExecutor] 截图数量: {len(result['screenshots'])}")
            
            # 收集视频并移动到持久化目录
            if record_video:
                result['videos'] = self._persist_videos()
                logger.info(f"[ScriptExecutor] 视频数量: {len(result['videos'])}")
            
        except subprocess.TimeoutExpired:
            result['error_message'] = f'执行超时: {self.timeout_seconds}秒'
            result['stack_trace'] = f'TimeoutExpired after {self.timeout_seconds}s'
            result['completed_at'] = datetime.now()
            logger.error(f"[ScriptExecutor] ❌ 执行超时: {self.timeout_seconds}秒")
            
        except Exception as e:
            result['error_message'] = str(e)
            result['stack_trace'] = f'{type(e).__name__}: {e}'
            result['completed_at'] = datetime.now()
            logger.exception("[ScriptExecutor] ❌ 脚本执行异常")
        
        return result
    
    def _persist_screenshots(self) -> List[str]:
        """
        将截图从临时目录移动到持久化的目录
        返回相对路径列表
        """
        screenshots = []
        temp_screenshots = list(Path(self.work_dir).glob('*.png'))
        
        if not temp_screenshots:
            return screenshots
        
        # 创建持久化目录
        persist_dir = Path('static/script_screenshots') / datetime.now().strftime('%Y%m%d')
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        for temp_path in temp_screenshots:
            # 生成唯一文件名避免冲突
            unique_name = f"{uuid.uuid4().hex[:8]}_{temp_path.name}"
            persist_path = persist_dir / unique_name
            
            try:
                shutil.copy2(temp_path, persist_path)
                # 存储相对路径
                relative_path = str(persist_path)
                screenshots.append(relative_path)
            except Exception as e:
                logger.warning(f"保存截图失败: {e}")
        
        return screenshots
    
    def _persist_videos(self) -> List[str]:
        """
        将视频从临时目录移动到持久化的目录
        返回相对路径列表
        """
        videos = []
        video_dir = Path(self.work_dir) / 'videos'
        
        if not video_dir.exists():
            return videos
        
        # Playwright 生成的视频是 .webm 格式
        temp_videos = list(video_dir.glob('*.webm'))
        
        if not temp_videos:
            return videos
        
        # 创建持久化目录
        persist_dir = Path('static/script_videos') / datetime.now().strftime('%Y%m%d')
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        for temp_path in temp_videos:
            # 生成唯一文件名避免冲突
            unique_name = f"{uuid.uuid4().hex[:8]}_{temp_path.name}"
            persist_path = persist_dir / unique_name
            
            try:
                shutil.copy2(temp_path, persist_path)
                # 存储相对路径
                relative_path = str(persist_path)
                videos.append(relative_path)
                logger.info(f"[ScriptExecutor] 视频已保存: {relative_path}")
            except Exception as e:
                logger.warning(f"保存视频失败: {e}")
        
        return videos
    
    def cleanup(self):
        """清理临时文件"""
        if self.work_dir and Path(self.work_dir).exists():
            shutil.rmtree(self.work_dir, ignore_errors=True)


def _cleanup_old_executions(script_id: str, max_executions: int = 15):
    """
    清理旧的执行记录，只保留最新的 max_executions 条
    同时删除关联的截图和视频文件
    
    Args:
        script_id: 脚本ID
        max_executions: 最多保留的执行记录数
    """
    # 这里应该连接数据库清理旧记录
    # 简化实现，实际项目中需要实现数据库操作
    logger.info(f"清理脚本 {script_id} 的旧执行记录，保留最新 {max_executions} 条")


async def execute_automation_script(
    script_id: str,
    script_content: str,
    script_type: str = 'playwright_python',
    target_url: str = '',
    timeout_seconds: int = 60,
    headless: bool = True,
    record_video: bool = False,
    max_executions: int = 15
) -> Dict[str, Any]:
    """
    执行自动化脚本并创建执行记录
    
    Args:
        script_id: 脚本ID
        script_content: 脚本内容
        script_type: 脚本类型
        target_url: 目标URL
        timeout_seconds: 超时时间
        headless: 是否无头模式
        record_video: 是否录制视频
        max_executions: 每个脚本最多保留的执行记录数，默认 15
    
    Returns:
        执行结果字典
    """
    # 清理旧的执行记录，只保留最新的 max_executions 条
    _cleanup_old_executions(script_id, max_executions)
    
    logger.info(f"[execute_automation_script] 开始执行脚本 ID={script_id}")
    logger.info(f"[execute_automation_script] 脚本类型={script_type}, record_video={record_video}")
    
    try:
        # 创建执行器
        script_executor = ScriptExecutor(
            timeout_seconds=timeout_seconds,
            browser_type='chromium'
        )
        
        # 判断是否使用 pytest - 使用更可靠的方式
        use_pytest = (
            script_type == 'playwright_python' 
            and 'import pytest' in script_content 
            and 'def test_' in script_content
        )
        
        logger.info(f"[execute_automation_script] use_pytest={use_pytest}, headless={headless}, record_video={record_video}")
        logger.info(f"[execute_automation_script] 脚本内容长度: {len(script_content)} 字符")
        
        # 执行脚本
        result = script_executor.execute_script(
            script_content=script_content,
            use_pytest=use_pytest,
            headless=headless,
            record_video=record_video
        )
        
        # 添加脚本信息到结果
        result['script_id'] = script_id
        result['script_type'] = script_type
        result['target_url'] = target_url
        result['use_pytest'] = use_pytest
        result['headless'] = headless
        result['record_video'] = record_video
        
        if result['success']:
            logger.info(f"[execute_automation_script] ✅ 执行成功, 耗时: {result['execution_time']:.2f}秒")
        else:
            logger.error(f"[execute_automation_script] ❌ 执行失败: {result['error_message']}")
        
        # 清理临时目录（截图已持久化）
        script_executor.cleanup()
        
        return result
        
    except Exception as e:
        logger.exception("[execute_automation_script] ❌ 执行脚本时发生错误")
        return {
            'success': False,
            'error_message': str(e),
            'script_id': script_id,
            'script_type': script_type,
            'execution_time': 0,
            'started_at': datetime.now(),
            'completed_at': datetime.now(),
            'screenshots': [],
            'videos': []
        }