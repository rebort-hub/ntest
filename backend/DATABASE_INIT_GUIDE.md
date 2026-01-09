# 数据库初始化指南

## 📋 概述

本指南适用于在新服务器上部署测试平台时的数据库初始化操作。支持 MySQL 和 PostgreSQL 两种数据库。

## 🚀 快速开始

### 1. 环境准备

确保以下条件已满足：
- 数据库服务已启动（MySQL 或 PostgreSQL）
- Python 虚拟环境已激活
- 依赖包已安装：`pip install -r requirements.txt`

### 2. 配置数据库连接

编辑 `.env` 文件，设置数据库连接信息：

```bash
# MySQL 配置
DB_TYPE=mysql
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=test_platform

# PostgreSQL 配置
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=test_platform
```

### 3. 执行初始化

```bash
# 完整初始化（推荐首次部署使用）
python init_database.py --full

# 或者分步执行
python init_database.py --tables  # 仅创建表结构
python init_database.py --data    # 仅插入默认数据
```

## 📖 命令详解

### 完整初始化
```bash
python init_database.py --full
```
- 创建所有数据库表（101个表）
- 插入默认数据（用户、角色、配置等）
- 验证初始化结果

### 仅创建表结构
```bash
python init_database.py --tables
```
- 仅创建数据库表结构
- 适用于已有数据但需要重建表的情况

### 仅插入默认数据
```bash
python init_database.py --data
```
- 仅插入默认数据
- 适用于表已存在但缺少初始数据的情况

### 检查数据库状态
```bash
python init_database.py --check
```
- 检查数据库连接
- 显示表数量和关键数据统计
- 列出默认用户账号

### 显示帮助
```bash
python init_database.py --help
```

## 👥 默认账号

初始化完成后，系统会创建以下默认账号：

| 角色 | 账号 | 密码 | 权限 |
|------|------|------|------|
| 系统管理员 | admin | 123456 | 所有权限 |
| 业务线负责人 | manager | manager | 业务线管理权限 |
| 测试人员 | tester | tester | 基础测试权限 |

## 📊 初始化内容

### 数据库表（101个）
- **API测试相关**：11个表
- **Web UI测试相关**：12个表
- **App UI测试相关**：14个表
- **AI测试相关**：24个表
- **系统管理相关**：7个表
- **配置管理相关**：6个表
- **需求管理相关**：3个表
- **其他功能表**：24个表

### 默认数据
- **运行环境**：开发、测试、UAT、生产环境
- **权限系统**：66个权限点
- **角色系统**：4个默认角色
- **业务线**：公共业务线
- **用户系统**：3个默认用户
- **配置系统**：14个系统配置
- **脚本模板**：3个函数模板

## 🔧 故障排除

### 1. 数据库连接失败
```bash
# 检查数据库服务状态
# MySQL
sudo systemctl status mysql

# PostgreSQL
sudo systemctl status postgresql

# 检查连接配置
python init_database.py --check
```

### 2. 权限不足
```bash
# 确保数据库用户有创建表的权限
# MySQL
GRANT ALL PRIVILEGES ON test_platform.* TO 'your_user'@'localhost';

# PostgreSQL
GRANT ALL PRIVILEGES ON DATABASE test_platform TO your_user;
```

### 3. 表已存在错误
```bash
# 如果需要重新初始化，先删除数据库
# MySQL
DROP DATABASE test_platform;
CREATE DATABASE test_platform;

# PostgreSQL
DROP DATABASE test_platform;
CREATE DATABASE test_platform;

# 然后重新初始化
python init_database.py --full
```

### 4. 模块导入错误
```bash
# 确保在正确的目录下执行
cd backend

# 确保虚拟环境已激活
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

## 🔄 数据库切换

如需在 MySQL 和 PostgreSQL 之间切换：

```bash
# 使用切换脚本
python switch_database.py mysql      # 切换到 MySQL
python switch_database.py postgresql # 切换到 PostgreSQL

# 重新初始化
python init_database.py --full
```

## 📝 注意事项

1. **首次部署**：建议使用 `--full` 选项进行完整初始化
2. **数据备份**：重要数据请提前备份
3. **权限检查**：确保数据库用户有足够权限
4. **环境变量**：确保 `.env` 文件配置正确
5. **依赖安装**：确保所有 Python 依赖已安装

## 🆘 获取帮助

如遇到问题，可以：
1. 查看详细错误信息
2. 检查数据库日志
3. 使用 `--check` 选项诊断问题
4. 参考项目文档或联系开发团队

---

**初始化完成后，即可启动应用：**
```bash
python main.py
```

访问 `http://localhost:8018` 开始使用测试平台！