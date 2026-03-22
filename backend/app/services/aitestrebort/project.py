"""
aitestrebort 项目管理服务
"""
from typing import Optional
from fastapi import Request, Depends
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q

from app.models.aitestrebort import (
    aitestrebortProject, aitestrebortProjectCredential, aitestrebortProjectMember,
    aitestrebortLLMConfig, aitestrebortMCPConfig, aitestrebortAPIKey,
    aitestrebortConversation, aitestrebortMessage
)
from app.schemas.aitestrebort.project import (
    aitestrebortProjectCreateSchema, aitestrebortProjectUpdateSchema, aitestrebortProjectQueryForm,
    aitestrebortProjectCredentialCreateSchema, aitestrebortProjectMemberCreateSchema,
    aitestrebortLLMConfigCreateSchema, aitestrebortMCPConfigCreateSchema, aitestrebortAPIKeyCreateSchema,
    aitestrebortLLMConfigUpdateSchema, aitestrebortMCPConfigUpdateSchema, aitestrebortAPIKeyUpdateSchema,
    aitestrebortConversationCreateSchema, aitestrebortMessageCreateSchema
)
from utils.logs.log import logger


async def test_simple(request: Request):
    """简单测试接口"""
    return request.app.get_success(data={"message": "aitestrebort 项目 API 工作正常"})


async def get_projects(request: Request, form: aitestrebortProjectQueryForm = Depends()):
    """获取项目列表"""
    try:
        query = aitestrebortProject.all()
        
        # 搜索过滤
        if form.search:
            query = query.filter(
                Q(name__icontains=form.search) | 
                Q(description__icontains=form.search)
            )
        
        # 分页
        total = await query.count()
        
        if form.page_no and form.page_size:
            projects = await query.offset((form.page_no - 1) * form.page_size).limit(form.page_size).all()
        else:
            projects = await query.all()
        
        # 转换为响应格式
        project_list = []
        for project in projects:
            # 获取统计信息
            testcase_count = await project.testcases.all().count()
            member_count = await project.members.all().count()
            
            project_data = {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "creator_id": project.creator_id,
                "create_time": project.create_time,
                "update_time": project.update_time,
                "testcase_count": testcase_count,
                "member_count": member_count
            }
            project_list.append(project_data)
        
        return request.app.get_success(data={
            "items": project_list,
            "total": total,
            "page": form.page_no or 1,
            "page_size": form.page_size or 20
        })
        
    except Exception as e:
        return request.app.error(msg=f"获取项目列表失败: {str(e)}")


async def create_project(request: Request, project_data: aitestrebortProjectCreateSchema):
    """创建项目"""
    try:
        # 检查项目名称是否已存在
        if await aitestrebortProject.filter(name=project_data.name).exists():
            return request.app.fail(msg="项目名称已存在")
        
        # 创建项目
        project = await aitestrebortProject.create(
            name=project_data.name,
            description=project_data.description,
            creator_id=request.state.user.id
        )
        
        # 添加创建者为项目管理员
        await aitestrebortProjectMember.create(
            project=project,
            user_id=request.state.user.id,
            role="owner"
        )
        
        # 手动构建返回数据
        project_result = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "creator_id": project.creator_id,
            "create_time": project.create_time,
            "update_time": project.update_time,
            "testcase_count": 0,
            "member_count": 1
        }
        
        return request.app.post_success(data=project_result)
        
    except Exception as e:
        return request.app.error(msg=f"创建项目失败: {str(e)}")


async def get_project_detail(request: Request, project_id: int):
    """获取项目详情"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查用户权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取统计信息
        testcase_count = await project.testcases.all().count()
        member_count = await project.members.all().count()
        suite_count = await project.test_suites.all().count()
        
        # 手动构建项目详情数据
        project_data = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "creator_id": project.creator_id,
            "create_time": project.create_time.isoformat() if project.create_time else None,
            "update_time": project.update_time.isoformat() if project.update_time else None,
            "status": "active",  # 默认状态为活跃，因为模型中没有状态字段
            "testcase_count": testcase_count,
            "member_count": member_count,
            "suite_count": suite_count
        }
        
        return request.app.get_success(data=project_data)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取项目详情失败: {str(e)}")


async def update_project(request: Request, project_id: int, project_data: aitestrebortProjectUpdateSchema):
    """更新项目"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查用户权限（只有管理员可以修改）
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限修改此项目")
        
        # 更新项目信息
        if project_data.name and project_data.name != project.name:
            # 检查新名称是否已存在
            if await aitestrebortProject.filter(name=project_data.name).exclude(id=project_id).exists():
                return request.app.fail(msg="项目名称已存在")
            project.name = project_data.name
        
        if project_data.description is not None:
            project.description = project_data.description
        
        await project.save()
        
        # 手动构建返回数据
        project_result = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "creator_id": project.creator_id,
            "create_time": project.create_time,
            "update_time": project.update_time
        }
        
        return request.app.put_success(data=project_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"更新项目失败: {str(e)}")


async def delete_project(request: Request, project_id: int):
    """删除项目"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查用户权限（项目创建者或拥有者可以删除）
        is_creator = project.creator_id == request.state.user.id
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role="owner"
        ).first()
        
        if not is_creator and not member:
            return request.app.forbidden(msg="无权限删除此项目")
        
        # 检查项目下是否有测试用例
        from app.models.aitestrebort import aitestrebortTestCase
        testcase_count = await aitestrebortTestCase.filter(project=project).count()
        if testcase_count > 0:
            return request.app.fail(msg=f"无法删除项目，该项目下还有 {testcase_count} 个测试用例。请先删除所有测试用例。")
        
        await project.delete()
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"删除项目失败: {str(e)}")


# 项目凭据管理
async def get_project_credentials(request: Request, project_id: int):
    """获取项目凭据列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        credentials = await aitestrebortProjectCredential.filter(project=project).all()
        
        credential_list = []
        for credential in credentials:
            credential_data = {
                "id": credential.id,
                "system_url": credential.system_url,
                "username": credential.username,
                "user_role": credential.user_role,
                "create_time": credential.create_time
                # 注意：不返回密码
            }
            credential_list.append(credential_data)
        
        return request.app.get_success(data=credential_list)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取项目凭据失败: {str(e)}")


async def create_project_credential(request: Request, project_id: int, credential_data: aitestrebortProjectCredentialCreateSchema):
    """创建项目凭据"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限（只有管理员可以添加凭据）
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限添加项目凭据")
        
        credential = await aitestrebortProjectCredential.create(
            project=project,
            system_url=credential_data.system_url,
            username=credential_data.username,
            password=credential_data.password,
            user_role=credential_data.user_role
        )
        
        credential_result = {
            "id": credential.id,
            "system_url": credential.system_url,
            "username": credential.username,
            "user_role": credential.user_role,
            "create_time": credential.create_time
        }
        
        return request.app.post_success(data=credential_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"创建项目凭据失败: {str(e)}")


# 项目成员管理
async def get_project_members(request: Request, project_id: int):
    """获取项目成员列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        members = await aitestrebortProjectMember.filter(project=project).all()
        
        member_list = []
        for member in members:
            member_data = {
                "id": member.id,
                "user_id": member.user_id,
                "role": member.role,
                "create_time": member.create_time
            }
            member_list.append(member_data)
        
        return request.app.get_success(data=member_list)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取项目成员失败: {str(e)}")


async def add_project_member(request: Request, project_id: int, member_data: aitestrebortProjectMemberCreateSchema):
    """添加项目成员"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限（只有管理员可以添加成员）
        current_member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not current_member:
            return request.app.forbidden(msg="无权限添加项目成员")
        
        # 检查用户是否已经是项目成员
        if await aitestrebortProjectMember.filter(
            project=project, user_id=member_data.user_id
        ).exists():
            return request.app.fail(msg="用户已经是项目成员")
        
        member = await aitestrebortProjectMember.create(
            project=project,
            user_id=member_data.user_id,
            role=member_data.role
        )
        
        member_result = {
            "id": member.id,
            "user_id": member.user_id,
            "role": member.role,
            "create_time": member.create_time
        }
        
        return request.app.post_success(data=member_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"添加项目成员失败: {str(e)}")


# LLM 配置管理
async def get_llm_configs(
    request: Request, 
    project_id: int,
    search: Optional[str] = "",
    provider: Optional[str] = "",
    is_active: Optional[bool] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = 20
):
    """获取 LLM 配置列表 - 只返回全局配置"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 构建查询条件 - 只查询全局配置
        query = aitestrebortLLMConfig.filter(project_id__isnull=True)
        
        # 搜索条件
        if search:
            query = query.filter(
                Q(name__icontains=search) | Q(config_name__icontains=search)
            )
        if provider:
            query = query.filter(provider=provider)
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        # 获取总数
        total = await query.count()
        
        # 分页
        offset = (page - 1) * page_size
        configs = await query.offset(offset).limit(page_size).order_by('-create_time').all()
        
        config_list = []
        for config in configs:
            config_data = {
                "id": config.id,
                "name": config.config_name or config.name,  # 优先显示用户自定义名称
                "provider": config.provider,
                "model_name": config.model_name,
                "base_url": config.base_url,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
                "is_default": config.is_default,
                "is_active": config.is_active,
                "create_time": config.create_time
                # 注意：不返回 API 密钥
            }
            config_list.append(config_data)
        
        return request.app.get_success(data={
            "items": config_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取 LLM 配置失败: {str(e)}")


async def create_llm_config(request: Request, project_id: int, config_data: aitestrebortLLMConfigCreateSchema):
    """创建 LLM 配置"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限（只有管理员可以添加配置）
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限添加 LLM 配置")
        
        # 如果设置为默认配置，先取消其他默认配置
        if config_data.is_default:
            await aitestrebortLLMConfig.filter(project_id__isnull=True, is_default=True).update(is_default=False)
        
        config = await aitestrebortLLMConfig.create(
            # project=project,  # 创建全局配置，不关联项目
            config_name=getattr(config_data, 'config_name', None),
            name=config_data.name,
            provider=config_data.provider,
            model_name=config_data.model_name,
            api_key=config_data.api_key,
            base_url=config_data.base_url,
            system_prompt=getattr(config_data, 'system_prompt', None),
            temperature=config_data.temperature,
            max_tokens=config_data.max_tokens,
            supports_vision=getattr(config_data, 'supports_vision', False),
            context_limit=getattr(config_data, 'context_limit', 128000),
            is_default=config_data.is_default,
            is_active=config_data.is_active,
            creator_id=request.state.user.id
        )
        
        config_result = {
            "id": config.id,
            "name": config.config_name or config.name,
            "provider": config.provider,
            "model_name": config.model_name,
            "base_url": config.base_url,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "is_default": config.is_default,
            "is_active": config.is_active,
            "create_time": config.create_time
        }
        
        return request.app.post_success(data=config_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"创建 LLM 配置失败: {str(e)}")


async def update_llm_config(request: Request, project_id: int, config_id: int, config_data: aitestrebortLLMConfigUpdateSchema):
    """更新 LLM 配置"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限修改 LLM 配置")
        
        config = await aitestrebortLLMConfig.get(id=config_id, project_id__isnull=True)
        
        # 更新字段
        if config_data.name is not None:
            config.name = config_data.name
        if config_data.provider is not None:
            config.provider = config_data.provider
        if config_data.model_name is not None:
            config.model_name = config_data.model_name
        if config_data.api_key is not None:
            config.api_key = config_data.api_key
        if config_data.base_url is not None:
            config.base_url = config_data.base_url
        if config_data.temperature is not None:
            config.temperature = config_data.temperature
        if config_data.max_tokens is not None:
            config.max_tokens = config_data.max_tokens
        if config_data.is_active is not None:
            config.is_active = config_data.is_active
        
        # 处理默认配置
        if config_data.is_default is not None and config_data.is_default:
            await aitestrebortLLMConfig.filter(project_id__isnull=True, is_default=True).update(is_default=False)
            config.is_default = True
        elif config_data.is_default is not None:
            config.is_default = config_data.is_default
        
        await config.save()
        
        config_result = {
            "id": config.id,
            "name": config.name,
            "provider": config.provider,
            "model_name": config.model_name,
            "base_url": config.base_url,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            "is_default": config.is_default,
            "is_active": config.is_active,
            "create_time": config.create_time
        }
        
        return request.app.put_success(data=config_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或 LLM 配置不存在")
    except Exception as e:
        return request.app.error(msg=f"更新 LLM 配置失败: {str(e)}")


async def delete_llm_config(request: Request, project_id: int, config_id: int):
    """删除 LLM 配置"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限删除 LLM 配置")
        
        config = await aitestrebortLLMConfig.get(id=config_id, project_id__isnull=True)
        await config.delete()
        
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目或 LLM 配置不存在")
    except Exception as e:
        return request.app.error(msg=f"删除 LLM 配置失败: {str(e)}")


# MCP 配置管理
async def get_mcp_configs(
    request: Request, 
    project_id: int, 
    search: Optional[str] = "", 
    is_enabled: Optional[bool] = None, 
    page: Optional[int] = 1, 
    page_size: Optional[int] = 20
):
    """获取 MCP 配置列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 构建查询条件
        query = aitestrebortMCPConfig.filter(user_id=request.state.user.id)
        
        # 搜索条件
        if search:
            query = query.filter(name__icontains=search)
        if is_enabled is not None:
            query = query.filter(is_enabled=is_enabled)
        
        # 获取总数
        total = await query.count()
        
        # 分页
        offset = (page - 1) * page_size
        configs = await query.offset(offset).limit(page_size).order_by('-create_time').all()
        
        config_list = []
        for config in configs:
            config_data = {
                "id": config.id,
                "name": config.name,
                "url": config.url,
                "transport": config.transport,
                "headers": config.headers,
                "is_enabled": config.is_enabled,
                "created_at": config.create_time
            }
            config_list.append(config_data)
        
        return request.app.get_success(data={
            "items": config_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取 MCP 配置失败: {str(e)}")


async def create_mcp_config(request: Request, project_id: int, config_data: aitestrebortMCPConfigCreateSchema):
    """创建 MCP 配置"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限（只有管理员可以添加配置）
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限添加 MCP 配置")
        
        # 检查配置名称是否已存在
        if await aitestrebortMCPConfig.filter(user_id=request.state.user.id, name=config_data.name).exists():
            return request.app.fail(msg="MCP 配置名称已存在")
        
        config = await aitestrebortMCPConfig.create(
            user_id=request.state.user.id,
            name=config_data.name,
            url=config_data.url,
            transport=config_data.transport,
            headers=config_data.headers or {},
            is_enabled=config_data.is_enabled,
            creator_id=request.state.user.id,
            create_user=request.state.user.id,
            update_user=request.state.user.id
        )
        
        config_result = {
            "id": config.id,
            "name": config.name,
            "url": config.url,
            "transport": config.transport,
            "headers": config.headers,
            "is_enabled": config.is_enabled,
            "created_at": config.create_time
        }
        
        return request.app.post_success(data=config_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"创建 MCP 配置失败: {str(e)}")


async def update_mcp_config(request: Request, project_id: int, config_id: int, config_data: aitestrebortMCPConfigUpdateSchema):
    """更新 MCP 配置"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限修改 MCP 配置")
        
        config = await aitestrebortMCPConfig.get(id=config_id, user_id=request.state.user.id)
        
        # 更新字段
        if config_data.name is not None:
            # 检查新名称是否已存在
            if await aitestrebortMCPConfig.filter(
                user_id=request.state.user.id, name=config_data.name
            ).exclude(id=config_id).exists():
                return request.app.fail(msg="MCP 配置名称已存在")
            config.name = config_data.name
        
        if config_data.url is not None:
            config.url = config_data.url
        if config_data.transport is not None:
            config.transport = config_data.transport
        if config_data.headers is not None:
            config.headers = config_data.headers
        if config_data.is_enabled is not None:
            config.is_enabled = config_data.is_enabled
        
        await config.save()
        
        config_result = {
            "id": config.id,
            "name": config.name,
            "url": config.url,
            "transport": config.transport,
            "headers": config.headers,
            "is_enabled": config.is_enabled,
            "created_at": config.create_time
        }
        
        return request.app.put_success(data=config_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或 MCP 配置不存在")
    except Exception as e:
        return request.app.error(msg=f"更新 MCP 配置失败: {str(e)}")


async def delete_mcp_config(request: Request, project_id: int, config_id: int):
    """删除 MCP 配置"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限删除 MCP 配置")
        
        config = await aitestrebortMCPConfig.get(id=config_id, user_id=request.state.user.id)
        await config.delete()
        
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目或 MCP 配置不存在")
    except Exception as e:
        return request.app.error(msg=f"删除 MCP 配置失败: {str(e)}")


async def test_mcp_config(request: Request, project_id: int, config_id: int):
    """测试 MCP 配置连接"""
    try:
        from .mcp_real import test_mcp_connection
        return await test_mcp_connection(request, project_id, config_id)
    except Exception as e:
        logger.error(f"Test MCP config failed: {str(e)}", exc_info=True)
        return request.app.error(msg=f"测试MCP配置失败: {str(e)}")


# API 密钥管理
async def get_api_keys(
    request: Request, 
    project_id: int, 
    search: Optional[str] = "", 
    service_type: Optional[str] = "", 
    is_active: Optional[bool] = None, 
    page: Optional[int] = 1, 
    page_size: Optional[int] = 20
):
    """获取 API 密钥列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 构建查询条件
        query = aitestrebortAPIKey.filter(user_id=request.state.user.id)
        
        # 搜索条件
        if search:
            query = query.filter(name__icontains=search)
        if service_type:
            query = query.filter(service=service_type)
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        # 获取总数
        total = await query.count()
        
        # 分页
        offset = (page - 1) * page_size
        logger.info(f"API Keys pagination: page={page}, page_size={page_size}, offset={offset}, total={total}")
        keys = await query.offset(offset).limit(page_size).order_by('-create_time').all()
        
        key_list = []
        for key in keys:
            key_data = {
                "id": key.id,
                "name": key.name,
                "service_type": key.service,
                "api_key": key.key_value,
                "description": key.description,
                "is_active": key.is_active,
                "created_at": key.create_time
            }
            key_list.append(key_data)
        
        logger.info(f"Returning {len(key_list)} API keys")
        return request.app.get_success(data={
            "items": key_list,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取 API 密钥失败: {str(e)}")


async def create_api_key(request: Request, project_id: int, key_data: aitestrebortAPIKeyCreateSchema):
    """创建 API 密钥"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限（只有管理员可以添加密钥）
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限添加 API 密钥")
        
        # 检查密钥名称是否已存在
        if await aitestrebortAPIKey.filter(user_id=request.state.user.id, name=key_data.name).exists():
            return request.app.fail(msg="API 密钥名称已存在")
        
        key = await aitestrebortAPIKey.create(
            user_id=request.state.user.id,
            name=key_data.name,
            service=key_data.service_type,
            key_value=key_data.api_key,
            description=key_data.description,
            is_active=key_data.is_active,
            creator_id=request.state.user.id,
            create_user=request.state.user.id,
            update_user=request.state.user.id
        )
        
        key_result = {
            "id": key.id,
            "name": key.name,
            "service_type": key.service,
            "api_key": key.key_value,
            "description": key.description,
            "is_active": key.is_active,
            "created_at": key.create_time
        }
        
        return request.app.post_success(data=key_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"创建 API 密钥失败: {str(e)}")


async def update_api_key(request: Request, project_id: int, key_id: int, key_data: aitestrebortAPIKeyUpdateSchema):
    """更新 API 密钥"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限修改 API 密钥")
        
        key = await aitestrebortAPIKey.get(id=key_id, user_id=request.state.user.id)
        
        # 更新字段
        if key_data.name is not None:
            # 检查新名称是否已存在
            if await aitestrebortAPIKey.filter(
                # project=project,  # 全局配置，不关联项目 name=key_data.name
            ).exclude(id=key_id).exists():
                return request.app.fail(msg="API 密钥名称已存在")
            key.name = key_data.name
        
        if key_data.service_type is not None:
            key.service = key_data.service_type
        if key_data.api_key is not None:
            key.key_value = key_data.api_key
        if key_data.description is not None:
            key.description = key_data.description
        if key_data.is_active is not None:
            key.is_active = key_data.is_active
        
        await key.save()
        
        key_result = {
            "id": key.id,
            "name": key.name,
            "service_type": key.service,
            "api_key": key.key_value,
            "description": key.description,
            "is_active": key.is_active,
            "created_at": key.create_time
        }
        
        return request.app.put_success(data=key_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或 API 密钥不存在")
    except Exception as e:
        return request.app.error(msg=f"更新 API 密钥失败: {str(e)}")


async def delete_api_key(request: Request, project_id: int, key_id: int):
    """删除 API 密钥"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限删除 API 密钥")
        
        key = await aitestrebortAPIKey.get(id=key_id, user_id=request.state.user.id)
        await key.delete()
        
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目或 API 密钥不存在")
    except Exception as e:
        return request.app.error(msg=f"删除 API 密钥失败: {str(e)}")


async def test_api_key(request: Request, project_id: int, key_id: int):
    """测试 API 密钥"""
    try:
        from .api_key_real import test_api_key as real_test
        return await real_test(request, project_id, key_id)
    except Exception as e:
        logger.error(f"Test API key failed: {str(e)}", exc_info=True)
        return request.app.error(msg=f"测试API密钥失败: {str(e)}")


async def regenerate_api_key(request: Request, project_id: int, key_id: int):
    """重新生成 API 密钥"""
    try:
        from .api_key_real import regenerate_api_key as real_regenerate
        return await real_regenerate(request, project_id, key_id)
    except Exception as e:
        logger.error(f"Regenerate API key failed: {str(e)}", exc_info=True)
        return request.app.error(msg=f"重新生成API密钥失败: {str(e)}")


# LLM 对话管理
async def get_conversations(request: Request, project_id: int):
    """获取对话列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        conversations = await aitestrebortConversation.filter(
            project=project, user_id=request.state.user.id
        ).order_by('-create_time').all()
        
        conversation_list = []
        for conversation in conversations:
            conversation_data = {
                "id": conversation.id,
                "session_id": conversation.session_id,
                "title": conversation.title,
                "llm_config_id": conversation.llm_config_id,
                "user_id": conversation.user_id,
                "is_active": conversation.is_active,
                "create_time": conversation.create_time
            }
            conversation_list.append(conversation_data)
        
        return request.app.get_success(data=conversation_list)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取对话列表失败: {str(e)}")


async def create_conversation(request: Request, project_id: int, conversation_data: aitestrebortConversationCreateSchema):
    """创建对话"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 验证 LLM 配置是否存在
        llm_config = None
        if conversation_data.llm_config_id:
            llm_config = await aitestrebortLLMConfig.get(
                id=conversation_data.llm_config_id, project=project
            )
        
        # 生成会话ID
        import uuid
        session_id = str(uuid.uuid4())
        
        conversation = await aitestrebortConversation.create(
            project=project,  # 关联到项目
            session_id=session_id,
            title=conversation_data.title or "新对话",
            llm_config=llm_config,
            user_id=request.state.user.id
        )
        
        conversation_result = {
            "id": conversation.id,
            "session_id": conversation.session_id,
            "title": conversation.title,
            "llm_config_id": conversation.llm_config_id,
            "user_id": conversation.user_id,
            "is_active": conversation.is_active,
            "create_time": conversation.create_time
        }
        
        return request.app.post_success(data=conversation_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或 LLM 配置不存在")
    except Exception as e:
        return request.app.error(msg=f"创建对话失败: {str(e)}")


async def get_conversation_messages(request: Request, project_id: int, conversation_id: int):
    """获取对话消息"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        conversation = await aitestrebortConversation.get(
            id=conversation_id, project=project, user_id=request.state.user.id
        )
        
        messages = await conversation.messages.all().order_by('create_time')
        
        message_list = []
        for message in messages:
            message_data = {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "message_type": message.message_type,
                "metadata": message.metadata,
                "tokens_used": message.tokens_used,
                "create_time": message.create_time
            }
            message_list.append(message_data)
        
        return request.app.get_success(data=message_list)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或对话不存在")
    except Exception as e:
        return request.app.error(msg=f"获取对话消息失败: {str(e)}")


async def send_message(request: Request, project_id: int, conversation_id: int, message_data: aitestrebortMessageCreateSchema):
    """发送消息并获取真实的LLM回复"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        conversation = await aitestrebortConversation.get(
            id=conversation_id, project=project, user_id=request.state.user.id
        )
        
        # 创建用户消息
        user_message = await aitestrebortMessage.create(
            conversation=conversation,
            role=message_data.role,
            content=message_data.content,
            message_type=getattr(message_data, 'message_type', 'text'),
            metadata=getattr(message_data, 'metadata', {})
        )
        
        # 获取 LLM 配置 - 使用更宽松的查询条件
        llm_config = None
        if conversation.llm_config_id:
            try:
                llm_config = await aitestrebortLLMConfig.get(
                    id=conversation.llm_config_id,
                    is_active=True
                )
            except DoesNotExist:
                pass
        
        if not llm_config:
            # 优先使用默认的全局配置
            llm_config = await aitestrebortLLMConfig.filter(
                project_id__isnull=True,
                is_default=True,
                is_active=True
            ).first()
        
        if not llm_config:
            # 如果没有默认配置，使用任意可用的全局配置
            llm_config = await aitestrebortLLMConfig.filter(
                project_id__isnull=True,
                is_active=True
            ).first()
        
        if not llm_config:
            # 如果还是没有，使用任意可用的配置（包括项目配置）
            llm_config = await aitestrebortLLMConfig.filter(
                is_active=True
            ).first()
        
        if not llm_config:
            return request.app.fail(msg="未找到可用的 LLM 配置，请先在项目设置中配置 LLM")
        
        # 创建 LLM 实例
        try:
            from .ai_generator_real import create_llm_instance
            llm = create_llm_instance(llm_config, temperature=0.7)
        except Exception as e:
            logger.error(f"Failed to create LLM instance: {e}", exc_info=True)
            return request.app.error(msg=f"LLM 初始化失败: {str(e)}")
        
        # 构建消息历史
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        messages = []
        
        # 添加系统提示词
        system_prompt = None
        
        # 优先使用对话关联的提示词
        if conversation.prompt_id:
            try:
                prompt = await aitestrebortPrompt.get(
                    id=conversation.prompt_id,
                    is_active=True
                )
                system_prompt = prompt.content
            except DoesNotExist:
                pass
        
        # 如果没有关联提示词，使用 LLM 配置的系统提示词
        if not system_prompt and llm_config.system_prompt:
            system_prompt = llm_config.system_prompt
        
        # 如果还是没有，使用默认的测试用例生成提示词
        if not system_prompt:
            system_prompt = """你是一个专业的测试工程师，擅长根据需求描述生成高质量的测试用例。

请根据用户提供的需求描述，生成详细的测试用例。测试用例应该包含：
1. 用例名称：简洁明确地描述测试目标
2. 前置条件：执行测试前需要满足的条件
3. 测试步骤：详细的操作步骤
4. 预期结果：每个步骤的预期结果
5. 用例等级：P0(核心功能)、P1(重要功能)、P2(一般功能)、P3(边缘功能)

请确保测试步骤清晰、可执行，预期结果明确、可验证。
如果可能，请以表格形式展示测试用例，便于阅读和理解。"""
        
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        
        # 加载历史消息（最近10条）
        history_messages = await aitestrebortMessage.filter(
            conversation=conversation
        ).order_by('create_time').limit(10)
        
        for msg in history_messages[:-1]:  # 排除刚创建的用户消息
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'assistant':
                messages.append(AIMessage(content=msg.content))
        
        # 添加当前用户消息
        messages.append(HumanMessage(content=message_data.content))
        
        # 调用真实的 LLM 服务
        try:
            logger.info(f"Calling LLM with {len(messages)} messages")
            ai_response = await llm.ainvoke(messages)
            ai_content = ai_response.content
            logger.info(f"LLM response received, length: {len(ai_content)}")
            
        except Exception as e:
            logger.error(f"LLM call failed: {e}", exc_info=True)
            ai_content = f"抱歉，AI服务暂时不可用。错误信息：{str(e)}"
        
        # 保存 AI 回复
        ai_message = await aitestrebortMessage.create(
            conversation=conversation,
            role="assistant",
            content=ai_content,
            message_type="text",
            metadata={}
        )
        
        # 更新对话时间
        await conversation.save()
        
        # 返回消息数组
        messages_result = [
            {
                "id": user_message.id,
                "role": user_message.role,
                "content": user_message.content,
                "message_type": user_message.message_type,
                "metadata": user_message.metadata,
                "tokens_used": user_message.tokens_used,
                "create_time": user_message.create_time
            },
            {
                "id": ai_message.id,
                "role": ai_message.role,
                "content": ai_message.content,
                "message_type": ai_message.message_type,
                "metadata": ai_message.metadata,
                "tokens_used": ai_message.tokens_used,
                "create_time": ai_message.create_time
            }
        ]
        
        return request.app.post_success(data=messages_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目或对话不存在")
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}", exc_info=True)
        return request.app.error(msg=f"发送消息失败: {str(e)}")


async def delete_conversation(request: Request, project_id: int, conversation_id: int):
    """删除对话"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        conversation = await aitestrebortConversation.get(
            id=conversation_id, project=project, user_id=request.state.user.id
        )
        
        await conversation.delete()
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目或对话不存在")
    except Exception as e:
        return request.app.error(msg=f"删除对话失败: {str(e)}")


# 项目统计信息
async def get_project_statistics(request: Request, project_id: int):
    """获取项目统计信息"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 统计各种数据
        testcase_count = await project.testcases.all().count()
        module_count = await project.testcase_modules.all().count()
        suite_count = await project.test_suites.all().count()
        member_count = await project.members.all().count()
        
        # 通过测试用例统计自动化脚本数量
        from app.models.aitestrebort.automation import aitestrebortAutomationScript
        automation_script_count = await aitestrebortAutomationScript.filter(
            test_case__project_id=project_id
        ).count()
        
        llm_config_count = await project.llm_configs.all().count()
        
        # MCP 配置是用户级别的，不是项目级别的，所以不统计
        # mcp_config_count = await project.mcp_configs.all().count()
        
        # API 密钥也是用户级别的，不是项目级别的，所以不统计
        # api_key_count = await project.api_keys.all().count()
        
        # 执行统计
        execution_count = 0
        for suite in await project.test_suites.all():
            execution_count += await suite.executions.all().count()
        
        stats = {
            "testcase_count": testcase_count,
            "module_count": module_count,
            "suite_count": suite_count,
            "member_count": member_count,
            "automation_script_count": automation_script_count,
            "execution_count": execution_count,
            "llm_config_count": llm_config_count
        }
        
        return request.app.get_success(data=stats)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取项目统计失败: {str(e)}")


async def get_project_activity(request: Request, project_id: int):
    """获取项目最近活动"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取最近的活动记录
        activities = []
        
        # 获取最近创建的测试用例（最多5个）
        recent_testcases = await project.testcases.all().order_by('-create_time').limit(5)
        for testcase in recent_testcases:
            activities.append({
                "id": f"testcase_{testcase.id}",
                "type": "testcase",
                "title": "创建了测试用例",
                "description": testcase.name,
                "user": "系统用户",  # TODO: 从用户表获取真实用户名
                "time": testcase.create_time.isoformat()
            })
        
        # 获取最近创建的自动化脚本（最多3个）
        from app.models.aitestrebort.automation import aitestrebortAutomationScript
        recent_scripts = await aitestrebortAutomationScript.filter(
            test_case__project_id=project_id
        ).order_by('-create_time').limit(3)
        for script in recent_scripts:
            activities.append({
                "id": f"script_{script.id}",
                "type": "automation",
                "title": "生成了自动化脚本",
                "description": script.name,
                "user": "系统用户",
                "time": script.create_time.isoformat()
            })
        
        # 获取最近创建的测试套件（最多3个）
        recent_suites = await project.test_suites.all().order_by('-create_time').limit(3)
        for suite in recent_suites:
            activities.append({
                "id": f"suite_{suite.id}",
                "type": "suite",
                "title": "创建了测试套件",
                "description": suite.name,
                "user": "系统用户",
                "time": suite.create_time.isoformat()
            })
        
        # 按时间排序，取最近的10个活动
        activities.sort(key=lambda x: x["time"], reverse=True)
        activities = activities[:10]
        
        return request.app.get_success(data=activities)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        return request.app.error(msg=f"获取项目活动失败: {str(e)}")


# 移除项目成员
async def remove_project_member(request: Request, project_id: int, member_id: int):
    """移除项目成员"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限（只有管理员可以移除成员）
        current_member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not current_member:
            return request.app.forbidden(msg="无权限移除项目成员")
        
        member = await aitestrebortProjectMember.get(id=member_id, project=project)
        
        # 不能移除项目拥有者
        if member.role == "owner":
            return request.app.fail(msg="不能移除项目拥有者")
        
        await member.delete()
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="项目或成员不存在")
    except Exception as e:
        return request.app.error(msg=f"移除项目成员失败: {str(e)}")


# 提示词管理
async def get_prompts(
    request: Request, 
    project_id: int,
    search: Optional[str] = "",
    prompt_type: Optional[str] = "",
    is_active: Optional[bool] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = 20
):
    """获取提示词列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return {
                "status": 403,
                "message": "无权限访问此项目",
                "data": None
            }
        
        # 暂时返回模拟数据，避免数据库依赖问题
        mock_prompts = [
            {
                "id": 1,
                "name": "测试用例生成提示词",
                "description": "用于生成高质量测试用例的专业提示词",
                "prompt_type": "test_case_generation",
                "is_default": True,
                "is_active": True,
                "project_id": None,
                "create_time": "2024-01-01T10:00:00"
            },
            {
                "id": 2,
                "name": "需求分析提示词",
                "description": "用于分析需求完整性和一致性的提示词",
                "prompt_type": "requirement_analysis",
                "is_default": False,
                "is_active": True,
                "project_id": None,
                "create_time": "2024-01-01T10:00:00"
            },
            {
                "id": 3,
                "name": "边界测试提示词",
                "description": "专门用于生成边界条件测试用例的提示词",
                "prompt_type": "boundary_testing",
                "is_default": False,
                "is_active": True,
                "project_id": None,
                "create_time": "2024-01-01T10:00:00"
            }
        ]
        
        # 应用搜索过滤
        if search:
            mock_prompts = [p for p in mock_prompts if search.lower() in p['name'].lower() or search.lower() in p['description'].lower()]
        
        # 应用类型过滤
        if prompt_type:
            mock_prompts = [p for p in mock_prompts if p['prompt_type'] == prompt_type]
        
        # 应用状态过滤
        if is_active is not None:
            mock_prompts = [p for p in mock_prompts if p['is_active'] == is_active]
        
        # 分页处理
        total = len(mock_prompts)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_prompts = mock_prompts[start:end]
        
        return {
            "status": 200,
            "message": "获取提示词列表成功",
            "data": {
                "prompts": paginated_prompts,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
        
    except DoesNotExist:
        return {
            "status": 404,
            "message": "项目不存在",
            "data": None
        }
    except Exception as e:
        logger.error(f"获取提示词列表失败: {str(e)}")
        return {
            "status": 500,
            "message": f"获取提示词列表失败: {str(e)}",
            "data": None
        }


# 知识库管理（代理到知识库服务）
async def get_knowledge_bases(
    request: Request, 
    project_id: int,
    search: Optional[str] = "",
    is_active: Optional[bool] = None,
    page: Optional[int] = 1,
    page_size: Optional[int] = 20
):
    """获取知识库列表"""
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        if not await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).exists():
            return {
                "status": 403,
                "message": "无权限访问此项目",
                "data": None
            }
        
        # 暂时返回模拟数据，避免数据库依赖问题
        mock_knowledge_bases = [
            {
                "id": "kb-001",
                "name": "产品需求知识库",
                "description": "包含产品需求文档和业务规则",
                "is_active": True,
                "document_count": 15,
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00"
            },
            {
                "id": "kb-002",
                "name": "技术规范知识库",
                "description": "包含技术规范和API文档",
                "is_active": True,
                "document_count": 8,
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00"
            },
            {
                "id": "kb-003",
                "name": "测试用例库",
                "description": "历史测试用例和最佳实践",
                "is_active": True,
                "document_count": 25,
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00"
            }
        ]
        
        # 应用搜索过滤
        if search:
            mock_knowledge_bases = [kb for kb in mock_knowledge_bases if search.lower() in kb['name'].lower() or search.lower() in kb['description'].lower()]
        
        # 应用状态过滤
        if is_active is not None:
            mock_knowledge_bases = [kb for kb in mock_knowledge_bases if kb['is_active'] == is_active]
        
        # 分页处理
        total = len(mock_knowledge_bases)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_kbs = mock_knowledge_bases[start:end]
        
        return {
            "status": 200,
            "message": "获取知识库列表成功",
            "data": {
                "knowledge_bases": paginated_kbs,
                "total": total,
                "page": page,
                "page_size": page_size
            }
        }
        
    except DoesNotExist:
        return {
            "status": 404,
            "message": "项目不存在",
            "data": None
        }
    except Exception as e:
        logger.error(f"获取知识库列表失败: {str(e)}")
        return {
            "status": 500,
            "message": f"获取知识库列表失败: {str(e)}",
            "data": None
        }