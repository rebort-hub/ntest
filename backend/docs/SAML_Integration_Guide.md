# SAML SSO 集成指南

## 概述

本平台已集成SAML 2.0协议支持，可以与各种身份提供商(IdP)进行单点登录集成，如Azure AD、ADFS、Okta、OneLogin等。

## 功能特性

- ✅ 支持SAML 2.0协议
- ✅ 多IdP配置管理
- ✅ 灵活的属性映射
- ✅ 安全配置选项
- ✅ 单点登录(SSO)
- ✅ 单点登出(SLO)
- ✅ 元数据自动生成
- ✅ 连接测试功能

## 架构说明

### 当前平台架构
- **后端**: FastAPI + Tortoise ORM + MySQL
- **前端**: Vue3 + TypeScript + ElementPlus
- **认证**: OAuth2.0 + SAML 2.0 双重支持

### SAML集成架构
```
┌─────────────────┐    SAML Request     ┌─────────────────┐
│                 │ ──────────────────> │                 │
│   Identity      │                     │   Your App      │
│   Provider      │ <────────────────── │   (Service      │
│   (IdP)         │    SAML Response    │   Provider)     │
└─────────────────┘                     └─────────────────┘
```

## 安装配置

### 1. 安装依赖

```bash
cd backend
pip install -r requirements_saml.txt
```

### 2. 数据库迁移

```bash
# 执行SAML配置表创建脚本
mysql -u root -p test_platform < migrations/saml_config_migration.sql
```

### 3. 更新配置

在 `config.py` 中设置认证类型：

```python
auth_type = 'SAML'  # 或者保持 'test_platform' 支持多种认证方式
```

## 配置管理

### 1. 访问配置页面

登录系统后，访问：`系统管理` -> `SAML SSO配置`

### 2. 创建SAML配置

#### 基础配置
- **配置名称**: 便于识别的配置名称
- **SP Entity ID**: 服务提供商实体ID，通常是你的应用URL
- **ACS URL**: 断言消费服务URL，格式：`https://your-domain.com/api/system/saml/acs`
- **SLS URL**: 单点登出URL，格式：`https://your-domain.com/api/system/saml/sls`

#### IdP配置
- **IdP Entity ID**: 身份提供商实体ID
- **IdP SSO URL**: 身份提供商单点登录URL
- **IdP SLS URL**: 身份提供商单点登出URL
- **IdP X.509证书**: 身份提供商的公钥证书

#### 属性映射
配置SAML属性到用户字段的映射关系：
- `username`: 用户名属性
- `email`: 邮箱属性
- `first_name`: 名字属性
- `last_name`: 姓氏属性

## 常见IdP配置示例

### Azure AD配置

1. **基础信息**
   - Entity ID: `https://your-domain.com/saml/metadata`
   - ACS URL: `https://your-domain.com/api/system/saml/acs`

2. **Azure AD信息**
   - IdP Entity ID: `https://sts.windows.net/{tenant-id}/`
   - IdP SSO URL: `https://login.microsoftonline.com/{tenant-id}/saml2`

3. **属性映射**
   ```json
   {
     "username": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name",
     "email": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress",
     "first_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname",
     "last_name": "http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname"
   }
   ```

### ADFS配置

1. **基础信息**
   - Entity ID: `https://your-domain.com/saml/metadata`
   - ACS URL: `https://your-domain.com/api/system/saml/acs`

2. **ADFS信息**
   - IdP Entity ID: `http://your-adfs-server.com/adfs/services/trust`
   - IdP SSO URL: `https://your-adfs-server.com/adfs/ls/`

## API接口说明

### 认证相关接口

#### 发起SAML登录
```http
GET /api/system/saml/login?config_id=1&relay_state=https://your-app.com/dashboard
```

#### 断言消费服务(ACS)
```http
POST /api/system/saml/acs
Content-Type: application/x-www-form-urlencoded

SAMLResponse=...&RelayState=...
```

#### 单点登出
```http
GET /api/system/saml/logout?config_id=1
```

#### 获取元数据
```http
GET /api/system/saml/metadata?config_id=1
```

### 配置管理接口

#### 获取配置列表
```http
GET /api/system/saml/config/list
```

#### 创建配置
```http
POST /api/system/saml/config
Content-Type: application/json

{
  "name": "Azure AD SAML",
  "entity_id": "https://your-domain.com/saml/metadata",
  "acs_url": "https://your-domain.com/api/system/saml/acs",
  "idp_entity_id": "https://sts.windows.net/tenant-id/",
  "idp_sso_url": "https://login.microsoftonline.com/tenant-id/saml2",
  "idp_x509_cert": "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----"
}
```

## 前端集成

### 登录页面集成

```vue
<template>
  <div class="login-container">
    <!-- 传统登录表单 -->
    <el-form v-if="!showSamlLogin">
      <!-- 用户名密码登录 -->
    </el-form>
    
    <!-- SAML登录按钮 -->
    <div class="saml-login-section">
      <el-divider>或</el-divider>
      <el-button 
        type="primary" 
        @click="loginWithSaml"
        :loading="samlLoading"
      >
        <el-icon><Key /></el-icon>
        企业SSO登录
      </el-button>
    </div>
  </div>
</template>

<script setup>
const loginWithSaml = async () => {
  try {
    samlLoading.value = true
    const response = await api.get('/api/system/saml/login')
    // 重定向到IdP登录页面
    window.location.href = response.data.redirect_url
  } catch (error) {
    ElMessage.error('SAML登录失败')
  } finally {
    samlLoading.value = false
  }
}
</script>
```

### 登录回调处理

```javascript
// 在路由守卫中处理SAML登录回调
router.beforeEach(async (to, from, next) => {
  if (to.path === '/saml/callback') {
    // 处理SAML登录回调
    const token = to.query.token
    if (token) {
      // 保存token并跳转到主页
      localStorage.setItem('access_token', token)
      next('/dashboard')
    } else {
      next('/login')
    }
  } else {
    next()
  }
})
```

## 安全考虑

### 证书管理
- 定期更新IdP证书
- 使用强加密算法
- 安全存储私钥

### 配置安全
- 启用断言签名验证
- 使用HTTPS传输
- 配置适当的会话超时

### 用户权限
- 基于SAML属性自动分配角色
- 实现最小权限原则
- 定期审核用户权限

## 故障排除

### 常见问题

1. **证书验证失败**
   - 检查IdP证书格式是否正确
   - 确认证书未过期
   - 验证证书链完整性

2. **属性映射错误**
   - 检查IdP发送的属性名称
   - 验证属性映射配置
   - 查看SAML响应日志

3. **时间同步问题**
   - 确保服务器时间同步
   - 检查时区设置
   - 调整时间容差配置

### 调试方法

1. **启用详细日志**
   ```python
   # 在config.py中启用调试模式
   import logging
   logging.getLogger('onelogin.saml2').setLevel(logging.DEBUG)
   ```

2. **查看SAML响应**
   ```bash
   # 查看应用日志
   tail -f logs/app.log | grep SAML
   ```

## 性能优化

### 缓存策略
- 缓存IdP元数据
- 缓存用户会话信息
- 优化数据库查询

### 负载均衡
- 支持多实例部署
- 会话状态外部存储
- 健康检查配置

## 监控告警

### 关键指标
- SAML登录成功率
- 响应时间监控
- 错误率统计

### 告警配置
- 证书过期提醒
- 登录失败率异常
- 服务可用性监控

## 总结

通过以上配置，你的平台现在支持：

1. **多种认证方式**: OAuth2.0 + SAML 2.0
2. **企业级集成**: 支持主流IdP
3. **灵活配置**: 可视化配置管理
4. **安全可靠**: 完整的安全机制
5. **易于维护**: 完善的监控和日志

这样的架构既保持了原有OAuth2.0的功能，又扩展了SAML协议支持，为企业用户提供了更好的SSO体验。