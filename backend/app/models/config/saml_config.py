# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields
from app.schemas.enums import DataStatusEnum


class SamlConfig(BaseModel):
    """ SAML配置表 """
    
    name = fields.CharField(50, description="配置名称")
    entity_id = fields.CharField(255, description="SP Entity ID")
    acs_url = fields.CharField(255, description="断言消费服务URL")
    sls_url = fields.CharField(255, null=True, description="单点登出URL")
    
    # IdP配置
    idp_entity_id = fields.CharField(255, description="IdP Entity ID")
    idp_sso_url = fields.CharField(255, description="IdP SSO URL")
    idp_sls_url = fields.CharField(255, null=True, description="IdP SLS URL")
    idp_x509_cert = fields.TextField(description="IdP X.509证书")
    
    # SP配置
    sp_x509_cert = fields.TextField(null=True, description="SP X.509证书")
    sp_private_key = fields.TextField(null=True, description="SP私钥")
    
    # 属性映射
    name_id_format = fields.CharField(100, default="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress", description="NameID格式")
    attribute_mapping = fields.JSONField(default={
        "username": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
        "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
        "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
        "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"
    }, description="属性映射配置")
    
    # 安全配置
    want_assertions_signed = fields.BooleanField(default=True, description="要求断言签名")
    want_name_id_encrypted = fields.BooleanField(default=False, description="要求NameID加密")
    authn_requests_signed = fields.BooleanField(default=False, description="认证请求签名")
    logout_requests_signed = fields.BooleanField(default=False, description="登出请求签名")
    
    # 其他配置
    is_default = fields.BooleanField(default=False, description="是否为默认配置")
    status = fields.CharEnumField(DataStatusEnum, default=DataStatusEnum.ENABLE, description="状态")
    description = fields.TextField(null=True, description="配置描述")
    
    class Meta:
        table = "config_saml"
        table_description = "SAML配置表"
        
    async def get_saml_settings(self):
        """获取python3-saml所需的配置格式"""
        # 构建SP配置
        sp_config = {
            "entityId": self.entity_id,
            "assertionConsumerService": {
                "url": self.acs_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            },
            "NameIDFormat": self.name_id_format,
            "x509cert": self.sp_x509_cert or "",
            "privateKey": self.sp_private_key or ""
        }
        
        # 只有当SLS URL存在时才添加
        if self.sls_url:
            sp_config["singleLogoutService"] = {
                "url": self.sls_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            }
        
        # 构建IdP配置
        idp_config = {
            "entityId": self.idp_entity_id,
            "singleSignOnService": {
                "url": self.idp_sso_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            },
            "x509cert": self.idp_x509_cert
        }
        
        # 只有当IdP SLS URL存在时才添加
        if self.idp_sls_url:
            idp_config["singleLogoutService"] = {
                "url": self.idp_sls_url,
                "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
            }
        
        return {
            "sp": sp_config,
            "idp": idp_config,
            "security": {
                "nameIdEncrypted": self.want_name_id_encrypted,
                "authnRequestsSigned": self.authn_requests_signed,
                "logoutRequestSigned": self.logout_requests_signed,
                "logoutResponseSigned": self.logout_requests_signed,
                "signMetadata": False,
                "wantAssertionsSigned": self.want_assertions_signed,
                "wantNameId": True,
                "wantAssertionsEncrypted": False,
                "wantNameIdEncrypted": self.want_name_id_encrypted,
                "requestedAuthnContext": True,
                "signatureAlgorithm": "http://www.w3.org/2000/09/xmldsig#rsa-sha1",
                "digestAlgorithm": "http://www.w3.org/2000/09/xmldsig#sha1"
            }
        }