# Docker 部署指南

本指南介绍如何使用Docker部署测试平台，支持MySQL和PostgreSQL数据库的自动初始化。

## 🚀 快速开始

### 1. 环境准备

确保已安装：
- Docker (>= 20.10)
- Docker Compose (>= 2.0)

### 2. 配置数据库类型

编辑 `.env` 文件设置数据库类型：

```bash
# 使用 MySQL (默认)
DB_TYPE=mysql
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Rebort
DB_NAME=test_platform

# 使用 PostgreSQL
DB_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=test_platform

# 自动初始化数据库 (默认启用)
AUTO_INIT_DB=true
```

## 🐳 部署方式

### 开发环境部署

```bash
# 启动所有服务（MySQL + PostgreSQL + 后端）
docker-compose -f docker-compose.dev.yml up -d

# 仅启动 MySQL 环境
docker-compose -f docker-compose.dev.yml up -d mysql backend

# 仅启动 PostgreSQL 环境
docker-compose -f docker-compose.dev.yml up -d postgres backend

# 查看日志
docker-compose -f docker-compose.dev.yml logs -f backend
```

### 生产环境部署

```bash
# 启动生产环境
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
```

## 🔄 数据库切换

### 在线切换数据库类型

1. **停止服务**
```bash
docker-compose down
```

2. **修改配置**
```bash
# 编辑 .env 文件，修改 DB_TYPE
vim .env
```

3. **重新启动**
```bash
docker-compose up -d
```

### 使用环境变量切换

```bash
# 切换到 PostgreSQL
DB_TYPE=postgresql docker-compose up -d

# 切换到 MySQL
DB_TYPE=mysql docker-compose up -d
```

## 🏗️ 自动初始化功能

### 初始化流程

Docker启动时会自动执行以下步骤：

1. **等待数据库服务启动**
2. **检查数据库是否已初始化**
3. **如果未初始化，自动执行：**
   - 创建数据库表结构（101个表）
   - 插入默认数据（用户、角色、配置等）
4. **启动应用服务**

### 初始化日志示例

```
🚀 启动测试平台后端服务...
数据库类型: postgresql
数据库主机: postgres
⏳ 等待数据库服务启动...
等待 PostgreSQL 启动...
✅ PostgreSQL 已就绪
🔍 检查数据库初始化状态...
数据库中有 0 个用户
🏗️ 数据库未初始化，开始自动初始化...
================================================================================
🚀 数据库初始化脚本
📊 数据库类型: POSTGRESQL
================================================================================
✅ 数据库初始化成功！
🚀 启动应用服务...
```

### 跳过自动初始化

如果不需要自动初始化，可以设置环境变量：

```bash
AUTO_INIT_DB=false docker-compose up -d
```

## 📊 默认账号信息

自动初始化完成后，系统会创建以下默认账号：

| 角色 | 账号 | 密码 | 权限 |
|------|------|------|------|
| 系统管理员 | admin | 123456 | 所有权限 |
| 业务线负责人 | manager | manager | 业务线管理权限 |
| 测试人员 | tester | tester | 基础测试权限 |

## 🔧 服务配置

### 端口映射

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|----------|----------|------|
| 后端API | 8018 | 8018 | 主要API服务 |
| 后端Job | 8019 | 8019 | 任务调度服务 |
| MySQL | 3306 | 3306 | MySQL数据库 |
| PostgreSQL | 5432 | 5432 | PostgreSQL数据库 |
| 前端 | 80 | 80 | Web界面 |

### 数据持久化

```bash
# 数据卷
mysql_data          # MySQL数据
postgres_data       # PostgreSQL数据
./backend/logs      # 应用日志
./backend/uploads   # 上传文件
```

## 🔍 健康检查

### 服务健康状态

```bash
# 查看所有服务状态
docker-compose ps

# 查看健康检查日志
docker inspect test-platform-backend --format='{{.State.Health.Status}}'
```

### 手动健康检查

```bash
# 检查后端API
curl http://localhost:8018/api/health

# 检查数据库连接
docker exec test-platform-backend python -c "
import asyncio
from tortoise import Tortoise
from config import tortoise_orm_conf

async def check():
    await Tortoise.init(config=tortoise_orm_conf)
    print('数据库连接正常')
    await Tortoise.close_connections()

asyncio.run(check())
"
```

## 🚨 故障排除

### 1. 数据库连接失败

```bash
# 检查数据库服务状态
docker-compose ps mysql postgres

# 查看数据库日志
docker-compose logs mysql
docker-compose logs postgres

# 重启数据库服务
docker-compose restart mysql
# 或
docker-compose restart postgres
```

### 2. 初始化失败

```bash
# 查看初始化日志
docker-compose logs backend

# 手动运行初始化
docker exec -it test-platform-backend python init_database.py --full

# 重置数据库
docker-compose down -v  # 删除数据卷
docker-compose up -d    # 重新启动
```

### 3. 服务无法启动

```bash
# 查看详细错误信息
docker-compose logs --tail=50 backend

# 检查配置文件
docker exec -it test-platform-backend cat .env

# 重新构建镜像
docker-compose build --no-cache backend
docker-compose up -d
```

### 4. 端口冲突

```bash
# 检查端口占用
netstat -tulpn | grep :8018

# 修改端口映射
# 编辑 docker-compose.yml 中的 ports 配置
```

## 📝 最佳实践

### 1. 生产环境建议

```bash
# 使用特定版本标签
# 在 docker-compose.yml 中指定镜像版本

# 设置资源限制
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

### 2. 数据备份

```bash
# MySQL 备份
docker exec test-platform-mysql mysqldump -u root -pRebort test_platform > backup.sql

# PostgreSQL 备份
docker exec test-platform-postgres pg_dump -U postgres test_platform > backup.sql

# 恢复数据
docker exec -i test-platform-mysql mysql -u root -pRebort test_platform < backup.sql
```

### 3. 日志管理

```bash
# 限制日志大小
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 4. 安全配置

```bash
# 生产环境建议修改默认密码
# 使用 Docker secrets 管理敏感信息
# 配置防火墙规则
```

## 🔄 更新部署

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建并启动
docker-compose build backend
docker-compose up -d backend

# 或者完全重新部署
docker-compose down
docker-compose up -d --build
```

### 数据库迁移

```bash
# 如果有数据库结构变更
docker exec -it test-platform-backend python init_database.py --tables
```

## 📞 支持

如遇到问题：

1. 查看服务日志：`docker-compose logs -f backend`
2. 检查服务状态：`docker-compose ps`
3. 运行健康检查：`curl http://localhost:8018/api/health`
4. 查看数据库状态：`docker exec -it test-platform-backend python test_database_switch.py`

---

**部署完成后，访问 `http://localhost:8018` 开始使用测试平台！**