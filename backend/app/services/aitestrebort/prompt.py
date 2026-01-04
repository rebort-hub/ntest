"""
aitestrebort 提示词管理服务
"""
import logging
from typing import List, Dict, Optional
from fastapi import Request
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from app.models.aitestrebort.project import aitestrebortPrompt, aitestrebortProject, aitestrebortProjectMember
from app.schemas.aitestrebort.project import (
    aitestrebortPromptCreateSchema,
    aitestrebortPromptUpdateSchema
)

logger = logging.getLogger(__name__)


# 提示词类型常量
PROMPT_TYPE_CHOICES = [
    ('general', '通用对话'),
    ('completeness_analysis', '完整性分析'),
    ('consistency_analysis', '一致性分析'),
    ('testability_analysis', '可测性分析'),
    ('feasibility_analysis', '可行性分析'),
    ('clarity_analysis', '清晰度分析'),
    ('test_case_execution', '测试用例执行'),
    ('brain_orchestrator', '智能规划'),
    ('diagram_generation', '图表生成'),
]

PROGRAM_CALL_TYPES = [
    'completeness_analysis',
    'consistency_analysis',
    'testability_analysis',
    'feasibility_analysis',
    'clarity_analysis',
    'test_case_execution',
    'diagram_generation',
]


async def get_prompts(request: Request):
    """
    获取用户的提示词列表
    支持项目隔离和全局提示词
    """
    try:
        project_id = request.query_params.get('project_id')
        prompt_type = request.query_params.get('prompt_type')
        is_active = request.query_params.get('is_active')
        search = request.query_params.get('search')
        
        # 构建查询条件
        query = Q(user_id=request.state.user.id)
        
        # 项目过滤
        if project_id:
            # 检查项目权限
            try:
                project = await aitestrebortProject.get(id=project_id)
            except DoesNotExist:
                return request.app.fail(msg="项目不存在")
            
            is_member = await aitestrebortProjectMember.filter(
                project=project,
                user_id=request.state.user.id
            ).exists()
            
            if not is_member and not request.state.user.is_superuser:
                return request.app.forbidden(msg="无权限访问此项目")
            
            query &= Q(project_id=project_id)
        else:
            # 不指定项目时，返回全局提示词
            query &= Q(project_id=None)
        
        # 类型过滤
        if prompt_type:
            query &= Q(prompt_type=prompt_type)
        
        # 激活状态过滤
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            query &= Q(is_active=is_active_bool)
        
        # 搜索
        if search:
            query &= (Q(name__icontains=search) | Q(description__icontains=search))
        
        # 查询提示词
        prompts = await aitestrebortPrompt.filter(query).order_by('-update_time').all()
        
        prompts_list = []
        for prompt in prompts:
            prompts_list.append({
                'id': prompt.id,
                'name': prompt.name,
                'content': prompt.content,
                'description': prompt.description,
                'prompt_type': prompt.prompt_type,
                'is_default': prompt.is_default,
                'is_active': prompt.is_active,
                'user_id': prompt.user_id,
                'project_id': prompt.project_id,
                'created_at': prompt.create_time.isoformat() if prompt.create_time else None,
                'updated_at': prompt.update_time.isoformat() if prompt.update_time else None,
            })
        
        return request.app.get_success(data={
            "prompts": prompts_list,
            "total": len(prompts_list)
        })
        
    except Exception as e:
        logger.error(f"Error in get_prompts: {str(e)}", exc_info=True)
        return request.app.error(msg=f"获取提示词列表失败: {str(e)}")


async def create_prompt(request: Request, prompt_data: dict):
    """
    创建提示词
    """
    try:
        project_id = prompt_data.get('project_id')
        name = prompt_data.get('name')
        content = prompt_data.get('content')
        description = prompt_data.get('description')
        prompt_type = prompt_data.get('prompt_type', 'general')
        is_default = prompt_data.get('is_default', False)
        is_active = prompt_data.get('is_active', True)
        
        # 验证必填字段
        if not name or not content:
            return request.app.fail(msg="提示词名称和内容不能为空")
        
        # 验证内容不为空
        if not content.strip():
            return request.app.fail(msg="提示词内容不能为空")
        
        # 如果指定了项目，检查项目权限
        project = None
        if project_id:
            try:
                project = await aitestrebortProject.get(id=project_id)
            except DoesNotExist:
                return request.app.fail(msg="项目不存在")
            
            is_member = await aitestrebortProjectMember.filter(
                project=project,
                user_id=request.state.user.id
            ).exists()
            
            if not is_member and not request.state.user.is_superuser:
                return request.app.forbidden(msg="无权限访问此项目")
        
        # 程序调用类型不允许设为默认
        if is_default and prompt_type in PROGRAM_CALL_TYPES:
            return request.app.fail(msg="程序调用类型的提示词不能设为默认，会影响对话功能")
        
        # 检查名称唯一性
        existing = await aitestrebortPrompt.filter(
            user_id=request.state.user.id,
            name=name,
            project_id=project_id
        ).exists()
        
        if existing:
            return request.app.fail(msg="该名称的提示词已存在")
        
        # 检查程序调用类型的唯一性
        if prompt_type in PROGRAM_CALL_TYPES:
            existing_program = await aitestrebortPrompt.filter(
                user_id=request.state.user.id,
                prompt_type=prompt_type,
                project_id=project_id
            ).exists()
            
            if existing_program:
                type_name = dict(PROMPT_TYPE_CHOICES).get(prompt_type, prompt_type)
                return request.app.fail(msg=f"每个用户只能有一个{type_name}类型的提示词")
        
        # 如果设置为默认，取消其他默认提示词（仅限通用对话类型）
        if is_default and prompt_type == 'general':
            await aitestrebortPrompt.filter(
                user_id=request.state.user.id,
                is_default=True,
                prompt_type='general',
                project_id=project_id
            ).update(is_default=False)
        
        # 创建提示词
        prompt = await aitestrebortPrompt.create(
            project=project,
            user_id=request.state.user.id,
            name=name,
            content=content,
            description=description,
            prompt_type=prompt_type,
            is_default=is_default,
            is_active=is_active
        )
        
        return request.app.post_success(data={
            'id': prompt.id,
            'name': prompt.name,
            'content': prompt.content,
            'description': prompt.description,
            'prompt_type': prompt.prompt_type,
            'is_default': prompt.is_default,
            'is_active': prompt.is_active,
            'user_id': prompt.user_id,
            'project_id': prompt.project_id,
            'created_at': prompt.create_time.isoformat() if prompt.create_time else None,
            'updated_at': prompt.update_time.isoformat() if prompt.update_time else None,
        })
        
    except Exception as e:
        logger.error(f"Error in create_prompt: {str(e)}", exc_info=True)
        return request.app.error(msg=f"创建提示词失败: {str(e)}")


async def update_prompt(request: Request, prompt_id: int, prompt_data: dict):
    """
    更新提示词
    """
    try:
        # 获取提示词
        prompt = await aitestrebortPrompt.get(
            id=prompt_id,
            user_id=request.state.user.id
        )
        
        # 更新字段
        if 'name' in prompt_data:
            # 检查名称唯一性
            existing = await aitestrebortPrompt.filter(
                user_id=request.state.user.id,
                name=prompt_data['name'],
                project_id=prompt.project_id
            ).exclude(id=prompt_id).exists()
            
            if existing:
                return request.app.fail(msg="该名称的提示词已存在")
            
            prompt.name = prompt_data['name']
        
        if 'content' in prompt_data:
            if not prompt_data['content'].strip():
                return request.app.fail(msg="提示词内容不能为空")
            prompt.content = prompt_data['content']
        
        if 'description' in prompt_data:
            prompt.description = prompt_data['description']
        
        if 'prompt_type' in prompt_data:
            new_type = prompt_data['prompt_type']
            
            # 检查程序调用类型的唯一性
            if new_type in PROGRAM_CALL_TYPES:
                existing_program = await aitestrebortPrompt.filter(
                    user_id=request.state.user.id,
                    prompt_type=new_type,
                    project_id=prompt.project_id
                ).exclude(id=prompt_id).exists()
                
                if existing_program:
                    type_name = dict(PROMPT_TYPE_CHOICES).get(new_type, new_type)
                    return request.app.fail(msg=f"每个用户只能有一个{type_name}类型的提示词")
            
            prompt.prompt_type = new_type
        
        if 'is_default' in prompt_data:
            is_default = prompt_data['is_default']
            
            # 程序调用类型不允许设为默认
            if is_default and prompt.prompt_type in PROGRAM_CALL_TYPES:
                return request.app.fail(msg="程序调用类型的提示词不能设为默认")
            
            # 如果设置为默认，取消其他默认提示词
            if is_default and prompt.prompt_type == 'general':
                await aitestrebortPrompt.filter(
                    user_id=request.state.user.id,
                    is_default=True,
                    prompt_type='general',
                    project_id=prompt.project_id
                ).exclude(id=prompt_id).update(is_default=False)
            
            prompt.is_default = is_default
        
        if 'is_active' in prompt_data:
            prompt.is_active = prompt_data['is_active']
        
        await prompt.save()
        
        return request.app.put_success(data={
            'id': prompt.id,
            'name': prompt.name,
            'content': prompt.content,
            'description': prompt.description,
            'prompt_type': prompt.prompt_type,
            'is_default': prompt.is_default,
            'is_active': prompt.is_active,
            'user_id': prompt.user_id,
            'project_id': prompt.project_id,
            'updated_at': prompt.update_time.isoformat() if prompt.update_time else None,
        })
        
    except DoesNotExist:
        return request.app.fail(msg="提示词不存在")
    except Exception as e:
        logger.error(f"Error in update_prompt: {str(e)}", exc_info=True)
        return request.app.error(msg=f"更新提示词失败: {str(e)}")


async def delete_prompt(request: Request, prompt_id: int):
    """
    删除提示词
    """
    try:
        prompt = await aitestrebortPrompt.get(
            id=prompt_id,
            user_id=request.state.user.id
        )
        
        await prompt.delete()
        
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="提示词不存在")
    except Exception as e:
        logger.error(f"Error in delete_prompt: {str(e)}", exc_info=True)
        return request.app.error(msg=f"删除提示词失败: {str(e)}")


async def get_default_prompt(request: Request):
    """
    获取用户的默认提示词（仅限通用对话类型）
    """
    try:
        project_id = request.query_params.get('project_id')
        
        query = Q(
            user_id=request.state.user.id,
            prompt_type='general',
            is_default=True,
            is_active=True
        )
        
        if project_id:
            query &= Q(project_id=project_id)
        else:
            query &= Q(project_id=None)
        
        prompt = await aitestrebortPrompt.filter(query).first()
        
        if prompt:
            return request.app.get_success(data={
                'id': prompt.id,
                'name': prompt.name,
                'content': prompt.content,
                'description': prompt.description,
                'prompt_type': prompt.prompt_type,
                'is_default': prompt.is_default,
                'is_active': prompt.is_active,
                'user_id': prompt.user_id,
                'project_id': prompt.project_id,
                'created_at': prompt.create_time.isoformat() if prompt.create_time else None,
                'updated_at': prompt.update_time.isoformat() if prompt.update_time else None,
            })
        else:
            return request.app.get_success(data=None, msg="用户暂无默认提示词")
        
    except Exception as e:
        logger.error(f"Error in get_default_prompt: {str(e)}", exc_info=True)
        return request.app.error(msg=f"获取默认提示词失败: {str(e)}")


async def get_prompt_by_type(request: Request):
    """
    根据类型获取提示词
    """
    try:
        prompt_type = request.query_params.get('type')
        project_id = request.query_params.get('project_id')
        
        if not prompt_type:
            return request.app.fail(msg="缺少type参数")
        
        query = Q(
            user_id=request.state.user.id,
            prompt_type=prompt_type,
            is_active=True
        )
        
        if project_id:
            query &= Q(project_id=project_id)
        else:
            query &= Q(project_id=None)
        
        prompt = await aitestrebortPrompt.filter(query).first()
        
        if prompt:
            return request.app.get_success(data={
                'id': prompt.id,
                'name': prompt.name,
                'content': prompt.content,
                'description': prompt.description,
                'prompt_type': prompt.prompt_type,
                'is_default': prompt.is_default,
                'is_active': prompt.is_active,
                'user_id': prompt.user_id,
                'project_id': prompt.project_id,
                'created_at': prompt.create_time.isoformat() if prompt.create_time else None,
                'updated_at': prompt.update_time.isoformat() if prompt.update_time else None,
            })
        else:
            type_name = dict(PROMPT_TYPE_CHOICES).get(prompt_type, prompt_type)
            return request.app.get_success(data=None, msg=f"用户暂无{type_name}类型的提示词")
        
    except Exception as e:
        logger.error(f"Error in get_prompt_by_type: {str(e)}", exc_info=True)
        return request.app.error(msg=f"获取提示词失败: {str(e)}")


async def get_prompt_types(request: Request):
    """
    获取所有提示词类型
    """
    try:
        types = [
            {
                'value': choice[0],
                'label': choice[1],
                'is_program_call': choice[0] in PROGRAM_CALL_TYPES
            }
            for choice in PROMPT_TYPE_CHOICES
        ]
        
        return request.app.get_success(data=types)
        
    except Exception as e:
        logger.error(f"Error in get_prompt_types: {str(e)}", exc_info=True)
        return request.app.error(msg=f"获取提示词类型失败: {str(e)}")


async def set_default_prompt(request: Request, prompt_id: int):
    """
    设置指定提示词为默认提示词
    """
    try:
        prompt = await aitestrebortPrompt.get(
            id=prompt_id,
            user_id=request.state.user.id
        )
        
        # 检查提示词是否处于激活状态
        if not prompt.is_active:
            return request.app.fail(msg="无法设置未激活的提示词为默认")
        
        # 检查是否为程序调用类型
        if prompt.prompt_type in PROGRAM_CALL_TYPES:
            return request.app.fail(msg="程序调用类型的提示词不能设为默认")
        
        # 取消其他默认提示词
        await aitestrebortPrompt.filter(
            user_id=request.state.user.id,
            is_default=True,
            project_id=prompt.project_id
        ).exclude(id=prompt_id).update(is_default=False)
        
        # 设置当前提示词为默认
        prompt.is_default = True
        await prompt.save()
        
        return request.app.success(
            msg="默认提示词设置成功",
            data={
                'id': prompt.id,
                'name': prompt.name,
                'is_default': prompt.is_default,
            }
        )
        
    except DoesNotExist:
        return request.app.fail(msg="提示词不存在")
    except Exception as e:
        logger.error(f"Error in set_default_prompt: {str(e)}", exc_info=True)
        return request.app.error(msg=f"设置默认提示词失败: {str(e)}")


async def clear_default_prompt(request: Request):
    """
    清除用户的默认提示词设置
    """
    try:
        project_id = request.query_params.get('project_id')
        
        query = Q(
            user_id=request.state.user.id,
            is_default=True
        )
        
        if project_id:
            query &= Q(project_id=project_id)
        else:
            query &= Q(project_id=None)
        
        updated_count = await aitestrebortPrompt.filter(query).update(is_default=False)
        
        return request.app.success(
            msg=f"已清除默认提示词设置，影响{updated_count}条记录",
            data={
                'updated_count': updated_count
            }
        )
        
    except Exception as e:
        logger.error(f"Error in clear_default_prompt: {str(e)}", exc_info=True)
        return request.app.error(msg=f"清除默认提示词失败: {str(e)}")


async def duplicate_prompt(request: Request, prompt_id: int):
    """
    复制提示词
    """
    try:
        original_prompt = await aitestrebortPrompt.get(
            id=prompt_id,
            user_id=request.state.user.id
        )
        
        # 创建副本
        new_prompt = await aitestrebortPrompt.create(
            project_id=original_prompt.project_id,
            user_id=request.state.user.id,
            name=f"{original_prompt.name} (副本)",
            content=original_prompt.content,
            description=f"复制自: {original_prompt.description}" if original_prompt.description else "复制的提示词",
            prompt_type=original_prompt.prompt_type,
            is_default=False,  # 副本不设为默认
            is_active=True
        )
        
        return request.app.success(
            msg="提示词复制成功",
            data={
                'id': new_prompt.id,
                'name': new_prompt.name,
                'content': new_prompt.content,
                'description': new_prompt.description,
                'prompt_type': new_prompt.prompt_type,
                'is_default': new_prompt.is_default,
                'is_active': new_prompt.is_active,
            }
        )
        
    except DoesNotExist:
        return request.app.fail(msg="提示词不存在")
    except Exception as e:
        logger.error(f"Error in duplicate_prompt: {str(e)}", exc_info=True)
        return request.app.error(msg=f"复制提示词失败: {str(e)}")
