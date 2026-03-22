"""
Executor 路由 - 测试执行
"""
import logging
import asyncio
import subprocess
import tempfile
import os
from datetime import datetime
from fastapi import APIRouter, Request, BackgroundTasks
from typing import Optional
from pydantic import BaseModel, Field

from ...models.playwright_agents import PlaywrightGeneratedCode, PlaywrightExecution

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/playwright-agents/executor", tags=["Playwright Executor"])


class ExecuteRequest(BaseModel):
    """执行请求"""
    code_id: int = Field(..., description="测试代码ID")
    browser: str = Field("chromium", description="浏览器")
    headless: bool = Field(True, description="是否无头模式")
    mcp_config_id: Optional[int] = Field(None, description="MCP配置ID（可选，优先使用MCP执行）")


async def run_test_async(execution_id: int, code: str, language: str, browser: str, headless: bool, mcp_config_id: Optional[int] = None):
    """异步执行测试"""
    temp_file = None
    try:
        execution = await PlaywrightExecution.get(id=execution_id)
        execution.status = "running"
        execution.start_time = datetime.now()
        await execution.save()
        
        # 优先使用 N-Tester MCP 执行（如果提供了 mcp_config_id）
        if mcp_config_id:
            logger.info(f" 使用 N-Tester MCP 执行测试 (mcp_config_id={mcp_config_id})")
            try:
                from ...services.playwright_agents.mcp_executor_agent import MCPExecutorAgent
                from ...models.aitestrebort.project import aitestrebortMCPConfig
                
                # 获取 MCP 配置
                mcp = await aitestrebortMCPConfig.get(id=mcp_config_id)
                logger.info(f" 获取到 MCP 配置: {mcp.name} ({mcp.url})")
                
                executor = MCPExecutorAgent()
                
                # 使用数据库中的 MCP 配置
                mcp_config = {
                    "url": mcp.url,
                    "headers": mcp.headers or {},
                    "browser": browser,
                    "headless": headless
                }
                
                result = await executor.execute_with_mcp(
                    code=code,
                    mcp_config=mcp_config,
                    browser=browser,
                    headless=headless
                )
                
                # 更新执行结果
                execution.end_time = datetime.now()
                execution.duration = result.get('duration', 0)
                execution.stdout = result.get('stdout', '')
                execution.stderr = result.get('stderr', '')
                execution.exit_code = result.get('exit_code', 0)
                execution.status = result.get('status', 'failed')
                execution.error_message = result.get('error_message')
                execution.screenshots = result.get('screenshots', [])
                execution.videos = result.get('videos', [])
                await execution.save()
                
                logger.info(f" N-Tester MCP 执行完成: status={execution.status}")
                return
                
            except Exception as e:
                logger.warning(f" N-Tester MCP 执行失败，降级到 Python Playwright: {e}")
        
        # 降级到 Python Playwright 直接执行
        logger.info(f" 使用 Python Playwright 直接执行测试")
        try:
            from ...services.playwright_agents.direct_playwright_executor import DirectPlaywrightExecutor
            
            executor = DirectPlaywrightExecutor()
            
            result = await executor.execute_test(
                code=code,
                browser=browser,
                headless=headless
            )
            
            # 更新执行结果
            execution.end_time = datetime.now()
            execution.duration = result.get('duration', 0)
            execution.stdout = result.get('stdout', '')
            execution.stderr = result.get('stderr', '')
            execution.exit_code = result.get('exit_code', 0)
            execution.status = result.get('status', 'failed')
            execution.error_message = result.get('error_message')
            execution.screenshots = result.get('screenshots', [])
            execution.videos = result.get('videos', [])
            await execution.save()
            
            logger.info(f" Python Playwright 执行完成: status={execution.status}")
            return
            
        except Exception as e:
            logger.warning(f" Python Playwright 执行失败，降级到 pytest: {e}")
        
        # 最后降级到 pytest 执行
        logger.info(f" 使用 pytest 执行测试")
        
        # 为 Python 代码添加编码声明
        if language == 'python' and not code.startswith('#'):
            code = '# -*- coding: utf-8 -*-\n' + code
        
        # 创建临时文件（不自动删除）
        suffix = '.ts' if language == 'typescript' else '.py'
        fd, temp_file = tempfile.mkstemp(suffix=suffix, text=True)
        
        try:
            # 写入代码
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # 执行测试
            if language == 'python':
                # 使用虚拟环境中的 Python
                venv_python = os.path.join(os.path.dirname(__file__), '..', '..', '..', '.venv', 'Scripts', 'python.exe')
                if os.path.exists(venv_python):
                    # 使用 pytest 运行，设置环境变量控制浏览器模式
                    cmd = [venv_python, '-m', 'pytest', temp_file, '-v', '-s']
                else:
                    # 降级到系统 Python
                    cmd = ['python', '-m', 'pytest', temp_file, '-v', '-s']
                
                # 通过环境变量传递 headless 设置
                env = os.environ.copy()
                env['PLAYWRIGHT_HEADLESS'] = 'true' if headless else 'false'
                env['PLAYWRIGHT_BROWSER'] = browser
            else:
                cmd = ['npx', 'playwright', 'test', temp_file]
                if not headless:
                    cmd.append('--headed')
                env = None
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            logger.info(f"临时文件: {temp_file}")
            
            # Windows 需要使用 shell=True 来执行 npx
            process = await asyncio.create_subprocess_shell(
                ' '.join(cmd),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            stdout, stderr = await process.communicate()
            
            # 更新执行结果
            execution.end_time = datetime.now()
            execution.duration = (execution.end_time - execution.start_time).total_seconds()
            execution.stdout = stdout.decode('utf-8', errors='ignore')
            execution.stderr = stderr.decode('utf-8', errors='ignore')
            execution.exit_code = process.returncode
            execution.status = "success" if process.returncode == 0 else "failed"
            
            if process.returncode != 0:
                execution.error_message = execution.stderr
            
            await execution.save()
            
        finally:
            # 清理临时文件
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except Exception as e:
                    logger.warning(f"清理临时文件失败: {e}")
                
    except Exception as e:
        logger.error(f"执行测试失败: {str(e)}", exc_info=True)
        try:
            execution = await PlaywrightExecution.get(id=execution_id)
            execution.status = "failed"
            execution.error_message = str(e)
            execution.end_time = datetime.now()
            if execution.start_time:
                execution.duration = (execution.end_time - execution.start_time).total_seconds()
            await execution.save()
        except:
            pass


@router.post("/execute")
async def execute_test(request: Request, data: ExecuteRequest):
    """执行测试代码"""
    try:
        # 获取测试代码
        code = await PlaywrightGeneratedCode.get(id=data.code_id)
        
        # 获取用户ID（如果存在）
        creator_id = getattr(request.state, 'user', None)
        if creator_id:
            creator_id = creator_id.id
        else:
            creator_id = 1  # 默认用户ID
        
        # 创建执行记录
        execution = await PlaywrightExecution.create(
            code_id=code.id,
            browser=data.browser,
            headless=data.headless,
            status="running",  # 直接设置为 running
            creator_id=creator_id
        )
        
        try:
            # 直接执行测试（与探索功能保持一致，不使用后台任务）
            await run_test_async(
                execution.id,
                code.code,
                code.language,
                data.browser,
                data.headless,
                data.mcp_config_id
            )
            
            # 重新获取执行记录（已被 run_test_async 更新）
            execution = await PlaywrightExecution.get(id=execution.id)
            
            return request.app.success(data={
                "id": execution.id,
                "code_id": code.id,
                "status": execution.status,
                "message": "测试执行完成"
            })
            
        except Exception as e:
            # 更新执行状态为失败
            execution.status = "failed"
            execution.error_message = str(e)
            await execution.save()
            raise e
        
    except Exception as e:
        logger.error(f"测试执行失败: {str(e)}", exc_info=True)
        return request.app.fail(msg=f"执行失败: {str(e)}")


@router.get("/executions")
async def get_executions(
    request: Request,
    page: int = 1,
    page_size: int = 10,
    status: Optional[str] = None,
    code_id: Optional[int] = None
):
    """获取执行记录列表"""
    try:
        query = PlaywrightExecution.all().prefetch_related('code')
        
        if status:
            query = query.filter(status=status)
        if code_id:
            query = query.filter(code_id=code_id)
        
        # 分页
        total = await query.count()
        executions = await query.order_by('-id').offset((page - 1) * page_size).limit(page_size)
        
        items = []
        for execution in executions:
            items.append({
                "id": execution.id,
                "code_id": execution.code_id,
                "browser": execution.browser,
                "headless": execution.headless,
                "status": execution.status,
                "duration": execution.duration,
                "created_at": execution.create_time.strftime("%Y-%m-%d %H:%M:%S") if execution.create_time else None
            })
        
        return request.app.success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"获取执行记录失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


@router.get("/executions/{execution_id}")
async def get_execution_detail(request: Request, execution_id: int):
    """获取执行详情"""
    try:
        execution = await PlaywrightExecution.get(id=execution_id).prefetch_related('code')
        
        return request.app.success(data={
            "id": execution.id,
            "code_id": execution.code_id,
            "browser": execution.browser,
            "headless": execution.headless,
            "status": execution.status,
            "start_time": execution.start_time.strftime("%Y-%m-%d %H:%M:%S") if execution.start_time else None,
            "end_time": execution.end_time.strftime("%Y-%m-%d %H:%M:%S") if execution.end_time else None,
            "duration": execution.duration,
            "exit_code": execution.exit_code,
            "error_message": execution.error_message,
            "created_at": execution.create_time.strftime("%Y-%m-%d %H:%M:%S") if execution.create_time else None
        })
        
    except Exception as e:
        logger.error(f"获取执行详情失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


@router.get("/executions/{execution_id}/logs")
async def get_execution_logs(request: Request, execution_id: int):
    """获取执行日志"""
    try:
        execution = await PlaywrightExecution.get(id=execution_id)
        
        return request.app.success(data={
            "execution_id": execution.id,
            "status": execution.status,
            "stdout": execution.stdout or "",
            "stderr": execution.stderr or "",
            "start_time": execution.start_time.strftime("%Y-%m-%d %H:%M:%S") if execution.start_time else None,
            "end_time": execution.end_time.strftime("%Y-%m-%d %H:%M:%S") if execution.end_time else None,
            "duration": execution.duration,
            "exit_code": execution.exit_code
        })
        
    except Exception as e:
        logger.error(f"获取执行日志失败: {str(e)}")
        return request.app.fail(msg=f"获取失败: {str(e)}")


@router.delete("/executions/{execution_id}")
async def delete_execution(request: Request, execution_id: int):
    """删除执行记录"""
    try:
        execution = await PlaywrightExecution.get(id=execution_id)
        await execution.delete()
        
        return request.app.success(msg="删除成功")
        
    except Exception as e:
        logger.error(f"删除执行记录失败: {str(e)}")
        return request.app.fail(msg=f"删除失败: {str(e)}")


@router.get("/executions/{execution_id}/steps")
async def get_execution_steps(request: Request, execution_id: int):
    """获取执行步骤详情（包含截图）"""
    try:
        execution = await PlaywrightExecution.get(id=execution_id)
        
        # 从 screenshots 字段获取步骤截图
        steps = execution.screenshots or []
        
        logger.info(f" 获取执行步骤: execution_id={execution_id}")
        logger.info(f"  screenshots 字段类型: {type(steps)}")
        logger.info(f"  步骤数量: {len(steps)}")
        
        if steps and len(steps) > 0:
            first_step = steps[0]
            logger.info(f"  第一个步骤类型: {type(first_step)}")
            logger.info(f"  第一个步骤内容: {first_step}")
            
            if isinstance(first_step, dict):
                for key in ['screenshot_before', 'screenshot_after']:
                    if key in first_step:
                        value = first_step[key]
                        logger.info(f"    {key}: type={type(value)}, length={len(value) if value else 0}")
                        if value:
                            logger.info(f"      前50字符: {value[:50]}")
        
        return request.app.success(data={
            "execution_id": execution.id,
            "status": execution.status,
            "steps": steps,
            "total_steps": len(steps)
        })
        
    except Exception as e:
        logger.error(f"获取执行步骤失败: {str(e)}", exc_info=True)
        return request.app.fail(msg=f"获取失败: {str(e)}")


@router.get("/test-mcp-connection")
async def test_mcp_connection(request: Request):
    """测试 MCP 连接"""
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        logger.info(" 测试 MCP 连接")
        
        # 使用与探索功能相同的配置
        client_config = {
            "n-tester": {
                "url": "http://127.0.0.1:8006",
                "transport": "streamable-http"
            }
        }
        
        logger.info(f" 连接配置: {client_config}")
        
        mcp_client = MultiServerMCPClient(client_config)
        
        logger.info(" 创建 session...")
        async with mcp_client.session("n-tester") as session:
            logger.info(" Session 创建成功")
            
            # 测试调用工具列表
            logger.info(" 获取工具列表...")
            tools = await session.list_tools()
            logger.info(f" 工具列表获取成功，共 {len(tools)} 个工具")
            
            tool_list = [{"name": tool.name, "description": tool.description} for tool in tools]
            
            return request.app.success(data={
                "status": "success",
                "message": "MCP 连接测试成功",
                "tools_count": len(tools),
                "tools": tool_list
            })
            
    except Exception as e:
        logger.error(f" MCP 连接测试失败: {e}", exc_info=True)
        return request.app.fail(msg=f"MCP 连接测试失败: {str(e)}")
