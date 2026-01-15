#!/bin/bash
set -e

echo "🚀 启动测试平台后端服务..."
echo "数据库类型: ${DB_TYPE:-mysql}"
echo "数据库主机: ${DB_HOST:-localhost}"

# 等待数据库服务启动
echo "⏳ 等待数据库服务启动..."
if [ "${DB_TYPE:-mysql}" = "postgresql" ]; then
    echo "等待 PostgreSQL 启动..."
    while ! nc -z ${DB_HOST:-postgres} ${DB_PORT:-5432}; do
        echo "PostgreSQL 未就绪，等待中..."
        sleep 2
    done
    echo "✅ PostgreSQL 已就绪"
else
    echo "等待 MySQL 启动..."
    while ! nc -z ${DB_HOST:-mysql} ${DB_PORT:-3306}; do
        echo "MySQL 未就绪，等待中..."
        sleep 2
    done
    echo "✅ MySQL 已就绪"
fi

# 检查是否需要初始化数据库
echo "🔍 检查数据库初始化状态..."
python -c "
import asyncio
import sys
from tortoise import Tortoise
from app.configs.config import tortoise_orm_conf

async def check_db():
    try:
        await Tortoise.init(config=tortoise_orm_conf)
        from app.models.system.user import User
        user_count = await User.all().count()
        print(f'数据库中有 {user_count} 个用户')
        return user_count > 0
    except Exception as e:
        print(f'数据库检查失败: {e}')
        return False
    finally:
        await Tortoise.close_connections()

result = asyncio.run(check_db())
sys.exit(0 if result else 1)
"

DB_INITIALIZED=$?

if [ $DB_INITIALIZED -eq 0 ]; then
    echo "✅ 数据库已初始化，跳过初始化步骤"
else
    echo "🏗️ 数据库未初始化，开始自动初始化..."
    
    # 初始化 aerich（如果需要）
    if [ ! -d "migrations/test_platform" ]; then
        echo "📝 初始化 aerich..."
        python -m aerich init -t app.configs.config.tortoise_orm_conf
        python -m aerich init-db
    fi
    
    # 运行数据库初始化
    python init_database.py --full
    
    if [ $? -eq 0 ]; then
        echo "✅ 数据库初始化成功！"
    else
        echo "❌ 数据库初始化失败！"
        exit 1
    fi
fi

# 应用数据库迁移（如果有新的迁移）
if [ -d "migrations/test_platform" ]; then
    echo "🔄 检查并应用数据库迁移..."
    python -m aerich upgrade || echo "⚠️  迁移应用失败或无新迁移"
fi

# 启动应用
echo "🚀 启动应用服务..."
exec "$@"