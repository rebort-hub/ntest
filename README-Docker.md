# Docker 一键部署指南

## 快速开始

### 1. 环境要求
- Docker 20.10+
- Docker Compose 2.0+

### 2. 一键启动
```bash
# 克隆项目
git clone <https://github.com/rebort-hub/ntest>
cd <project-directory>

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问应用
- 前端: http://localhost
- 后端API: http://localhost:8018
- API文档: http://localhost:8018/docs

### 4. 停止服务
```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（注意：会删除数据库数据）
docker-compose down -v
```

## 服务说明

### MySQL (端口: 3306)
- 数据库名: test_platform
- 用户名: root
- 密码: Rebort
- 数据持久化: mysql_data 卷

### 后端 (端口: 8018, 8019)
- 主服务: 8018
- 任务调度: 8019
- 日志目录: ./backend/logs
- 上传目录: ./backend/uploads

### 前端 (端口: 80)
- Nginx反向代理
- 静态文件服务
- API代理到后端

## 配置说明

### 环境变量
编辑 `.env` 文件修改配置：
```bash
# 数据库配置
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Rebort
DB_NAME=test_platform

# AI配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 自定义配置
1. **数据库**: 修改 `docker-compose.yml` 中的 MySQL 环境变量
2. **端口**: 修改 `docker-compose.yml` 中的端口映射
3. **Nginx**: 修改 `frontend/nginx.conf`

## 开发模式

### 本地开发 + Docker数据库
```bash
# 只启动数据库
docker-compose up -d mysql

# 本地启动后端
cd backend
python main.py

# 本地启动前端
cd frontend
npm run dev
```

### 热重载开发
```bash
# 使用开发版docker-compose
docker-compose -f docker-compose.dev.yml up -d
```

## 生产部署

### 1. 修改生产配置
```bash
# 复制环境变量模板
cp .env .env.production

# 编辑生产环境配置
vim .env.production
```

### 2. 使用生产配置启动
```bash
docker-compose --env-file .env.production up -d
```

### 3. 备份数据
```bash
# 备份数据库
docker exec test-platform-mysql mysqldump -u root -pRebort test_platform > backup.sql

# 恢复数据库
docker exec -i test-platform-mysql mysql -u root -pRebort test_platform < backup.sql
```

## 故障排除

### 1. 服务启动失败
```bash
# 查看服务状态
docker-compose ps

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mysql
```

### 2. 数据库连接失败
```bash
# 检查MySQL是否就绪
docker-compose exec mysql mysqladmin ping -h localhost -u root -pRebort

# 进入MySQL容器
docker-compose exec mysql mysql -u root -pRebort test_platform
```

### 3. 前端无法访问后端
```bash
# 检查网络连接
docker-compose exec frontend ping backend

# 检查nginx配置
docker-compose exec frontend nginx -t
```

### 4. 重建服务
```bash
# 重建特定服务
docker-compose build backend
docker-compose up -d backend

# 重建所有服务
docker-compose build
docker-compose up -d
```

## 监控和维护

### 1. 健康检查
```bash
# 检查所有服务健康状态
docker-compose ps

# 手动健康检查
curl http://localhost:8018/api/health
curl http://localhost/
```

### 2. 日志管理
```bash
# 查看实时日志
docker-compose logs -f --tail=100

# 清理日志
docker-compose down
docker system prune -f
```

### 3. 性能监控
```bash
# 查看资源使用
docker stats

# 查看容器详情
docker-compose top
```

## 常见问题

### Q: 端口被占用怎么办？
A: 修改 `docker-compose.yml` 中的端口映射，例如将 `80:80` 改为 `8080:80`

### Q: 数据库数据丢失怎么办？
A: 数据存储在 `mysql_data` 卷中，除非手动删除卷，否则数据会持久化

### Q: 如何更新应用？
A: 
```bash
git pull
docker-compose build
docker-compose up -d
```

### Q: 如何扩展服务？
A: 
```bash
# 扩展后端服务到3个实例
docker-compose up -d --scale backend=3
```
