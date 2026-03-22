# N-Tester MCP 增强版

> 集成官方 Playwright MCP 的 N-Tester 测试工具

## 📋 目录结构

```
N-Tester_MCP/
├── src/                              # 源代码
│   ├── core/                         # 核心功能
│   │   ├── N-Tester_tools.py        # 主服务
│   │   ├── ms_mcp_api.py            # MCP API
│   │   └── config_enhanced.py       # 配置
│   ├── integrations/                 # 集成模块
│   │   └── playwright/              # Playwright 集成
│   │       ├── enhanced_playwright_integration.py
│   │       ├── http_bridge.js       # HTTP 桥接服务
│   │       └── config.json          # Playwright 配置
│   └── wrappers/                     # 包装器
│       ├── http_wrapper.py          # HTTP 包装器
│       └── start_http_wrapper.py    # 启动脚本
├── scripts/                          # 脚本
│   ├── start/                       # 启动脚本
│   │   ├── start-enhanced.bat       # Windows 启动
│   │   ├── start-enhanced.sh        # Linux 启动
│   │   ├── stop-services.bat        # Windows 停止
│   │   └── stop-services.sh         # Linux 停止
│   └── test/                        # 测试脚本
├── tests/                            # 单元测试
├── docs/                             # 文档
├── config/                           # 配置文件
├── start.bat / start.sh              # 主启动脚本
├── install-deps.bat / install-deps.sh # 依赖安装脚本
└── package.json                      # Node.js 依赖
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# Windows
install-deps.bat

# Linux/Mac
chmod +x install-deps.sh
./install-deps.sh
```

### 2. 配置环境变量

复制配置文件并编辑：

```bash
cp config/.env.example config/.env
```

编辑 `config/.env` 文件，设置必要的环境变量。

### 3. 启动服务

```bash
# Windows
start.bat

# Linux/Mac
chmod +x start.sh
./start.sh
```

### 4. 访问服务

- **Playwright MCP**: http://127.0.0.1:3000
- **N-Tester MCP**: http://127.0.0.1:8006

---

## 📖 使用指南

### 启动服务

```bash
# 方法 1: 使用主启动脚本
./start.sh  # 或 start.bat
pip install -r requirements.txt

# 方法 2: 使用详细启动脚本
./scripts/start/start-enhanced.sh  # 或 start-enhanced.bat
```

### 停止服务

```bash
# 方法 1: 按 Ctrl+C（如果在前台运行）

# 方法 2: 使用停止脚本
./scripts/start/stop-services.sh  # 或 stop-services.bat
```

### 测试服务

```bash
# 测试目录结构
./test-new-structure.bat

# 测试 Playwright MCP 桥接
node scripts/test/test_bridge_service.js

# 测试工具列表
python scripts/test/test_list_playwright_tools.py
```

---

## 🔧 配置说明

### 环境变量

在 `config/.env` 文件中配置：

```bash
# 后端地址
N-Tester_BACKEND_URL=http://127.0.0.1:8018

# API Key
N-Tester_API_KEY=your_api_key_here

# Playwright MCP 地址
PLAYWRIGHT_MCP_URL=http://127.0.0.1:3000
```

### Playwright 配置

在 `src/integrations/playwright/config.json` 中配置 Playwright 选项。

---

## 📝 开发指南

### 添加新的集成

1. 在 `src/integrations/` 下创建新目录
2. 实现集成逻辑
3. 更新启动脚本

示例：添加 filesystem-mcp

```bash
mkdir -p src/integrations/filesystem
# 添加集成代码
```

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python tests/test_playwright_example.py
```

---

## 🐛 故障排除

### 问题 1: 端口被占用

**症状**: 启动时提示端口 3000 或 8006 被占用

**解决方案**:
```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux
lsof -i :3000
kill -9 <PID>
```

### 问题 2: 找不到模块

**症状**: Python 提示 ModuleNotFoundError

**解决方案**:
```bash
# 重新安装依赖
./install-deps.sh
```

### 问题 3: Node.js 模块未找到

**症状**: Node.js 提示 Cannot find module

**解决方案**:
```bash
# 安装 Node.js 依赖
npm install
```

---

---

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📄 许可证

MIT License

---

## 📞 支持

如有问题，请：
1. 提交 Issue

---

## 🎉 致谢

- [Playwright](https://playwright.dev/) - 官方 Playwright MCP
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP 框架
- [FastAPI](https://fastapi.tiangolo.com/) - HTTP API 框架
