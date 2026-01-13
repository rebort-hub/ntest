"""
aitestrebort MCP配置真实连接测试
"""
import logging
from typing import Optional
from fastapi import Request
from tortoise.exceptions import DoesNotExist

from app.models.aitestrebort import aitestrebortMCPConfig, aitestrebortProjectMember, aitestrebortProject

logger = logging.getLogger(__name__)


async def test_mcp_connection(request: Request, project_id: int, config_id: int):
    """
    测试MCP配置连接 - 完全对标旧架构的RemoteMCPConfigPingView
    
    注意：虽然路由中有project_id，但实际验证的是用户对MCP配置的权限
    这是为了保持前端兼容性，实际逻辑是用户级的
    """
    try:
        # 1. 验证用户权限（对标旧架构的权限检查）
        # 旧架构: has_perm('mcp_tools.view_remotemcpconfig')
        # 这里我们检查用户是否有项目访问权限作为基础权限验证
        try:
            project = await aitestrebortProject.get(id=project_id)
            member = await aitestrebortProjectMember.filter(
                project=project, user_id=request.state.user.id
            ).first()
            if not member:
                return request.app.forbidden(msg="无权限访问此项目")
        except DoesNotExist:
            return request.app.fail(msg="项目不存在")
        
        # 2. 获取用户的MCP配置（用户级查询，对标旧架构）
        # 旧架构: RemoteMCPConfig.objects.get(id=config_id, owner=request.user)
        config = await aitestrebortMCPConfig.get(id=config_id, user_id=request.state.user.id)
        
        # 3. 验证URL格式
        target_mcp_url = config.url
        logger.info(f"Testing MCP config {config_id}: {config.name}")
        logger.info(f"Target MCP URL: {target_mcp_url}")
        
        if not target_mcp_url or not target_mcp_url.strip():
            return request.app.get_success(data={
                "status": "error",
                "url": target_mcp_url,
                "message": "MCP服务器URL不能为空"
            })
        
        if not (target_mcp_url.startswith('http://') or target_mcp_url.startswith('https://')):
            return request.app.get_success(data={
                "status": "error", 
                "url": target_mcp_url,
                "message": "MCP服务器URL格式无效，必须以http://或https://开头"
            })
        
        # 4. 外部API密钥验证（新增，处理外部MCP服务的认证）
        # 检查MCP配置的headers中是否包含外部API密钥
        external_auth_valid = True
        auth_message = ""
        
        if config.headers and isinstance(config.headers, dict):
            # 检查常见的外部API密钥格式
            auth_headers = config.headers
            if 'Authorization' in auth_headers:
                auth_value = auth_headers['Authorization']
                if auth_value.startswith('Bearer ') and len(auth_value) > 7:
                    logger.info("Found Bearer token in MCP config headers")
                elif auth_value.startswith('API-Key ') and len(auth_value) > 8:
                    logger.info("Found API-Key in MCP config headers")
                else:
                    external_auth_valid = False
                    auth_message = "外部API密钥格式无效，请检查Authorization头格式"
            elif 'X-API-Key' in auth_headers or 'x-api-key' in auth_headers:
                api_key = auth_headers.get('X-API-Key') or auth_headers.get('x-api-key')
                if not api_key or len(api_key.strip()) < 10:
                    external_auth_valid = False
                    auth_message = "外部API密钥无效，请检查X-API-Key头"
                else:
                    logger.info("Found X-API-Key in MCP config headers")
        
        # 5. 用户API密钥验证（确保用户配置的密钥与MCP服务实际使用的密钥一致）
        api_key_validation_result = await validate_user_mcp_api_key_match(request.state.user.id, config)
        if not api_key_validation_result["valid"]:
            return request.app.get_success(data={
                "status": "error",
                "url": target_mcp_url,
                "message": api_key_validation_result["message"]
            })
        
        # 如果外部认证无效，返回错误
        if not external_auth_valid:
            return request.app.get_success(data={
                "status": "error",
                "url": target_mcp_url,
                "message": f"外部服务认证失败：{auth_message}"
            })
        
        try:
            # 6. 真实连接测试（完全对标旧架构）
            from langchain_mcp_adapters.client import MultiServerMCPClient
            
            # 准备配置（对标旧架构的client_config）
            server_config_key = config.name or "target_server"
            
            client_config = {
                server_config_key: {
                    "url": target_mcp_url,
                    "transport": config.transport.replace('-', '_'),
                }
            }
            
            # 传递认证头（对标旧架构的headers传递）
            if config.headers and isinstance(config.headers, dict) and config.headers:
                client_config[server_config_key]["headers"] = config.headers
                logger.info(f"Using external authentication headers for MCP connection")
            
            logger.info(f"Connecting to MCP server with config: {client_config}")
            
            # 创建MCP客户端并测试连接
            mcp_client = MultiServerMCPClient(client_config)
            tools_list = await mcp_client.get_tools()
            tools_count = len(tools_list)
            
            logger.info(f"Successfully connected to MCP server and retrieved {tools_count} tools")
            
            return request.app.get_success(data={
                "status": "online",
                "url": target_mcp_url,
                "tools_count": tools_count,
                "tools": [tool.name for tool in tools_list if hasattr(tool, 'name')],
                "config_name": config.name,
                "transport": config.transport,
                "message": f"MCP服务器在线，成功获取 {tools_count} 个工具"
            })
            
        except ImportError as e:
            logger.error(f"langchain-mcp-adapters library not installed: {e}")
            return request.app.get_success(data={
                "status": "error",
                "url": target_mcp_url,
                "message": "服务器配置错误：langchain-mcp-adapters库未安装，请运行 pip install langchain-mcp-adapters"
            })
            
        except Exception as e:
            logger.error(f"Error connecting to MCP server: {e}", exc_info=True)
            
            # 提取更友好的错误信息
            error_type = type(e).__name__
            error_detail = str(e)
            
            # 处理常见错误类型
            if "ExceptionGroup" in error_type:
                error_message = "连接MCP服务器失败：网络连接错误或服务器不可达"
            elif "timeout" in error_detail.lower():
                error_message = "连接MCP服务器失败：连接超时"
            elif "connection" in error_detail.lower():
                error_message = "连接MCP服务器失败：无法建立连接"
            elif "refused" in error_detail.lower():
                error_message = "连接MCP服务器失败：连接被拒绝"
            elif "unauthorized" in error_detail.lower() or "401" in error_detail:
                error_message = "连接MCP服务器失败：外部API密钥认证失败"
            elif "forbidden" in error_detail.lower() or "403" in error_detail:
                error_message = "连接MCP服务器失败：外部API密钥权限不足"
            else:
                error_message = f"连接MCP服务器失败：{error_detail}"
            
            # 返回失败状态，但HTTP状态码为200
            return request.app.get_success(data={
                "status": "offline",
                "url": target_mcp_url,
                "error_type": error_type,
                "error_detail": error_detail,
                "message": error_message
            })
        
    except DoesNotExist:
        return request.app.fail(msg="MCP配置不存在或无权限访问")
    except Exception as e:
        logger.error(f"Test MCP connection failed: {str(e)}", exc_info=True)
        return request.app.error(msg=f"测试MCP连接失败: {str(e)}")


async def validate_user_mcp_api_key_match(user_id: int, mcp_config) -> dict:
    """
    验证用户配置的API密钥是否与MCP服务实际使用的密钥匹配
    
    这是一个关键的安全验证步骤，确保：
    1. 用户已配置API密钥
    2. 用户配置的密钥与MCP服务器实际使用的密钥一致
    3. 防止用户使用错误或无效的密钥绕过认证
    
    Args:
        user_id: 用户ID
        mcp_config: MCP配置对象
        
    Returns:
        dict: {"valid": bool, "message": str, "matched_key": str}
    """
    try:
        from app.models.aitestrebort import aitestrebortAPIKey
        import os
        
        logger.info(f"Validating API key match for user {user_id} and MCP config {mcp_config.id}")
        
        # 1. 获取MCP服务实际使用的密钥
        # 从环境变量或配置中获取MCP服务器的实际API密钥
        actual_mcp_api_key = os.getenv('N-Tester_API_KEY', 'N-Tester-default-mcp-key-2025')
        logger.info(f"MCP server actual API key: {actual_mcp_api_key[:10]}...")
        
        # 2. 查找用户的所有激活API密钥
        user_api_keys = await aitestrebortAPIKey.filter(
            user_id=user_id,
            is_active=True
        ).all()
        
        logger.info(f"Found {len(user_api_keys)} active API keys for user {user_id}")
        
        if not user_api_keys:
            return {
                "valid": False,
                "message": "请先在API密钥管理中配置您的API密钥，然后再测试MCP连接",
                "matched_key": None
            }
        
        # 3. 检查用户配置的密钥中是否有与MCP服务实际密钥匹配的
        matched_keys = []
        for key in user_api_keys:
            if key.key_value and key.key_value.strip() == actual_mcp_api_key:
                matched_keys.append(key)
                logger.info(f"Found matching API key: {key.name} (service: {key.service})")
        
        if matched_keys:
            matched_key = matched_keys[0]  # 使用第一个匹配的密钥
            logger.info(f"User {user_id} has valid matching API key: {matched_key.name}")
            return {
                "valid": True,
                "message": f"API密钥验证成功，使用密钥: {matched_key.name}",
                "matched_key": matched_key.key_value
            }
        
        # 4. 如果没有匹配的密钥，检查用户配置了哪些密钥（用于调试）
        user_key_info = []
        for key in user_api_keys:
            if key.key_value and len(key.key_value.strip()) >= 10:
                user_key_info.append(f"{key.name}({key.service}): {key.key_value[:10]}...")
        
        logger.warning(f"User {user_id} has API keys but none match MCP server key")
        logger.warning(f"User keys: {user_key_info}")
        logger.warning(f"Expected key: {actual_mcp_api_key[:10]}...")
        
        return {
            "valid": False,
            "message": f"API密钥不匹配：您配置的API密钥与MCP服务器使用的密钥不一致。请确保在API密钥管理中配置正确的密钥值: {actual_mcp_api_key}",
            "matched_key": None
        }
        
    except Exception as e:
        logger.error(f"Error validating API key match for user {user_id}: {e}")
        return {
            "valid": False,
            "message": f"API密钥验证失败: {str(e)}",
            "matched_key": None
        }


async def validate_user_has_api_key(user_id: int) -> bool:
    """
    验证用户是否配置了API密钥（用于MCP连接）
    
    Args:
        user_id: 用户ID
        
    Returns:
        bool: 用户是否配置了有效的API密钥
    """
    try:
        from app.models.aitestrebort import aitestrebortAPIKey
        
        logger.info(f"Checking if user {user_id} has configured API keys")
        
        # 查找用户的所有激活API密钥
        api_keys = await aitestrebortAPIKey.filter(
            user_id=user_id,
            is_active=True
        ).all()
        
        logger.info(f"Found {len(api_keys)} active API keys for user {user_id}")
        
        if not api_keys:
            logger.warning(f"No active API keys found for user {user_id}")
            return False
        
        # 检查是否有有效的密钥值（非空且长度合理）
        valid_keys = []
        for key in api_keys:
            if key.key_value and len(key.key_value.strip()) >= 10:  # 基本长度验证
                valid_keys.append(key)
                logger.info(f"Valid API key found: {key.name} (service: {key.service})")
        
        if valid_keys:
            logger.info(f"User {user_id} has {len(valid_keys)} valid API keys configured")
            return True
        else:
            logger.warning(f"User {user_id} has API keys but none are valid (too short or empty)")
            return False
        
    except Exception as e:
        logger.error(f"Error checking API keys for user {user_id}: {e}")
        return False


# 注意：移除了validate_mcp_api_key函数，因为我们不再限制特定的密钥格式
# MCP服务器支持各种类型的API密钥，应该由用户自由配置
