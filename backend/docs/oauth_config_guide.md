# OAuth 2.0 配置管理指南

## 概述

系统现在支持两种OAuth配置方式：
1. **UI界面配置**（推荐）：通过Web界面动态管理OAuth配置
2. **配置文件配置**（后备）：在config.py中硬编码配置

## 配置优先级

系统按以下优先级选择OAuth配置：
1. **UI配置优先**：如果UI中有启用的默认OAuth配置，优先使用
2. **配置文件后备**：如果UI中没有配置且config.py中auth_type='SSO'，使用配置文件配置
3. **无配置**：如果都没有配置，OAuth功能不可用

## UI界面配置（推荐）

### 访问路径
- 前端页面：`/config/oauth`
- API接口：`/api/config/oauth/*`

### 功能特性
- ✅ 支持多个OAuth提供商（GitHub、Gitee、Google、Microsoft、微信等）
- ✅ 动态启用/禁用配置
- ✅ 设置默认配置
- ✅ 连接测试功能
- ✅ 批量管理
- ✅ 实时生效，无需重启服务

### 使用步骤
1. 访问 `/config/oauth` 页面
2. 点击"新增OAuth配置"
3. 选择OAuth提供商或自定义配置
4. 填写Client ID、Client Secret等信息
5. 测试连接确保配置正确
6. 启用配置并设为默认（如需要）

## 配置文件配置（后备）

### 适用场景
- 系统初始化时的默认配置
- UI配置不可用时的后备方案
- 需要版本控制的固定配置

### 配置方法
1. 修改 `config.py` 中的 `auth_type = 'SSO'`
2. 配置 `_Sso` 类中的相关参数：
   ```python
   class _Sso:
       sso_host = "https://gitee.com/oauth/"
       client_id = "your_client_id"
       client_secret = "your_client_secret"
       redirect_uri = "http://your-domain/sso/login"
       # ... 其他配置
   ```
3. 重启服务使配置生效

## 配置迁移

### 从配置文件迁移到UI
如果你已经在配置文件中配置了OAuth，可以一键迁移到UI：

```bash
# API调用
POST /api/config/oauth/migrate
```

或者在前端OAuth配置页面点击"迁移配置文件配置"按钮。

### 迁移后的建议
1. 验证迁移后的配置是否正确
2. 测试OAuth登录功能
3. 将配置文件中的 `auth_type` 改回 `'test_platform'`
4. 保留配置文件配置作为后备（可选）

## API接口

### 配置管理接口
- `GET /api/config/oauth/list` - 获取OAuth配置列表
- `POST /api/config/oauth/create` - 创建OAuth配置
- `PUT /api/config/oauth/{id}` - 更新OAuth配置
- `DELETE /api/config/oauth/{id}` - 删除OAuth配置
- `POST /api/config/oauth/set-default` - 设置默认配置

### 状态查询接口
- `GET /api/config/oauth/status` - 获取配置状态
- `GET /api/config/oauth/active` - 获取当前激活的配置
- `GET /api/config/oauth/providers` - 获取支持的OAuth提供商

### 迁移接口
- `POST /api/config/oauth/migrate` - 迁移配置文件配置到UI

### 测试接口
- `GET /api/config/oauth/{id}/test` - 测试指定配置
- `POST /api/config/oauth/test-connection` - 测试连接

## 最佳实践

### 1. 推荐使用UI配置
- 更灵活，支持多个OAuth提供商
- 可以动态启用/禁用
- 支持实时测试和验证
- 无需重启服务

### 2. 配置文件作为后备
- 保留配置文件中的配置作为后备方案
- 在系统初始化或紧急情况下使用
- 便于版本控制和部署

### 3. 安全建议
- Client Secret等敏感信息建议使用环境变量
- 定期轮换OAuth应用的密钥
- 限制回调地址的域名范围

### 4. 测试建议
- 创建配置后立即测试连接
- 在生产环境部署前充分测试OAuth流程
- 监控OAuth登录的成功率和错误日志

## 故障排除

### 常见问题
1. **OAuth登录失败**
   - 检查Client ID和Client Secret是否正确
   - 验证回调地址是否在OAuth应用中正确配置
   - 确认OAuth配置处于启用状态

2. **配置不生效**
   - 检查是否有启用的默认配置
   - 验证配置优先级是否符合预期
   - 查看系统日志获取详细错误信息

3. **迁移失败**
   - 确认配置文件中auth_type='SSO'
   - 检查配置文件中的OAuth参数是否完整
   - 验证数据库连接是否正常

### 调试接口
```bash
# 查看当前配置状态
curl http://localhost:8018/api/config/oauth/status

# 查看激活的配置
curl http://localhost:8018/api/config/oauth/active

# 测试配置连接
curl -X POST http://localhost:8018/api/config/oauth/test-connection \
  -H "Content-Type: application/json" \
  -d '{"client_id":"xxx","client_secret":"xxx","authorize_url":"xxx","token_url":"xxx"}'
```

## 总结

通过UI界面配置OAuth是推荐的方式，它提供了更好的灵活性和用户体验。配置文件配置作为后备方案，确保系统在各种情况下都能正常工作。两种方式可以并存，系统会自动选择合适的配置。