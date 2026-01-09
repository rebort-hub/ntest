#!/usr/bin/env python3
"""
验证数据库表创建情况
"""
import asyncio
from tortoise import Tortoise
from config import tortoise_orm_conf
from app.tools.db_compatibility import DatabaseCompatibility


async def verify_tables():
    """验证表创建情况"""
    print(f"🔍 验证 {DatabaseCompatibility.get_db_type().upper()} 数据库表...")
    
    try:
        await Tortoise.init(config=tortoise_orm_conf)
        db = Tortoise.get_connection("default")
        
        if DatabaseCompatibility.is_postgresql():
            # PostgreSQL 查询表
            result = await db.execute_query_dict("""
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
        else:
            # MySQL 查询表
            result = await db.execute_query_dict("SHOW TABLES;")
        
        print(f"📊 数据库中共有 {len(result)} 个表:")
        
        # 按类别分组显示
        categories = {
            'api_test_': '🔌 API测试相关',
            'web_ui_test_': '🌐 Web UI测试相关', 
            'app_ui_test_': '📱 App UI测试相关',
            'system_': '⚙️ 系统管理相关',
            'config_': '🔧 配置管理相关',
            'auto_test_': '🤖 自动化测试相关',
            'test_work_': '📋 测试工作相关',
            'aitestrebort_': '🧠 AI测试相关',
            'requirement': '📝 需求管理相关',
            'review_': '👀 评审相关',
            'oauth_': '🔐 OAuth相关',
        }
        
        categorized_tables = {}
        other_tables = []
        
        for table_info in result:
            if DatabaseCompatibility.is_postgresql():
                table_name = table_info['table_name']
            else:
                table_name = list(table_info.values())[0]
            
            categorized = False
            for prefix, category in categories.items():
                if table_name.startswith(prefix):
                    if category not in categorized_tables:
                        categorized_tables[category] = []
                    categorized_tables[category].append(table_name)
                    categorized = True
                    break
            
            if not categorized:
                other_tables.append(table_name)
        
        # 显示分类结果
        for category, tables in categorized_tables.items():
            print(f"\n{category} ({len(tables)} 个表):")
            for table in sorted(tables)[:5]:  # 只显示前5个
                print(f"  - {table}")
            if len(tables) > 5:
                print(f"  ... 还有 {len(tables) - 5} 个表")
        
        if other_tables:
            print(f"\n🗂️ 其他表 ({len(other_tables)} 个):")
            for table in sorted(other_tables):
                print(f"  - {table}")
        
        # 测试一些核心表的数据
        print(f"\n🧪 测试核心表...")
        
        # 测试用户表
        try:
            user_count = await db.execute_query_dict("SELECT COUNT(*) as count FROM system_user;")
            print(f"  system_user 表: {user_count[0]['count']} 条记录")
        except Exception as e:
            print(f"  system_user 表查询失败: {e}")
        
        # 测试项目表
        try:
            project_count = await db.execute_query_dict("SELECT COUNT(*) as count FROM api_test_project;")
            print(f"  api_test_project 表: {project_count[0]['count']} 条记录")
        except Exception as e:
            print(f"  api_test_project 表查询失败: {e}")
        
        print(f"\n✅ 数据库验证完成!")
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(verify_tables())