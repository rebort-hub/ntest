#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建示例SAML配置
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.models.config.model_factory import SamlConfig
from tortoise import Tortoise
import config


async def create_sample_config():
    """创建示例SAML配置"""
    print("🚀 创建示例SAML配置...")
    
    try:
        # 初始化数据库连接
        await Tortoise.init(config=config.tortoise_orm_conf)
        print("✅ 数据库连接成功")
        
        # Azure AD示例配置
        azure_config = {
            "name": "Azure AD SAML",
            "entity_id": "https://your-domain.com/saml/metadata",
            "acs_url": "https://your-domain.com/api/system/saml/acs",
            "sls_url": "https://your-domain.com/api/system/saml/sls",
            "idp_entity_id": "https://sts.windows.net/your-tenant-id/",
            "idp_sso_url": "https://login.microsoftonline.com/your-tenant-id/saml2",
            "idp_sls_url": "https://login.microsoftonline.com/your-tenant-id/saml2",
            "idp_x509_cert": """-----BEGIN CERTIFICATE-----
MIICmzCCAYMCBgF7zT2+XDANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZtYXN0
ZXIwHhcNMjEwNzE0MDcxNjE0WhcNMzEwNzE0MDcxNzU0WjARMQ8wDQYDVQQDDAZt
YXN0ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC...
（这里应该是你的IdP实际证书内容）
-----END CERTIFICATE-----""",
            "name_id_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
            "attribute_mapping": {
                "username": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
                "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"
            },
            "want_assertions_signed": True,
            "want_name_id_encrypted": False,
            "authn_requests_signed": False,
            "logout_requests_signed": False,
            "is_default": True,
            "description": "Azure AD SAML集成配置示例"
        }
        
        # 检查是否已存在
        existing = await SamlConfig.filter(name="Azure AD SAML").first()
        if existing:
            print("⚠️  Azure AD SAML配置已存在，跳过创建")
        else:
            config_obj = await SamlConfig.model_create(azure_config)
            print(f"✅ Azure AD SAML配置创建成功，ID: {config_obj.id}")
        
        # ADFS示例配置
        adfs_config = {
            "name": "ADFS SAML",
            "entity_id": "https://your-domain.com/saml/metadata",
            "acs_url": "https://your-domain.com/api/system/saml/acs",
            "sls_url": "https://your-domain.com/api/system/saml/sls",
            "idp_entity_id": "http://your-adfs-server.com/adfs/services/trust",
            "idp_sso_url": "https://your-adfs-server.com/adfs/ls/",
            "idp_sls_url": "https://your-adfs-server.com/adfs/ls/",
            "idp_x509_cert": """-----BEGIN CERTIFICATE-----
MIICmzCCAYMCBgF7zT2+XDANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZtYXN0
ZXIwHhcNMjEwNzE0MDcxNjE0WhcNMzEwNzE0MDcxNzU0WjARMQ8wDQYDVQQDDAZt
YXN0ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC...
（这里应该是你的ADFS实际证书内容）
-----END CERTIFICATE-----""",
            "name_id_format": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
            "attribute_mapping": {
                "username": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
                "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
                "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
                "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"
            },
            "want_assertions_signed": True,
            "want_name_id_encrypted": False,
            "authn_requests_signed": False,
            "logout_requests_signed": False,
            "is_default": False,
            "description": "ADFS SAML集成配置示例"
        }
        
        # 检查是否已存在
        existing = await SamlConfig.filter(name="ADFS SAML").first()
        if existing:
            print("⚠️  ADFS SAML配置已存在，跳过创建")
        else:
            config_obj = await SamlConfig.model_create(adfs_config)
            print(f"✅ ADFS SAML配置创建成功，ID: {config_obj.id}")
        
        print("\n🎉 示例配置创建完成！")
        print("\n📋 配置说明:")
        print("   1. 请将证书内容替换为你的IdP实际证书")
        print("   2. 请将URL中的域名替换为你的实际域名")
        print("   3. 请将tenant-id替换为你的实际租户ID")
        print("   4. 可以通过API或前端界面修改配置")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 关闭数据库连接
        await Tortoise.close_connections()


async def main():
    """主函数"""
    print("=" * 60)
    print("🔧 SAML配置示例创建工具")
    print("=" * 60)
    
    result = await create_sample_config()
    
    print("\n" + "=" * 60)
    if result:
        print("🎉 示例配置创建成功！")
        print("\n📋 下一步操作:")
        print("   1. 访问 http://localhost:8018/docs")
        print("   2. 使用 GET /api/system/saml/config/list 查看配置")
        print("   3. 使用 PUT /api/system/saml/config 更新配置")
        print("   4. 配置完成后测试 GET /api/system/saml/login")
        return 0
    else:
        print("❌ 示例配置创建失败")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)