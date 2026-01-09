#!/usr/bin/env python3
"""
数据库切换脚本
用于在MySQL和PostgreSQL之间切换
"""
import os
import sys
import shutil
from pathlib import Path


def update_env_file(db_type: str):
    """更新.env文件中的数据库配置"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("错误: .env文件不存在")
        return False
    
    # 读取现有配置
    with open(env_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 更新配置
    new_lines = []
    for line in lines:
        if line.startswith('DB_TYPE='):
            new_lines.append(f'DB_TYPE={db_type}\n')
        elif line.startswith('DB_HOST='):
            if db_type == 'postgresql':
                new_lines.append('DB_HOST=postgres\n')
            else:
                new_lines.append('DB_HOST=mysql\n')
        elif line.startswith('DB_PORT='):
            if db_type == 'postgresql':
                new_lines.append('DB_PORT=5432\n')
            else:
                new_lines.append('DB_PORT=3306\n')
        elif line.startswith('DB_USER='):
            if db_type == 'postgresql':
                new_lines.append('DB_USER=postgres\n')
            else:
                new_lines.append('DB_USER=root\n')
        elif line.startswith('DB_PASSWORD='):
            if db_type == 'postgresql':
                new_lines.append('DB_PASSWORD=postgres\n')
            else:
                new_lines.append('DB_PASSWORD=Rebort\n')
        else:
            new_lines.append(line)
    
    # 写入更新后的配置
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ 已更新.env文件，数据库类型设置为: {db_type}")
    return True


def backup_migrations():
    """备份现有的迁移文件"""
    migrations_dir = Path('backend/migrations')
    if migrations_dir.exists():
        backup_dir = Path(f'backend/migrations_backup_{int(time.time())}')
        shutil.copytree(migrations_dir, backup_dir)
        print(f"✅ 已备份迁移文件到: {backup_dir}")


def show_next_steps(db_type: str):
    """显示后续步骤"""
    print("\n" + "="*50)
    print("🎉 数据库配置切换完成!")
    print("="*50)
    print(f"当前数据库类型: {db_type.upper()}")
    print("\n📋 后续步骤:")
    print("1. 重启Docker容器:")
    print("   docker-compose -f docker-compose.dev.yml down")
    print("   docker-compose -f docker-compose.dev.yml up -d")
    print("\n2. 初始化数据库:")
    print("   python backend/init_database.py")
    print("\n3. 运行数据库迁移 (如果需要):")
    print("   cd backend && aerich init -t config.tortoise_orm_conf")
    print("   cd backend && aerich init-db")
    print("\n4. 测试数据库连接:")
    print("   python backend/init_database.py check")
    
    if db_type == 'postgresql':
        print("\n💡 PostgreSQL特殊说明:")
        print("- 支持JSONB类型，性能更好")
        print("- 支持数组类型")
        print("- 更严格的数据类型检查")
    else:
        print("\n💡 MySQL特殊说明:")
        print("- 支持全文索引")
        print("- JSON类型支持")
        print("- 更宽松的数据类型转换")


def main():
    if len(sys.argv) != 2:
        print("用法: python switch_database.py [mysql|postgresql]")
        print("示例: python switch_database.py postgresql")
        sys.exit(1)
    
    db_type = sys.argv[1].lower()
    
    if db_type not in ['mysql', 'postgresql']:
        print("错误: 只支持 mysql 或 postgresql")
        sys.exit(1)
    
    print(f"🔄 正在切换到 {db_type.upper()} 数据库...")
    
    # 更新环境变量文件
    if not update_env_file(db_type):
        sys.exit(1)
    
    # 显示后续步骤
    show_next_steps(db_type)


if __name__ == "__main__":
    import time
    main()