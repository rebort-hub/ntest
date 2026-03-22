# -*- coding: utf-8 -*-
from fastapi import Request, HTTPException
from ...models.config.model_factory import SamlConfig
from ...schemas.system import saml as schema


async def get_saml_config_list(request: Request):
    """获取SAML配置列表"""
    configs = await SamlConfig.all().order_by("-create_time")
    config_list = []
    
    for config in configs:
        config_data = dict(config)
        # 隐藏敏感信息
        config_data.pop("sp_private_key", None)
        config_list.append(config_data)
    
    return request.app.get_success(data=config_list)


async def create_saml_config(request: Request, form: schema.CreateSamlConfigForm):
    """创建SAML配置"""
    # 检查配置名称是否已存在
    existing_config = await SamlConfig.filter(name=form.name).first()
    if existing_config:
        raise HTTPException(status_code=400, detail="配置名称已存在")
    
    # 如果设置为默认配置，需要将其他配置的默认状态取消
    if form.is_default:
        await SamlConfig.filter(is_default=True).update(is_default=False)
    
    config_data = form.dict()
    config = await SamlConfig.model_create(config_data)
    
    return request.app.post_success(data={"id": config.id, "message": "SAML配置创建成功"})


async def update_saml_config(request: Request, form: schema.UpdateSamlConfigForm):
    """更新SAML配置"""
    config = await SamlConfig.filter(id=form.id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 检查配置名称是否与其他配置冲突
    existing_config = await SamlConfig.filter(name=form.name, id__not=form.id).first()
    if existing_config:
        raise HTTPException(status_code=400, detail="配置名称已存在")
    
    # 如果设置为默认配置，需要将其他配置的默认状态取消
    if form.is_default:
        await SamlConfig.filter(is_default=True, id__not=form.id).update(is_default=False)
    
    update_data = form.dict(exclude={"id"})
    await config.model_update(update_data)
    
    return request.app.put_success(message="SAML配置更新成功")


async def delete_saml_config(request: Request, config_id: int):
    """删除SAML配置"""
    config = await SamlConfig.filter(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    await config.delete()
    return request.app.delete_success(message="SAML配置删除成功")


async def get_saml_config_detail(request: Request, config_id: int):
    """获取SAML配置详情"""
    config = await SamlConfig.filter(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    config_data = dict(config)
    return request.app.get_success(data=config_data)


async def toggle_saml_config_status(request: Request, config_id: int):
    """切换SAML配置状态"""
    config = await SamlConfig.filter(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    new_status = "disable" if config.status == "enable" else "enable"
    await config.model_update({"status": new_status})
    
    return request.app.put_success(data={"status": new_status}, message=f"配置已{'启用' if new_status == 'enable' else '禁用'}")


async def set_default_saml_config(request: Request, config_id: int):
    """设置默认SAML配置"""
    config = await SamlConfig.filter(id=config_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="配置不存在")
    
    # 取消其他配置的默认状态
    await SamlConfig.filter(is_default=True).update(is_default=False)
    
    # 设置当前配置为默认
    await config.model_update({"is_default": True})
    
    return request.app.put_success(message="默认配置设置成功")