# -*- coding: utf-8 -*-
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class SamlConfigBase(BaseModel):
    """SAML配置基础模型"""
    name: str = Field(..., description="配置名称")
    entity_id: str = Field(..., description="SP Entity ID")
    acs_url: str = Field(..., description="断言消费服务URL")
    sls_url: Optional[str] = Field(None, description="单点登出URL")
    
    # IdP配置
    idp_entity_id: str = Field(..., description="IdP Entity ID")
    idp_sso_url: str = Field(..., description="IdP SSO URL")
    idp_sls_url: Optional[str] = Field(None, description="IdP SLS URL")
    idp_x509_cert: str = Field(..., description="IdP X.509证书")
    
    # SP配置
    sp_x509_cert: Optional[str] = Field(None, description="SP X.509证书")
    sp_private_key: Optional[str] = Field(None, description="SP私钥")
    
    # 属性映射
    name_id_format: str = Field(
        default="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        description="NameID格式"
    )
    attribute_mapping: Dict[str, str] = Field(
        default={
            "username": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
            "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
            "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
            "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"
        },
        description="属性映射配置"
    )
    
    # 安全配置
    want_assertions_signed: bool = Field(default=True, description="要求断言签名")
    want_name_id_encrypted: bool = Field(default=False, description="要求NameID加密")
    authn_requests_signed: bool = Field(default=False, description="认证请求签名")
    logout_requests_signed: bool = Field(default=False, description="登出请求签名")
    
    # 其他配置
    is_default: bool = Field(default=False, description="是否为默认配置")
    description: Optional[str] = Field(None, description="配置描述")


class CreateSamlConfigForm(SamlConfigBase):
    """创建SAML配置表单"""
    pass


class UpdateSamlConfigForm(SamlConfigBase):
    """更新SAML配置表单"""
    id: int = Field(..., description="配置ID")


class SamlConfigResponse(SamlConfigBase):
    """SAML配置响应模型"""
    id: int
    status: str
    create_time: str
    update_time: str


class SamlLoginRequest(BaseModel):
    """SAML登录请求"""
    config_id: Optional[int] = Field(None, description="SAML配置ID，不传则使用默认配置")
    relay_state: Optional[str] = Field(None, description="登录成功后的重定向地址")


class SamlLogoutRequest(BaseModel):
    """SAML登出请求"""
    config_id: Optional[int] = Field(None, description="SAML配置ID，不传则使用默认配置")


class SamlMetadataRequest(BaseModel):
    """SAML元数据请求"""
    config_id: Optional[int] = Field(None, description="SAML配置ID，不传则使用默认配置")


class SamlTestConnectionForm(BaseModel):
    """SAML连接测试表单"""
    idp_sso_url: str = Field(..., description="IdP SSO URL")
    idp_x509_cert: str = Field(..., description="IdP X.509证书")
    entity_id: str = Field(..., description="SP Entity ID")