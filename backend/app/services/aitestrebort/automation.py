"""
aitestrebort 自动化脚本管理服务
"""
from typing import Optional
from datetime import datetime
from fastapi import Request, Depends, Query
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from app.models.aitestrebort import (
    aitestrebortProject, aitestrebortAutomationScript, aitestrebortScriptExecution,
    aitestrebortTestCase, aitestrebortProjectMember
)
from app.schemas.aitestrebort.automation import (
    aitestrebortAutomationScriptCreateSchema, aitestrebortAutomationScriptUpdateSchema,
    aitestrebortScriptExecutionCreateSchema, aitestrebortAutomationScriptQueryForm
)


async def test_simple(request: Request):
    """简单测试接口"""
    return request.app.get_success(data={"message": "aitestrebort 自动化脚本 API 工作正常"})


async def get_automation_scripts(
    request: Request,
    project_id: int,
    form: aitestrebortAutomationScriptQueryForm = Depends()
):
    """获取自动化脚本列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 查询该项目下的所有自动化脚本
        query = aitestrebortAutomationScript.filter(project_id=project_id)
        
        # 测试用例过滤
        if form.test_case_id:
            query = query.filter(test_case_id=form.test_case_id)
        
        # 脚本类型过滤
        if form.script_type:
            query = query.filter(script_type=form.script_type)
        
        # 状态过滤
        if form.status:
            query = query.filter(status=form.status)
        
        # 搜索过滤
        if form.search:
            query = query.filter(
                Q(name__icontains=form.search) |
                Q(description__icontains=form.search)
            )
        
        # 分页
        total = await query.count()
        
        # 使用page而不是page_no，与前端保持一致
        page = getattr(form, 'page', None) or getattr(form, 'page_no', None) or 1
        page_size = getattr(form, 'page_size', None) or 20
        
        if page and page_size:
            scripts = await query.offset((page - 1) * page_size).limit(page_size).order_by('-create_time').all()
        else:
            scripts = await query.order_by('-create_time').all()
        
        # 转换为响应格式
        script_list = []
        for script in scripts:
            # 获取关联的测试用例和模块信息
            test_case_name = None
            module_name = None
            if script.test_case_id:
                try:
                    test_case = await aitestrebortTestCase.get(id=script.test_case_id).prefetch_related('module')
                    test_case_name = test_case.name
                    if test_case.module:
                        module_name = test_case.module.name
                except:
                    pass
            
            script_data = {
                "id": script.id,
                "name": script.name,
                "description": getattr(script, 'description', ''),
                "script_type": getattr(script, 'script_type', 'ui'),  # 映射到前端期望的类型
                "framework": getattr(script, 'framework', 'selenium'),  # 前端期望的framework字段
                "language": getattr(script, 'language', 'python'),     # 前端期望的language字段
                "script_content": getattr(script, 'script_content', ''),  # 添加script_content字段
                "source": getattr(script, 'source', 'ai_generated'),
                "status": getattr(script, 'status', 'active'),
                "version": getattr(script, 'version', 1),
                "test_case_id": getattr(script, 'test_case_id', None),
                "test_case_name": test_case_name,
                "module_name": module_name,
                "target_url": getattr(script, 'target_url', ''),
                "timeout_seconds": getattr(script, 'timeout_seconds', 30),
                "creator_id": getattr(script, 'creator_id', None),  # 添加creator_id字段
                "created_at": script.create_time.isoformat() if script.create_time else None,
                "updated_at": script.update_time.isoformat() if script.update_time else None,
                "latest_status": None  # 暂时不查询执行状态
            }
            script_list.append(script_data)
        
        return request.app.get_success(data={
            "items": script_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取自动化脚本失败: {str(e)}")


async def create_automation_script(request: Request, project_id: int, script_data: aitestrebortAutomationScriptCreateSchema):
    """创建自动化脚本"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 检查测试用例是否存在
        test_case = None
        if script_data.test_case_id:
            test_case = await aitestrebortTestCase.get(id=script_data.test_case_id, project=project)
        
        script = await aitestrebortAutomationScript.create(
            test_case=test_case,
            name=script_data.name,
            description=script_data.description,
            script_type=script_data.script_type,
            script_content=script_data.script_content,
            source=getattr(script_data, 'source', 'manual'),
            status='draft',
            target_url=getattr(script_data, 'target_url', ''),
            timeout_seconds=getattr(script_data, 'timeout_seconds', 30),
            headless=getattr(script_data, 'headless', True),
            version=1,
            framework='playwright',  # 添加必需的framework字段
            language='python',       # 添加必需的language字段
            creator_id=request.state.user.id,  # 修正字段名
            project_id=project_id    # 添加必需的project_id字段
        )
        
        return request.app.post_success(data={
            "id": script.id,
            "name": script.name,
            "status": script.status,
            "created_at": script.create_time
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试用例不存在")
    except Exception as e:
        return request.app.error(msg=f"创建自动化脚本失败: {str(e)}")


async def get_automation_script_detail(request: Request, project_id: int, script_id: int):
    """获取自动化脚本详情"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        script = await aitestrebortAutomationScript.get(
            id=script_id, project_id=project_id
        ).prefetch_related('test_case')
        
        # 获取执行历史
        executions = await aitestrebortScriptExecution.filter(
            script=script
        ).order_by('-create_time').limit(10).all()
        
        execution_list = []
        for execution in executions:
            execution_list.append({
                "id": execution.id,
                "status": execution.status,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "execution_time": execution.execution_time,
                "error_message": execution.error_message,
                "screenshots": execution.screenshots,
                "videos": execution.videos,
                "created_at": execution.create_time
            })
        
        script_data = {
            "id": script.id,
            "name": script.name,
            "description": getattr(script, 'description', ''),
            "script_type": getattr(script, 'script_type', 'playwright_python'),
            "script_content": getattr(script, 'script_content', ''),
            "source": getattr(script, 'source', 'ai_generated'),
            "status": getattr(script, 'status', 'active'),
            "version": getattr(script, 'version', 1),  # 安全获取version字段，默认为1
            "test_case_id": getattr(script, 'test_case_id', None),
            "test_case_name": script.test_case.name if hasattr(script, 'test_case') and script.test_case else None,
            "target_url": getattr(script, 'target_url', ''),
            "timeout_seconds": getattr(script, 'timeout_seconds', 30),
            "created_at": script.create_time,
            "updated_at": script.update_time,
            "executions": execution_list
        }
        
        return request.app.get_success(data=script_data)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或自动化脚本不存在")
    except Exception as e:
        return request.app.error(msg=f"获取自动化脚本详情失败: {str(e)}")


async def update_automation_script(request: Request, project_id: int, script_id: int, script_data: aitestrebortAutomationScriptUpdateSchema):
    """更新自动化脚本"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        script = await aitestrebortAutomationScript.get(
            id=script_id, project_id=project_id
        )
        
        # 更新字段
        if script_data.name is not None:
            script.name = script_data.name
        if script_data.description is not None:
            script.description = script_data.description
        if script_data.script_content is not None:
            script.script_content = script_data.script_content
        if script_data.script_type is not None:
            script.script_type = script_data.script_type
        if script_data.source is not None:
            script.source = script_data.source
        if script_data.status is not None:
            script.status = script_data.status
        if script_data.target_url is not None:
            script.target_url = script_data.target_url
        if script_data.timeout_seconds is not None:
            script.timeout_seconds = script_data.timeout_seconds
        
        await script.save()
        
        return request.app.put_success(data={
            "id": script.id,
            "name": script.name,
            "status": script.status,
            "updated_at": script.update_time
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目或自动化脚本不存在")
    except Exception as e:
        return request.app.error(msg=f"更新自动化脚本失败: {str(e)}")


async def delete_automation_script(request: Request, project_id: int, script_id: int):
    """删除自动化脚本"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        script = await aitestrebortAutomationScript.get(
            id=script_id, project_id=project_id
        )
        
        await script.delete()
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目或自动化脚本不存在")
    except Exception as e:
        return request.app.error(msg=f"删除自动化脚本失败: {str(e)}")


async def execute_automation_script(request: Request, project_id: int, script_id: int, execution_data: aitestrebortScriptExecutionCreateSchema):
    """执行自动化脚本"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        script = await aitestrebortAutomationScript.get(
            id=script_id, project_id=project_id
        )
        
        # 检查脚本状态
        if script.status != 'active':
            return request.app.fail(msg="只能执行已激活的脚本")
        
        # 安全检查：只允许执行 AI 生成或录制的脚本
        if script.source not in ('ai_generated', 'recorded'):
            return request.app.fail(msg="只能执行 AI 生成或录制的脚本，手动编写的脚本需要先审核")
        
        # 创建执行记录
        execution = await aitestrebortScriptExecution.create(
            script=script,
            executor_id=request.state.user.id,
            status='running',
            started_at=datetime.now(),
            browser_type=execution_data.browser_type or 'chromium',
            viewport=execution_data.viewport or {"width": 1280, "height": 720}
        )
        
        try:
            # 使用脚本执行器执行脚本
            from .script_executor import execute_automation_script as exec_script
            
            result = await exec_script(
                script_id=str(script.id),
                script_content=script.script_content,
                script_type=script.script_type,
                target_url=script.target_url or '',
                timeout_seconds=script.timeout_seconds,
                headless=execution_data.headless if execution_data.headless is not None else script.headless,
                record_video=execution_data.record_video or False
            )
            
            # 更新执行记录
            execution.completed_at = result.get('completed_at') or datetime.now()
            execution.execution_time = result.get('execution_time', 0)
            execution.output = result.get('output', '')
            execution.screenshots = result.get('screenshots', [])
            execution.videos = result.get('videos', [])
            
            if result.get('success'):
                execution.status = 'pass'
            else:
                execution.status = 'fail'
                execution.error_message = result.get('error_message', '')
                execution.stack_trace = result.get('stack_trace', '')
            
            await execution.save()
            
            return request.app.post_success(data={
                "execution_id": execution.id,
                "status": execution.status,
                "success": result.get('success', False),
                "execution_time": execution.execution_time,
                "screenshots_count": len(execution.screenshots),
                "videos_count": len(execution.videos),
                "message": "脚本执行完成" if result.get('success') else f"脚本执行失败: {execution.error_message}"
            })
            
        except Exception as e:
            # 更新执行记录为错误状态
            execution.status = 'error'
            execution.error_message = str(e)
            execution.completed_at = datetime.now()
            await execution.save()
            
            return request.app.error(msg=f"脚本执行异常: {str(e)}")
        
    except DoesNotExist:
        return request.app.fail(msg="项目或自动化脚本不存在")
    except Exception as e:
        return request.app.error(msg=f"执行自动化脚本失败: {str(e)}")


async def get_script_executions(request: Request, project_id: int, script_id: int):
    """获取脚本执行历史"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        script = await aitestrebortAutomationScript.get(
            id=script_id, project_id=project_id
        )
        
        executions = await aitestrebortScriptExecution.filter(
            script=script
        ).order_by('-create_time').all()
        
        execution_list = []
        for execution in executions:
            execution_list.append({
                "id": execution.id,
                "status": execution.status,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "execution_time": execution.execution_time,
                "output": execution.output,
                "error_message": execution.error_message,
                "stack_trace": execution.stack_trace,
                "screenshots": execution.screenshots,
                "videos": execution.videos,
                "browser_type": execution.browser_type,
                "viewport": execution.viewport,
                "executor_detail": {
                    "id": execution.executor_id,
                    "username": "用户"  # 这里应该关联用户信息
                },
                "created_at": execution.create_time
            })
        
        return request.app.get_success(data=execution_list)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或自动化脚本不存在")
    except Exception as e:
        return request.app.error(msg=f"获取执行历史失败: {str(e)}")


async def get_execution_detail(request: Request, project_id: int, script_id: int, execution_id: int):
    """获取执行详情"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        script = await aitestrebortAutomationScript.get(
            id=script_id, project_id=project_id
        )
        execution = await aitestrebortScriptExecution.get(id=execution_id, script=script)
        
        execution_data = {
            "id": execution.id,
            "script_id": execution.script_id,
            "status": execution.status,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "execution_time": execution.execution_time,
            "output": execution.output,
            "error_message": execution.error_message,
            "stack_trace": execution.stack_trace,
            "screenshots": execution.screenshots,
            "videos": execution.videos,
            "browser_type": execution.browser_type,
            "viewport": execution.viewport,
            "executor_detail": {
                "id": execution.executor_id,
                "username": "用户"  # 这里应该关联用户信息
            },
            "created_at": execution.create_time
        }
        
        return request.app.get_success(data=execution_data)
        
    except DoesNotExist:
        return request.app.fail(msg="项目、脚本或执行记录不存在")
    except Exception as e:
        return request.app.error(msg=f"获取执行详情失败: {str(e)}")