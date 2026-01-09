# 数据库兼容性指南

本项目支持 MySQL 和 PostgreSQL 两种数据库，用户可以根据需要选择使用。

## 🚀 快速开始

### 1. 切换数据库类型

使用提供的脚本快速切换数据库类型：

```bash
# 切换到 PostgreSQL
python switch_database.py postgresql

# 切换到 MySQL  
python switch_database.py mysql
```

### 2. 手动配置

也可以直接修改 `.env` 文件：

```bash
# 使用 MySQL
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
```

## 🐳 Docker 部署

项目的 Docker 配置已经支持两种数据库：

```bash
# 启动所有服务（包括 MySQL 和 PostgreSQL）
docker-compose -f docker-compose.dev.yml up -d

# 只启动 MySQL 相关服务
docker-compose -f docker-compose.dev.yml up -d mysql backend

# 只启动 PostgreSQL 相关服务  
docker-compose -f docker-compose.dev.yml up -d postgres backend
```

## 🔧 数据库初始化

### 初始化数据库表结构

```bash
python backend/init_database.py --full
```

### 检查数据库兼容性

```bash
python backend/check_compatibility.py
```

### 测试数据库切换

```bash
python backend/test_database_switch.py
```

## 📊 数据库特性对比

| 特性 | MySQL | PostgreSQL |
|------|-------|------------|
| JSON 支持 | ✅ JSON | ✅ JSON + JSONB |
| 全文搜索 | ✅ | ✅ |
| 窗口函数 | ✅ | ✅ |
| CTE 支持 | ✅ | ✅ |
| 数组类型 | ❌ | ✅ |
| 严格模式 | 可选 | 默认 |
| 性能 | 读取优化 | 复杂查询优化 |

## 🔄 数据类型映射

### MySQL → PostgreSQL

| MySQL | PostgreSQL |
|-------|------------|
| LONGTEXT | TEXT |
| TINYINT(1) | BOOLEAN |
| DATETIME | TIMESTAMP |
| AUTO_INCREMENT | SERIAL |
| \` (反引号) | " (双引号) |

### PostgreSQL → MySQL

| PostgreSQL | MySQL |
|------------|-------|
| TEXT | LONGTEXT |
| BOOLEAN | TINYINT(1) |
| TIMESTAMP | DATETIME |
| SERIAL | AUTO_INCREMENT |
| " (双引号) | \` (反引号) |

## 🛠️ 开发注意事项

### 1. 使用兼容性工具类

项目提供了 `DatabaseCompatibility` 工具类来处理数据库差异：

```python
from app.tools.db_compatibility import DatabaseCompatibility

# 检查数据库类型
if DatabaseCompatibility.is_postgresql():
    # PostgreSQL 特定逻辑
    pass
elif DatabaseCompatibility.is_mysql():
    # MySQL 特定逻辑  
    pass

# 执行兼容的 SQL
result = await DatabaseCompatibility.execute_raw_sql(sql)
```

### 2. 日期时间处理

```python
from utils.util.time_util import get_now, time_calculate

# 兼容的时间处理
current_time = get_now()  # 自动返回适合的格式
past_time = time_calculate(-7)  # 7天前
```

### 3. 模型定义最佳实践

```python
from tortoise import fields, models
from app.models.base_model import BaseModel

class ExampleModel(BaseModel):
    # 使用 Tortoise ORM 的标准字段类型
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    is_active = fields.BooleanField(default=True)
    data = fields.JSONField(default=dict)
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "example_table"
```

### 4. 避免数据库特定语法

```python
# ❌ 避免使用数据库特定语法
await connection.execute_query("SELECT * FROM table LIMIT 10 OFFSET 20")

# ✅ 使用 ORM 查询
await Model.all().offset(20).limit(10)

# ✅ 或使用兼容性工具
sql = f"SELECT * FROM table {DatabaseCompatibility.get_limit_offset_sql(10, 20)}"
```

## 🔍 兼容性检查工具

### 运行兼容性检查

```bash
python backend/check_compatibility.py
```

这个工具会检查：
- 时间工具函数的使用
- 原生SQL的兼容性
- 模型字段类型
- 数据库函数兼容性

### 运行切换测试

```bash
python backend/test_database_switch.py
```

这个工具会测试：
- 基本数据库操作
- 仪表板API兼容性
- 统计API兼容性

## 🔄 数据库切换流程

### 完整切换流程

1. **备份当前数据**（重要！）
2. **停止应用服务**
3. **修改配置文件**
4. **启动目标数据库**
5. **初始化数据库**
6. **迁移数据**（可选）
7. **测试兼容性**
8. **启动应用服务**

### 示例：从PostgreSQL切换到MySQL

```bash
# 1. 备份数据
pg_dump test_platform > backup.sql

# 2. 停止服务
docker-compose -f docker-compose.dev.yml down

# 3. 切换配置
python switch_database.py mysql

# 4. 启动MySQL
docker-compose -f docker-compose.dev.yml up -d mysql

# 5. 初始化数据库
python backend/init_database.py --full

# 6. 测试兼容性
python backend/test_database_switch.py

# 7. 启动服务
docker-compose -f docker-compose.dev.yml up -d
```

## 🚨 故障排除

### 1. 连接失败

检查数据库服务状态：

```bash
# 检查 MySQL
docker ps | grep mysql

# 检查 PostgreSQL  
docker ps | grep postgres
```

### 2. 权限不足

```bash
# 确保数据库用户有创建表的权限
# MySQL
GRANT ALL PRIVILEGES ON test_platform.* TO 'your_user'@'localhost';

# PostgreSQL
GRANT ALL PRIVILEGES ON DATABASE test_platform TO your_user;
```

### 3. 日期时间格式错误

这通常是PostgreSQL特有的问题，确保：
- 使用 `utils.util.time_util` 中的兼容函数
- 在查询中使用datetime对象而非字符串

### 4. JSON字段兼容性

```python
# ✅ 推荐的JSON字段使用方式
data = fields.JSONField(default=dict)

# 查询时使用ORM方法
await Model.filter(data__contains={"key": "value"})
```

## 📝 已知兼容性问题及解决方案

### 1. 时间范围查询

**问题**: PostgreSQL要求datetime对象，MySQL接受字符串
**解决**: 使用兼容的时间工具函数

### 2. SQL语法差异

**问题**: 字段引用语法不同
**解决**: 使用DatabaseCompatibility.execute_raw_sql()

### 3. JSON字段行为

**问题**: MySQL和PostgreSQL的JSON实现不同
**解决**: 使用ORM查询，避免原生JSON操作

## 🤝 贡献

如果发现数据库兼容性问题，请：

1. 在 `app/tools/db_compatibility.py` 中添加兼容性处理
2. 更新相关文档
3. 添加测试用例
4. 提交 Pull Request

## 📞 支持

如有问题，可以：
1. 查看项目 Issues
2. 运行兼容性检查工具
3. 查看数据库日志
4. 参考项目文档或联系开发团队

---

**切换完成后，记得运行兼容性测试确保一切正常！**