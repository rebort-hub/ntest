"""
aitestrebort 测试用例管理服务
基于原始 aitestrebort 架构的完整功能实现
"""
from typing import Optional, List, Dict, Any
from fastapi import Request, Depends, Query, UploadFile, File
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise import transactions

from app.models.aitestrebort import (
    aitestrebortProject, aitestrebortTestCase, aitestrebortTestCaseStep, aitestrebortTestCaseModule,
    aitestrebortTestCaseScreenshot, aitestrebortTestSuite, aitestrebortTestExecution,
    aitestrebortTestCaseResult, aitestrebortProjectMember
)
from app.schemas.aitestrebort.testcase import (
    aitestrebortTestCaseCreateSchema, aitestrebortTestCaseUpdateSchema, aitestrebortTestCaseQueryForm,
    aitestrebortTestCaseStepCreateSchema, aitestrebortTestCaseModuleCreateSchema,
    aitestrebortTestSuiteCreateSchema, aitestrebortTestSuiteUpdateSchema
)
from utils.logs.log import logger


async def test_simple(request: Request):
    """简单测试接口"""
    return request.app.get_success(data={"message": "aitestrebort 测试用例管理 API 工作正常"})


# 测试用例模块管理
async def get_testcase_modules(request: Request, project_id: int):
    """获取测试用例模块树结构"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取根模块（没有父模块的模块）
        root_modules = await aitestrebortTestCaseModule.filter(
            project=project, parent_id=None
        ).order_by('name').all()
        
        async def build_module_tree(modules):
            """递归构建模块树"""
            result = []
            for module in modules:
                # 获取子模块
                children = await aitestrebortTestCaseModule.filter(
                    parent=module
                ).order_by('name').all()
                
                # 获取模块下的测试用例数量
                testcase_count = await aitestrebortTestCase.filter(module=module).count()
                
                module_data = {
                    "id": module.id,
                    "name": module.name,
                    "description": module.description,
                    "parent_id": module.parent_id,
                    "level": module.level,
                    "testcase_count": testcase_count,
                    "creator_id": module.creator_id,
                    "create_time": module.create_time,
                    "children": await build_module_tree(children) if children else []
                }
                result.append(module_data)
            return result
        
        module_tree = await build_module_tree(root_modules)
        return request.app.get_success(data=module_tree)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        logger.error(f"Error in get_testcase_modules: {str(e)}", exc_info=True)
        return request.app.error(msg=f"获取模块列表失败: {str(e)}")


async def create_testcase_module(request: Request, project_id: int, module_data: aitestrebortTestCaseModuleCreateSchema):
    """创建测试用例模块"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 验证父模块
        parent_module = None
        level = 1
        if module_data.parent_id:
            parent_module = await aitestrebortTestCaseModule.get(
                id=module_data.parent_id, project=project
            )
            level = parent_module.level + 1
            
            # 检查级别限制（最多5级）
            if level > 5:
                return request.app.fail(msg="模块级别不能超过5级")
        
        # 检查同级模块名称是否重复
        existing_module = await aitestrebortTestCaseModule.filter(
            project=project,
            parent_id=module_data.parent_id,
            name=module_data.name
        ).first()
        if existing_module:
            return request.app.fail(msg="同级模块名称已存在")
        
        module = await aitestrebortTestCaseModule.create(
            project=project,
            name=module_data.name,
            description=module_data.description,
            parent=parent_module,
            level=level,
            creator_id=request.state.user.id
        )
        
        module_result = {
            "id": module.id,
            "name": module.name,
            "description": module.description,
            "parent_id": module.parent_id,
            "level": module.level,
            "creator_id": module.creator_id,
            "create_time": module.create_time,
            "testcase_count": 0
        }
        
        return request.app.post_success(data=module_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或父模块不存在")
    except Exception as e:
        return request.app.error(msg=f"创建模块失败: {str(e)}")


async def update_testcase_module(request: Request, project_id: int, module_id: int, module_data: aitestrebortTestCaseModuleCreateSchema):
    """更新测试用例模块"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        module = await aitestrebortTestCaseModule.get(id=module_id, project=project)
        
        # 检查同级模块名称是否重复
        if module_data.name != module.name:
            existing_module = await aitestrebortTestCaseModule.filter(
                project=project,
                parent_id=module.parent_id,
                name=module_data.name
            ).exclude(id=module_id).first()
            if existing_module:
                return request.app.fail(msg="同级模块名称已存在")
        
        module.name = module_data.name
        if module_data.description is not None:
            module.description = module_data.description
        await module.save()
        
        module_result = {
            "id": module.id,
            "name": module.name,
            "description": module.description,
            "parent_id": module.parent_id,
            "level": module.level,
            "creator_id": module.creator_id,
            "create_time": module.create_time
        }
        
        return request.app.put_success(data=module_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或模块不存在")
    except Exception as e:
        return request.app.error(msg=f"更新模块失败: {str(e)}")


async def delete_testcase_module(request: Request, project_id: int, module_id: int):
    """删除测试用例模块"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        module = await aitestrebortTestCaseModule.get(id=module_id, project=project)
        
        # 检查是否有子模块
        if await aitestrebortTestCaseModule.filter(parent=module).exists():
            return request.app.fail(msg="请先删除子模块")
        
        # 检查是否有测试用例
        if await aitestrebortTestCase.filter(module=module).exists():
            return request.app.fail(msg="请先删除模块下的测试用例")
        
        await module.delete()
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目或模块不存在")
    except Exception as e:
        return request.app.error(msg=f"删除模块失败: {str(e)}")


# 测试用例管理
async def get_testcases(request: Request, project_id: int, form: aitestrebortTestCaseQueryForm = Depends()):
    """获取测试用例列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        query = aitestrebortTestCase.filter(project=project)
        
        # 模块过滤
        if form.module_id:
            query = query.filter(module_id=form.module_id)
        
        # 等级过滤
        if form.level:
            query = query.filter(level=form.level)
        
        # 创建人过滤
        if form.creator_id:
            query = query.filter(creator_id=form.creator_id)
        
        # 搜索过滤
        if form.search:
            query = query.filter(
                Q(name__icontains=form.search) |
                Q(precondition__icontains=form.search) |
                Q(notes__icontains=form.search)
            )
        
        # 分页
        total = await query.count()
        
        if form.page_no and form.page_size:
            testcases = await query.offset((form.page_no - 1) * form.page_size).limit(form.page_size).order_by('-create_time').all()
        else:
            testcases = await query.order_by('-create_time').all()
        
        testcase_list = []
        for testcase in testcases:
            # 获取模块名称
            module_name = ""
            if testcase.module_id:
                module = await aitestrebortTestCaseModule.get(id=testcase.module_id)
                module_name = module.name
            
            # 获取步骤数量
            step_count = await aitestrebortTestCaseStep.filter(test_case=testcase).count()
            
            testcase_data = {
                "id": testcase.id,
                "name": testcase.name,
                "description": testcase.description,
                "precondition": testcase.precondition,
                "level": testcase.level,
                "module_id": testcase.module_id,
                "module_name": module_name,
                "creator_id": testcase.creator_id,
                "create_time": testcase.create_time,
                "update_time": testcase.update_time,
                "notes": testcase.notes,
                "step_count": step_count
            }
            testcase_list.append(testcase_data)
        
        return request.app.get_success(data={
            "items": testcase_list,
            "total": total,
            "page": form.page_no or 1,
            "page_size": form.page_size or 20
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取测试用例列表失败: {str(e)}")


async def create_testcase(request: Request, project_id: int, testcase_data: aitestrebortTestCaseCreateSchema):
    """创建测试用例"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 验证模块是否存在（如果提供了module_id）
        module = None
        if testcase_data.module_id:
            module = await aitestrebortTestCaseModule.get(
                id=testcase_data.module_id, project=project
            )
        
        async with transactions.in_transaction():
            # 创建测试用例
            testcase = await aitestrebortTestCase.create(
                project=project,
                module=module,
                name=testcase_data.name,
                description=testcase_data.description,
                precondition=testcase_data.precondition,
                level=testcase_data.level,
                notes=testcase_data.notes,
                creator_id=request.state.user.id
            )
        
        # 获取创建的测试用例详情
        testcase_result = {
            "id": testcase.id,
            "name": testcase.name,
            "description": testcase.description,
            "precondition": testcase.precondition,
            "level": testcase.level,
            "module_id": testcase.module_id,
            "creator_id": testcase.creator_id,
            "create_time": testcase.create_time,
            "update_time": testcase.update_time,
            "notes": testcase.notes
        }
        
        return request.app.post_success(data=testcase_result)
        
    except DoesNotExist:
        logger.error(f"Project {project_id} or module not found")
        return request.app.fail(msg="项目或模块不存在")
    except Exception as e:
        logger.error(f"Error in create_testcase: {str(e)}", exc_info=True)
        return request.app.error(msg=f"创建测试用例失败: {str(e)}")


async def get_testcase_detail(request: Request, project_id: int, testcase_id: int):
    """获取测试用例详情"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        
        # 获取测试步骤
        steps = await aitestrebortTestCaseStep.filter(test_case=testcase).order_by('step_number').all()
        step_list = []
        for step in steps:
            step_data = {
                "id": step.id,
                "step_number": step.step_number,
                "description": step.description,
                "expected_result": step.expected_result,
                "creator_id": step.creator_id,
                "create_time": step.create_time
            }
            step_list.append(step_data)
        
        # 获取截图
        screenshots = await aitestrebortTestCaseScreenshot.filter(test_case=testcase).order_by('step_number', 'create_time').all()
        screenshot_list = []
        for screenshot in screenshots:
            screenshot_data = {
                "id": screenshot.id,
                "title": screenshot.title,
                "description": screenshot.description,
                "step_number": screenshot.step_number,
                "screenshot_url": screenshot.screenshot.url if screenshot.screenshot else None,
                "page_url": screenshot.page_url,
                "create_time": screenshot.create_time
            }
            screenshot_list.append(screenshot_data)
        
        # 获取模块名称
        module_name = ""
        if testcase.module_id:
            module = await aitestrebortTestCaseModule.get(id=testcase.module_id)
            module_name = module.name
        
        testcase_data = {
            "id": testcase.id,
            "name": testcase.name,
            "description": testcase.description,
            "precondition": testcase.precondition,
            "level": testcase.level,
            "module_id": testcase.module_id,
            "module_name": module_name,
            "creator_id": testcase.creator_id,
            "create_time": testcase.create_time,
            "update_time": testcase.update_time,
            "notes": testcase.notes,
            "steps": step_list,
            "screenshots": screenshot_list
        }
        
        return request.app.get_success(data=testcase_data)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试用例不存在")
    except Exception as e:
        return request.app.error(msg=f"获取测试用例详情失败: {str(e)}")


async def update_testcase(request: Request, project_id: int, testcase_id: int, testcase_data: aitestrebortTestCaseUpdateSchema):
    """更新测试用例"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        
        # 更新字段
        if testcase_data.name is not None:
            testcase.name = testcase_data.name
        if testcase_data.description is not None:
            testcase.description = testcase_data.description
        if testcase_data.precondition is not None:
            testcase.precondition = testcase_data.precondition
        if testcase_data.level is not None:
            testcase.level = testcase_data.level
        if testcase_data.notes is not None:
            testcase.notes = testcase_data.notes
        if testcase_data.module_id is not None:
            # 验证模块是否存在
            module = await aitestrebortTestCaseModule.get(
                id=testcase_data.module_id, project=project
            )
            testcase.module = module
        
        await testcase.save()
        
        testcase_result = {
            "id": testcase.id,
            "name": testcase.name,
            "description": testcase.description,
            "precondition": testcase.precondition,
            "level": testcase.level,
            "module_id": testcase.module_id,
            "creator_id": testcase.creator_id,
            "create_time": testcase.create_time,
            "update_time": testcase.update_time,
            "notes": testcase.notes
        }
        
        return request.app.put_success(data=testcase_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目、测试用例或模块不存在")
    except Exception as e:
        return request.app.error(msg=f"更新测试用例失败: {str(e)}")


async def delete_testcase(request: Request, project_id: int, testcase_id: int):
    """删除测试用例"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        await testcase.delete()
        
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试用例不存在")
    except Exception as e:
        return request.app.error(msg=f"删除测试用例失败: {str(e)}")


async def copy_testcase(request: Request, project_id: int, testcase_id: int):
    """复制测试用例"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        original_testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        
        # 获取模块对象
        module = None
        if original_testcase.module_id:
            module = await aitestrebortTestCaseModule.get(id=original_testcase.module_id)
        
        async with transactions.in_transaction():
            # 创建测试用例副本
            new_testcase = await aitestrebortTestCase.create(
                project=project,
                module=module,
                name=f"{original_testcase.name} - 副本",
                description=original_testcase.description,
                precondition=original_testcase.precondition,
                level=original_testcase.level,
                notes=original_testcase.notes,
                creator_id=request.state.user.id
            )
            
            # 复制测试步骤
            original_steps = await aitestrebortTestCaseStep.filter(test_case=original_testcase).order_by('step_number').all()
            for step in original_steps:
                await aitestrebortTestCaseStep.create(
                    test_case=new_testcase,
                    step_number=step.step_number,
                    description=step.description,
                    expected_result=step.expected_result,
                    creator_id=request.state.user.id
                )
        
        testcase_result = {
            "id": new_testcase.id,
            "name": new_testcase.name,
            "description": new_testcase.description,
            "precondition": new_testcase.precondition,
            "level": new_testcase.level,
            "module_id": new_testcase.module_id,
            "creator_id": new_testcase.creator_id,
            "create_time": new_testcase.create_time,
            "update_time": new_testcase.update_time,
            "notes": new_testcase.notes
        }
        
        return request.app.post_success(data=testcase_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试用例不存在")
    except Exception as e:
        return request.app.error(msg=f"复制测试用例失败: {str(e)}")


# 测试用例步骤管理
async def get_testcase_steps(request: Request, project_id: int, testcase_id: int):
    """获取测试用例步骤列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        steps = await aitestrebortTestCaseStep.filter(test_case=testcase).order_by('step_number').all()
        
        step_list = []
        for step in steps:
            step_data = {
                "id": step.id,
                "step_number": step.step_number,
                "description": step.description,
                "expected_result": step.expected_result,
                "creator_id": step.creator_id,
                "create_time": step.create_time,
                "update_time": step.update_time
            }
            step_list.append(step_data)
        
        return request.app.get_success(data=step_list)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试用例不存在")
    except Exception as e:
        return request.app.error(msg=f"获取测试步骤失败: {str(e)}")


async def create_testcase_step(request: Request, project_id: int, testcase_id: int, step_data: aitestrebortTestCaseStepCreateSchema):
    """创建测试用例步骤"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        
        # 检查步骤编号是否已存在
        if await aitestrebortTestCaseStep.filter(
            test_case=testcase, step_number=step_data.step_number
        ).exists():
            return request.app.fail(msg="步骤编号已存在")
        
        step = await aitestrebortTestCaseStep.create(
            test_case=testcase,
            step_number=step_data.step_number,
            description=step_data.description,
            expected_result=step_data.expected_result,
            creator_id=request.state.user.id
        )
        
        step_result = {
            "id": step.id,
            "step_number": step.step_number,
            "description": step.description,
            "expected_result": step.expected_result,
            "creator_id": step.creator_id,
            "create_time": step.create_time,
            "update_time": step.update_time
        }
        
        return request.app.post_success(data=step_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试用例不存在")
    except Exception as e:
        return request.app.error(msg=f"创建测试步骤失败: {str(e)}")


async def update_testcase_step(request: Request, project_id: int, testcase_id: int, step_id: int, step_data: aitestrebortTestCaseStepCreateSchema):
    """更新测试用例步骤"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        step = await aitestrebortTestCaseStep.get(id=step_id, test_case=testcase)
        
        # 检查步骤编号是否已存在（排除当前步骤）
        if step_data.step_number != step.step_number:
            if await aitestrebortTestCaseStep.filter(
                test_case=testcase, step_number=step_data.step_number
            ).exclude(id=step_id).exists():
                return request.app.fail(msg="步骤编号已存在")
        
        step.step_number = step_data.step_number
        step.description = step_data.description
        step.expected_result = step_data.expected_result
        await step.save()
        
        step_result = {
            "id": step.id,
            "step_number": step.step_number,
            "description": step.description,
            "expected_result": step.expected_result,
            "creator_id": step.creator_id,
            "create_time": step.create_time,
            "update_time": step.update_time
        }
        
        return request.app.put_success(data=step_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目、测试用例或步骤不存在")
    except Exception as e:
        return request.app.error(msg=f"更新测试步骤失败: {str(e)}")


async def delete_testcase_step(request: Request, project_id: int, testcase_id: int, step_id: int):
    """删除测试用例步骤"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        step = await aitestrebortTestCaseStep.get(id=step_id, test_case=testcase)
        
        await step.delete()
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目、测试用例或步骤不存在")
    except Exception as e:
        return request.app.error(msg=f"删除测试步骤失败: {str(e)}")


# 测试用例截图管理
async def get_testcase_screenshots(request: Request, project_id: int, testcase_id: int):
    """获取测试用例截图列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        screenshots = await aitestrebortTestCaseScreenshot.filter(test_case=testcase).order_by('step_number', 'create_time').all()
        
        screenshot_list = []
        for screenshot in screenshots:
            screenshot_data = {
                "id": screenshot.id,
                "title": screenshot.title,
                "description": screenshot.description,
                "step_number": screenshot.step_number,
                "screenshot_url": screenshot.screenshot.url if screenshot.screenshot else None,
                "page_url": screenshot.page_url,
                "mcp_session_id": screenshot.mcp_session_id,
                "uploader_id": screenshot.uploader_id,
                "create_time": screenshot.create_time
            }
            screenshot_list.append(screenshot_data)
        
        return request.app.get_success(data=screenshot_list)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试用例不存在")
    except Exception as e:
        return request.app.error(msg=f"获取测试截图失败: {str(e)}")


async def upload_testcase_screenshot(
    request: Request, 
    project_id: int, 
    testcase_id: int,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    description: Optional[str] = None,
    step_number: Optional[int] = None,
    page_url: Optional[str] = None
):
    """上传测试用例截图"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            return request.app.fail(msg="只能上传图片文件")
        
        # 保存文件（这里需要实现文件保存逻辑）
        # 暂时使用文件名作为路径
        file_path = f"aitestrebort/screenshots/{project_id}/{testcase_id}/{file.filename}"
        
        screenshot = await aitestrebortTestCaseScreenshot.create(
            test_case=testcase,
            screenshot=file_path,
            title=title,
            description=description,
            step_number=step_number,
            page_url=page_url,
            uploader_id=request.state.user.id
        )
        
        screenshot_result = {
            "id": screenshot.id,
            "title": screenshot.title,
            "description": screenshot.description,
            "step_number": screenshot.step_number,
            "screenshot_url": screenshot.screenshot,
            "page_url": screenshot.page_url,
            "uploader_id": screenshot.uploader_id,
            "create_time": screenshot.create_time
        }
        
        return request.app.post_success(data=screenshot_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试用例不存在")
    except Exception as e:
        return request.app.error(msg=f"上传截图失败: {str(e)}")


async def delete_testcase_screenshot(request: Request, project_id: int, testcase_id: int, screenshot_id: int):
    """删除测试用例截图"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        testcase = await aitestrebortTestCase.get(id=testcase_id, project=project)
        screenshot = await aitestrebortTestCaseScreenshot.get(id=screenshot_id, test_case=testcase)
        
        await screenshot.delete()
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目、测试用例或截图不存在")
    except Exception as e:
        return request.app.error(msg=f"删除截图失败: {str(e)}")


# 测试套件管理
async def get_test_suites(request: Request, project_id: int):
    """获取测试套件列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        suites = await aitestrebortTestSuite.filter(project=project).order_by('-create_time').all()
        
        suite_list = []
        for suite in suites:
            # 获取测试用例数量
            testcase_count = await suite.testcases.all().count()
            
            suite_data = {
                "id": suite.id,
                "name": suite.name,
                "description": suite.description,
                "testcase_count": testcase_count,
                "max_concurrent_tasks": suite.max_concurrent_tasks,
                "creator_id": suite.creator_id,
                "create_time": suite.create_time,
                "update_time": suite.update_time
            }
            suite_list.append(suite_data)
        
        return request.app.get_success(data=suite_list)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取测试套件列表失败: {str(e)}")


async def create_test_suite(request: Request, project_id: int, suite_data: aitestrebortTestSuiteCreateSchema):
    """创建测试套件"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 检查套件名称是否已存在
        if await aitestrebortTestSuite.filter(project=project, name=suite_data.name).exists():
            return request.app.fail(msg="测试套件名称已存在")
        
        async with transactions.in_transaction():
            suite = await aitestrebortTestSuite.create(
                project=project,
                name=suite_data.name,
                description=suite_data.description,
                max_concurrent_tasks=suite_data.max_concurrent_tasks or 1,
                creator_id=request.state.user.id
            )
            
            # 添加测试用例
            if suite_data.testcase_ids:
                testcases = await aitestrebortTestCase.filter(
                    id__in=suite_data.testcase_ids, project=project
                ).all()
                await suite.testcases.add(*testcases)
        
        suite_result = {
            "id": suite.id,
            "name": suite.name,
            "description": suite.description,
            "testcase_count": len(suite_data.testcase_ids) if suite_data.testcase_ids else 0,
            "max_concurrent_tasks": suite.max_concurrent_tasks,
            "creator_id": suite.creator_id,
            "create_time": suite.create_time,
            "update_time": suite.update_time
        }
        
        return request.app.post_success(data=suite_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"创建测试套件失败: {str(e)}")


async def get_test_suite_detail(request: Request, project_id: int, suite_id: int):
    """获取测试套件详情"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        suite = await aitestrebortTestSuite.get(id=suite_id, project=project)
        
        # 获取测试用例列表
        testcases = await suite.testcases.all()
        testcase_list = []
        for testcase in testcases:
            testcase_data = {
                "id": testcase.id,
                "name": testcase.name,
                "level": testcase.level,
                "module_id": testcase.module_id
            }
            testcase_list.append(testcase_data)
        
        suite_data = {
            "id": suite.id,
            "name": suite.name,
            "description": suite.description,
            "testcases": testcase_list,
            "testcase_count": len(testcase_list),
            "max_concurrent_tasks": suite.max_concurrent_tasks,
            "creator_id": suite.creator_id,
            "create_time": suite.create_time,
            "update_time": suite.update_time
        }
        
        return request.app.get_success(data=suite_data)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试套件不存在")
    except Exception as e:
        return request.app.error(msg=f"获取测试套件详情失败: {str(e)}")


async def update_test_suite(request: Request, project_id: int, suite_id: int, suite_data: aitestrebortTestSuiteUpdateSchema):
    """更新测试套件"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        suite = await aitestrebortTestSuite.get(id=suite_id, project=project)
        
        # 更新字段
        if suite_data.name is not None:
            # 检查名称是否已存在
            if await aitestrebortTestSuite.filter(
                project=project, name=suite_data.name
            ).exclude(id=suite_id).exists():
                return request.app.fail(msg="测试套件名称已存在")
            suite.name = suite_data.name
        
        if suite_data.description is not None:
            suite.description = suite_data.description
        if suite_data.max_concurrent_tasks is not None:
            suite.max_concurrent_tasks = suite_data.max_concurrent_tasks
        
        await suite.save()
        
        # 更新测试用例
        if suite_data.testcase_ids is not None:
            await suite.testcases.clear()
            if suite_data.testcase_ids:
                testcases = await aitestrebortTestCase.filter(
                    id__in=suite_data.testcase_ids, project=project
                ).all()
                await suite.testcases.add(*testcases)
        
        suite_result = {
            "id": suite.id,
            "name": suite.name,
            "description": suite.description,
            "testcase_count": await suite.testcases.all().count(),
            "max_concurrent_tasks": suite.max_concurrent_tasks,
            "creator_id": suite.creator_id,
            "create_time": suite.create_time,
            "update_time": suite.update_time
        }
        
        return request.app.put_success(data=suite_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试套件不存在")
    except Exception as e:
        return request.app.error(msg=f"更新测试套件失败: {str(e)}")


async def delete_test_suite(request: Request, project_id: int, suite_id: int):
    """删除测试套件"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        suite = await aitestrebortTestSuite.get(id=suite_id, project=project)
        await suite.delete()
        
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试套件不存在")
    except Exception as e:
        return request.app.error(msg=f"删除测试套件失败: {str(e)}")


async def execute_test_suite(request: Request, project_id: int, suite_id: int):
    """执行测试套件"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        suite = await aitestrebortTestSuite.get(id=suite_id, project=project)
        
        # 获取测试用例数量
        testcase_count = await suite.testcases.all().count()
        if testcase_count == 0:
            return request.app.fail(msg="测试套件中没有测试用例")
        
        # 创建执行记录
        execution = await aitestrebortTestExecution.create(
            suite=suite,
            executor_id=request.state.user.id,
            total_count=testcase_count,
            status="pending"
        )
        
        # 这里应该启动异步任务执行测试
        # 暂时返回执行记录
        execution_result = {
            "id": execution.id,
            "suite_id": execution.suite_id,
            "status": execution.status,
            "executor_id": execution.executor_id,
            "total_count": execution.total_count,
            "passed_count": execution.passed_count,
            "failed_count": execution.failed_count,
            "skipped_count": execution.skipped_count,
            "error_count": execution.error_count,
            "create_time": execution.create_time
        }
        
        return request.app.post_success(data=execution_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或测试套件不存在")
    except Exception as e:
        return request.app.error(msg=f"执行测试套件失败: {str(e)}")


async def get_test_executions(request: Request, project_id: int):
    """获取测试执行记录列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        executions = await aitestrebortTestExecution.filter(
            suite__project=project
        ).order_by('-create_time').all()
        
        execution_list = []
        for execution in executions:
            # 获取套件名称
            suite = await aitestrebortTestSuite.get(id=execution.suite_id)
            
            execution_data = {
                "id": execution.id,
                "suite_id": execution.suite_id,
                "suite_name": suite.name,
                "status": execution.status,
                "executor_id": execution.executor_id,
                "started_at": execution.started_at,
                "completed_at": execution.completed_at,
                "execution_time": execution.execution_time,
                "total_count": execution.total_count,
                "passed_count": execution.passed_count,
                "failed_count": execution.failed_count,
                "skipped_count": execution.skipped_count,
                "error_count": execution.error_count,
                "create_time": execution.create_time
            }
            execution_list.append(execution_data)
        
        return request.app.get_success(data=execution_list)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取执行记录失败: {str(e)}")


async def get_execution_detail(request: Request, project_id: int, execution_id: int):
    """获取执行记录详情"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        execution = await aitestrebortTestExecution.get(
            id=execution_id, suite__project=project
        )
        
        # 获取测试用例结果
        results = await aitestrebortTestCaseResult.filter(execution=execution).all()
        result_list = []
        for result in results:
            # 获取测试用例名称
            testcase = await aitestrebortTestCase.get(id=result.testcase_id)
            
            result_data = {
                "id": result.id,
                "testcase_id": result.testcase_id,
                "testcase_name": testcase.name,
                "status": result.status,
                "error_message": result.error_message,
                "stack_trace": result.stack_trace,
                "started_at": result.started_at,
                "completed_at": result.completed_at,
                "execution_time": result.execution_time,
                "screenshots": result.screenshots,
                "execution_log": result.execution_log,
                "create_time": result.create_time
            }
            result_list.append(result_data)
        
        # 获取套件名称
        suite = await aitestrebortTestSuite.get(id=execution.suite_id)
        
        execution_data = {
            "id": execution.id,
            "suite_id": execution.suite_id,
            "suite_name": suite.name,
            "status": execution.status,
            "executor_id": execution.executor_id,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
            "execution_time": execution.execution_time,
            "total_count": execution.total_count,
            "passed_count": execution.passed_count,
            "failed_count": execution.failed_count,
            "skipped_count": execution.skipped_count,
            "error_count": execution.error_count,
            "create_time": execution.create_time,
            "results": result_list
        }
        
        return request.app.get_success(data=execution_data)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或执行记录不存在")
    except Exception as e:
        return request.app.error(msg=f"获取执行记录详情失败: {str(e)}")


async def cancel_test_execution(request: Request, project_id: int, execution_id: int):
    """取消测试执行"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        execution = await aitestrebortTestExecution.get(
            id=execution_id, suite__project=project
        )
        
        if execution.status not in ["pending", "running"]:
            return request.app.fail(msg="只能取消等待中或执行中的任务")
        
        execution.status = "cancelled"
        await execution.save()
        
        # 这里应该取消对应的异步任务
        
        return request.app.put_success(data={"message": "执行已取消"})
        
    except DoesNotExist:
        return request.app.fail(msg="项目或执行记录不存在")
    except Exception as e:
        return request.app.error(msg=f"取消执行失败: {str(e)}")