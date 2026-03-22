# -*- coding: utf-8 -*-
from fastapi import Request, Depends, Form, HTTPException, Path
from fastapi.responses import Response, RedirectResponse

from ..base_view import APIRouter
from ...services.system import saml as saml_service
from ...schemas.system import saml as schema
from ...models.config.model_factory import SamlConfig

saml_router = APIRouter()


async def saml_login(
    request: Request,
    config_id: int = None,
    relay_state: str = None
):
    """发起SAML登录"""
    result = await saml_service.saml_login(request, config_id)
    
    # 如果有relay_state，添加到重定向URL中
    if relay_state:
        separator = "&" if "?" in result["redirect_url"] else "?"
        result["redirect_url"] += f"{separator}RelayState={relay_state}"
    
    return result


async def saml_acs(request: Request, config_id: int = None):
    """处理SAML断言消费服务(ACS)"""
    return await saml_service.saml_acs(request, config_id)


async def saml_logout(request: Request, config_id: int = None):
    """SAML单点登出"""
    return await saml_service.saml_logout(request, config_id)


async def saml_sls(request: Request, config_id: int = None):
    """处理SAML单点登出服务(SLS)"""
    return await saml_service.saml_sls(request, config_id)


async def saml_metadata(request: Request, config_id: int = None):
    """获取SAML元数据"""
    result = await saml_service.get_saml_metadata(request, config_id)
    return Response(
        content=result["metadata"],
        media_type=result["content_type"]
    )


# SAML配置管理函数
async def get_saml_config_list(request: Request):
    """获取SAML配置列表"""
    configs = await SamlConfig.all().values()
    return request.app.get_success(data=configs)


async def create_saml_config(request: Request, form: schema.CreateSamlConfigForm):
    """创建SAML配置"""
    # 如果设置为默认配置，需要将其他配置的默认状态取消
    if form.is_default:
        await SamlConfig.filter(is_default=True).update(is_default=False)
    
    config_data = form.dict()
    config = await SamlConfig.model_create(config_data)
    return request.app.post_success(data={"id": config.id})


async def update_saml_config(request: Request, form: schema.UpdateSamlConfigForm):
    """更新SAML配置"""
    config = await SamlConfig.filter(id=form.id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 如果设置为默认配置，需要将其他配置的默认状态取消
    if form.is_default:
        await SamlConfig.filter(is_default=True, id__not=form.id).update(is_default=False)
    
    update_data = form.dict(exclude={"id"})
    await config.model_update(update_data)
    return request.app.put_success()


async def test_saml_config(request: Request, form: schema.SamlTestConnectionForm):
    """测试SAML配置连接"""
    try:
        # 1. 基础格式验证
        if not form.idp_x509_cert.strip():
            raise ValueError("IdP证书不能为空")
        
        if not form.idp_sso_url.startswith(("http://", "https://")):
            raise ValueError("IdP SSO URL格式不正确，必须以http://或https://开头")
        
        if not form.entity_id.strip():
            raise ValueError("SP Entity ID不能为空")
        
        # 2. 证书格式验证
        cert_content = form.idp_x509_cert.strip()
        if not (cert_content.startswith("-----BEGIN CERTIFICATE-----") and 
                cert_content.endswith("-----END CERTIFICATE-----")):
            raise ValueError("IdP证书格式不正确，必须包含完整的PEM格式证书")
        
        # 3. 尝试解析证书
        try:
            import base64
            import re
            
            # 提取证书内容（去除头尾和换行）
            cert_lines = cert_content.replace("-----BEGIN CERTIFICATE-----", "")
            cert_lines = cert_lines.replace("-----END CERTIFICATE-----", "")
            cert_lines = re.sub(r'\s+', '', cert_lines)
            
            # 验证base64格式
            base64.b64decode(cert_lines)
            
        except Exception as cert_error:
            raise ValueError(f"证书内容无效: {str(cert_error)}")
        
        # 4. URL可达性测试
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                # 尝试访问IdP SSO URL
                response = await client.get(form.idp_sso_url, follow_redirects=True)
                
                # 检查响应状态
                if response.status_code >= 400:
                    request.app.logger.warning(f"IdP URL返回状态码: {response.status_code}")
                    # 不直接失败，因为有些IdP可能返回特定状态码
                
        except httpx.TimeoutException:
            raise ValueError("IdP SSO URL访问超时，请检查网络连接或URL是否正确")
        except httpx.ConnectError:
            raise ValueError("无法连接到IdP SSO URL，请检查URL是否正确或网络是否可达")
        except Exception as url_error:
            request.app.logger.warning(f"URL测试警告: {str(url_error)}")
            # 不直接失败，记录警告即可
        
        # 5. 尝试创建SAML设置对象进行验证
        try:
            from onelogin.saml2.settings import OneLogin_Saml2_Settings
            
            # 构建最小SAML设置用于验证
            test_settings = {
                "sp": {
                    "entityId": form.entity_id,
                    "assertionConsumerService": {
                        "url": "https://test.com/acs",
                        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                    },
                    "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
                },
                "idp": {
                    "entityId": "https://test-idp.com/metadata",
                    "singleSignOnService": {
                        "url": form.idp_sso_url,
                        "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
                    },
                    "x509cert": cert_content
                }
            }
            
            # 验证设置
            settings = OneLogin_Saml2_Settings(test_settings)
            errors = settings.check_sp_settings(test_settings)
            
            if errors:
                error_msg = f"SAML配置验证失败: {', '.join(errors)}"
                request.app.logger.warning(error_msg)
                # 有错误但不一定致命，记录警告
            
        except Exception as saml_error:
            raise ValueError(f"SAML配置验证失败: {str(saml_error)}")
        
        # 所有验证通过
        return request.app.success("SAML配置验证通过，证书格式正确，URL可访问")
        
    except ValueError as ve:
        # 验证错误，返回具体错误信息
        return request.app.fail(str(ve))
    except Exception as e:
        # 其他未预期的错误
        request.app.logger.error(f"SAML配置测试异常: {str(e)}")
        return request.app.fail(f"测试过程中发生错误: {str(e)}")


async def get_saml_config_detail(request: Request, config_id: int):
    """获取SAML配置详情"""
    config = await SamlConfig.filter(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    config_data = dict(config)
    return request.app.get_success(data=config_data)


async def delete_saml_config(request: Request, config_id: int):
    """删除SAML配置"""
    config = await SamlConfig.filter(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    await config.delete()
    return request.app.delete_success()


async def toggle_saml_config_status(request: Request, config_id: int):
    """切换SAML配置状态"""
    config = await SamlConfig.filter(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    new_status = "disable" if config.status == "enable" else "enable"
    await config.model_update({"status": new_status})
    
    return request.app.put_success(data={"status": new_status})


# 注册SAML认证路由
saml_router.add_get_route("/login", saml_login, auth=False, summary="发起SAML登录")
saml_router.add_post_route("/acs", saml_acs, auth=False, summary="SAML断言消费服务")
saml_router.add_get_route("/logout", saml_logout, summary="SAML单点登出")
saml_router.add_get_route("/sls", saml_sls, auth=False, summary="SAML单点登出服务(GET)")
saml_router.add_post_route("/sls", saml_sls, auth=False, summary="SAML单点登出服务(POST)")
saml_router.add_get_route("/metadata", saml_metadata, auth=False, summary="获取SAML元数据")

# 注册SAML配置管理路由
saml_router.add_get_route("/config/list", get_saml_config_list, summary="获取SAML配置列表")
saml_router.add_post_route("/config", create_saml_config, summary="创建SAML配置")
saml_router.add_put_route("/config", update_saml_config, summary="更新SAML配置")
saml_router.add_post_route("/config/test", test_saml_config, summary="测试SAML配置连接")


async def set_default_saml_config(request: Request, config_id: int):
    """设置默认SAML配置"""
    config = await SamlConfig.filter(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 取消其他配置的默认状态
    await SamlConfig.filter(is_default=True).update(is_default=False)
    
    # 设置当前配置为默认
    await config.model_update({"is_default": True})
    
    # 返回成功响应
    return request.app.put_success(msg="默认配置设置成功")


# 带路径参数的路由
async def get_config_detail_wrapper(request: Request, config_id: int = Path(...)):
    return await get_saml_config_detail(request, config_id)

async def delete_config_wrapper(request: Request, config_id: int = Path(...)):
    return await delete_saml_config(request, config_id)

async def toggle_status_wrapper(request: Request, config_id: int = Path(...)):
    return await toggle_saml_config_status(request, config_id)

async def set_default_wrapper(request: Request, config_id: int = Path(...)):
    return await set_default_saml_config(request, config_id)

# 使用自定义路由方法注册，这样可以控制认证
saml_router.add_get_route("/config/{config_id}", get_config_detail_wrapper, summary="获取SAML配置详情")
saml_router.add_delete_route("/config/{config_id}", delete_config_wrapper, summary="删除SAML配置")
saml_router.add_put_route("/config/{config_id}/status", toggle_status_wrapper, summary="切换SAML配置状态")
saml_router.add_put_route("/config/{config_id}/default", set_default_wrapper, summary="设置默认SAML配置")