# MCP 密钥配置指南

## 当前 MCP 服务说明

### 1. N-Tester_tools.py (端口 8006) ✅ 已可用
- **功能**: 测试用例管理（获取项目、模块、用例等）
- **状态**: 已启动并连接成功
- **配置**: 使用 `N-Tester_API_KEY=N-Tester-default-mcp-key-2025`

### 2. ms_mcp_api.py (端口 8007) ⚠️ 需要配置
- **功能**: 外部 MS 测试平台集成
- **状态**: 需要正确的密钥才能连接
- **配置**: 需要 `MS_ACCESS_KEY` 和 `MS_SECRET_KEY`

## MS 密钥配置要求

### 密钥长度要求
```
MS_ACCESS_KEY: 必须是 16 字节（16个字符）
MS_SECRET_KEY: 必须是 16/24/32 字节（推荐16字节）
```

### 配置示例
```bash
# .env 文件
MS_API_HOST=http://your-ms-platform.com
MS_ACCESS_KEY=1234567890ABCDEF  # 16字节示例
MS_SECRET_KEY=abcdefgh12345678  # 16字节示例
```

### 如何获取密钥
1. 联系你的 MS 测试平台管理员
2. 或在 MS 平台的 API 设置中生成
3. 确保密钥长度符合要求

## Playwright Test Agents 集成

### 当前状态
- ✅ N-Tester_tools (8006) 已连接
- ⚠️ 但 N-Tester_tools 不包含 Playwright 浏览器操作功能
- ⚠️ ms_mcp_api (8007) 也不包含 Playwright 功能

### 解决方案
**方案 A**: 使用 LLM 推理模式（当前实现）
- 不需要真实浏览器
- LLM 直接生成测试计划和代码
- 已自动降级，可以正常使用

**方案 B**: 扩展 N-Tester_tools 添加 Playwright 功能
- 需要在 N-Tester_tools.py 中添加浏览器操作工具
- 参考 Playwright MCP Server 的实现

## 测试连接

### 测试 N-Tester_tools
```bash
curl http://127.0.0.1:8006/mcp
```

### 测试 ms_mcp_api
```bash
# 需要先配置正确的密钥
python ms_mcp_api.py
```

## 常见问题

**Q: playwright-mcp-config.json 的作用？**
A: 这是 Playwright MCP Server 的配置文件，但当前没有运行 Playwright MCP Server

**Q: 如何让 Playwright Test Agents 使用真实浏览器？**
A: 需要运行支持 Playwright 的 MCP Server，或扩展现有的 N-Tester_tools

**Q: 当前能正常使用吗？**
A: 能！系统会自动使用 LLM 推理模式生成测试计划和代码
