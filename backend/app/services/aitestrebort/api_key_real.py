"""
aitestrebort API密钥管理 
"""
import secrets
import logging
from typing import Optional
from datetime import datetime
from fastapi import Request
from tortoise.exceptions import DoesNotExist

from app.models.aitestrebort import aitestrebortAPIKey, aitestrebortProjectMember, aitestrebortProject

logger = logging.getLogger(__name__)


def generate_api_key() -> str:
    """
    生成安全的API密钥
    
    Returns:
        str: 生成的API密钥
    """
    return secrets.token_urlsafe(32)  # 生成32字节（约43字符）的URL安全字符串


async def create_api_key_with_generation(
    request: Request,
    project_id: int,
    name: str,
    service_type: str,
    description: Optional[str] = None,
    is_active: bool = True
):
    """
    创建API密钥（自动生成密钥值）
    
    Args:
        project_id: 项目ID
        name: 密钥名称
        service_type: 服务类型
        description: 描述
        is_active: 是否激活
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限添加API密钥")
        
        # 检查名称是否已存在
        if await aitestrebortAPIKey.filter(project=project, name=name).exists():
            return request.app.fail(msg="API密钥名称已存在")
        
        # 生成API密钥
        api_key_value = generate_api_key()
        logger.info(f"Generated new API key for project {project_id}: {api_key_value[:10]}...")
        
        # 创建API密钥记录
        key = await aitestrebortAPIKey.create(
            project=project,
            name=name,
            service=service_type,
            key_value=api_key_value,
            description=description,
            is_active=is_active,
            creator_id=request.state.user.id,
            create_user=request.state.user.id,
            update_user=request.state.user.id
        )
        
        key_result = {
            "id": key.id,
            "name": key.name,
            "service_type": key.service,
            "api_key": key.key_value,  # 只在创建时返回完整密钥
            "description": key.description,
            "is_active": key.is_active,
            "created_at": key.create_time,
            "message": "API密钥创建成功，请妥善保管密钥，此密钥只显示一次"
        }
        
        return request.app.post_success(data=key_result)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        logger.error(f"Create API key failed: {str(e)}", exc_info=True)
        return request.app.error(msg=f"创建API密钥失败: {str(e)}")


async def validate_api_key(api_key_value: str) -> Optional[dict]:
    """
    验证API密钥
    
    Args:
        api_key_value: API密钥值
        
    Returns:
        dict: 包含用户信息的字典，如果密钥无效则返回None
    """
    try:
        # 查询API密钥
        key = await aitestrebortAPIKey.filter(key_value=api_key_value).first()
        
        if not key:
            logger.warning(f"API key not found: {api_key_value[:10]}...")
            return None
        
        # 检查密钥是否激活
        if not key.is_active:
            logger.warning(f"API key is inactive: {api_key_value[:10]}...")
            return None
        
        # 检查密钥是否过期
        if key.expires_at and key.expires_at < datetime.now():
            logger.warning(f"API key is expired: {api_key_value[:10]}...")
            return None
        
        logger.info(f"API key validated successfully: {api_key_value[:10]}...")
        
        return {
            "key_id": key.id,
            "key_name": key.name,
            "service_type": key.service,
            "creator_id": key.creator_id,
            "is_valid": True
        }
        
    except Exception as e:
        logger.error(f"Error validating API key: {e}")
        return None


async def test_api_key(request: Request, project_id: int, key_id: int):
    """
    测试API密钥是否有效
    
    Args:
        project_id: 项目ID
        key_id: 密钥ID
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取API密钥
        key = await aitestrebortAPIKey.get(id=key_id, project=project)
        
        # 验证密钥
        validation_result = await validate_api_key(key.key_value)
        
        if validation_result:
            return request.app.get_success(data={
                "status": "valid",
                "key_name": key.name,
                "service_type": key.service,
                "is_active": key.is_active,
                "created_at": key.create_time,
                "message": "API密钥有效"
            })
        else:
            return request.app.fail(msg="API密钥无效或已过期")
        
    except DoesNotExist:
        return request.app.fail(msg="项目或API密钥不存在")
    except Exception as e:
        logger.error(f"Test API key failed: {str(e)}", exc_info=True)
        return request.app.error(msg=f"测试API密钥失败: {str(e)}")


async def regenerate_api_key(request: Request, project_id: int, key_id: int):
    """
    重新生成API密钥
    
    Args:
        project_id: 项目ID
        key_id: 密钥ID
    """
    try:
        project = await aitestrebortProject.get(id=project_id)
        
        # 检查权限
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id, role__in=["owner", "admin"]
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限重新生成API密钥")
        
        # 获取API密钥
        key = await aitestrebortAPIKey.get(id=key_id, project=project)
        
        # 生成新的API密钥
        new_api_key_value = generate_api_key()
        logger.info(f"Regenerated API key for {key.name}: {new_api_key_value[:10]}...")
        
        # 更新密钥值
        key.key_value = new_api_key_value
        key.update_user = request.state.user.id
        await key.save()
        
        return request.app.put_success(data={
            "id": key.id,
            "name": key.name,
            "service_type": key.service,
            "api_key": new_api_key_value,  # 返回新密钥
            "description": key.description,
            "is_active": key.is_active,
            "created_at": key.create_time,
            "message": "API密钥重新生成成功，请妥善保管新密钥，此密钥只显示一次"
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目或API密钥不存在")
    except Exception as e:
        logger.error(f"Regenerate API key failed: {str(e)}", exc_info=True)
        return request.app.error(msg=f"重新生成API密钥失败: {str(e)}")
