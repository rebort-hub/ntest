"""
数据库管理辅助工具

推荐直接使用 aerich 命令：
1. 首次初始化: 
   python -m aerich init -t app.configs.config.tortoise_orm_conf
   python -m aerich init-db

2. 模型变更后:
   python -m aerich migrate --name 描述
   python -m aerich upgrade

本工具提供一些便捷的辅助命令：
- python db_manager.py status  # 检查数据库状态
- python db_manager.py setup   # 完整初始化（表+数据）
"""
import os
import sys
import asyncio
from pathlib import Path
from tortoise import Tortoise
from app.configs.config import tortoise_orm_conf, DB_TYPE
from app.tools.db_compatibility import DatabaseCompatibility


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.db_type = DB_TYPE
        self.config = tortoise_orm_conf
        
    def print_banner(self, title):
        """打印标题"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print(f"  数据库类型: {self.db_type.upper()}")
        print("=" * 80 + "\n")
    
    async def create_tables(self):
        """创建数据库表结构"""
        self.print_banner("创建数据库表结构")
        
        try:
            await Tortoise.init(config=self.config)
            print("正在生成表结构...")
            await Tortoise.generate_schemas(safe=True)
            
            # 验证表创建
            db = Tortoise.get_connection("default")
            if DatabaseCompatibility.is_postgresql():
                result = await db.execute_query_dict("""
                    SELECT COUNT(*) as count
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
            else:
                result = await db.execute_query_dict("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE();
                """)
            
            table_count = result[0]['count']
            print(f"✅ 成功创建 {table_count} 个数据库表")
            return True
            
        except Exception as e:
            print(f"❌ 表结构创建失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await Tortoise.close_connections()
    
    async def check_status(self):
        """检查数据库状态"""
        self.print_banner("检查数据库状态")
        
        try:
            await Tortoise.init(config=self.config)
            db = Tortoise.get_connection("default")
            
            # 检查连接
            await db.execute_query("SELECT 1;")
            print("✅ 数据库连接正常")
            
            # 检查表数量
            if DatabaseCompatibility.is_postgresql():
                result = await db.execute_query_dict("""
                    SELECT COUNT(*) as count
                    FROM information_schema.tables 
                    WHERE table_schema = 'public';
                """)
            else:
                result = await db.execute_query_dict("""
                    SELECT COUNT(*) as count 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE();
                """)
            
            table_count = result[0]['count']
            print(f"📊 数据库表数量: {table_count}")
            
            # 检查Aerich状态
            try:
                aerich_result = await db.execute_query_dict("SELECT * FROM aerich LIMIT 1;")
                if aerich_result:
                    print(f"📋 Aerich版本: {aerich_result[0].get('version', 'unknown')}")
                else:
                    print("⚠️  Aerich表为空，可能需要运行: python -m aerich init-db")
            except:
                print("⚠️  Aerich未初始化，需要运行: python -m aerich init-db")
            
            # 检查关键模型
            from app.models.system.model_factory import User, Role
            from app.models.config.model_factory import Config
            
            user_count = await User.all().count()
            role_count = await Role.all().count()
            config_count = await Config.all().count()
            
            print(f"👥 用户数量: {user_count}")
            print(f"🔐 角色数量: {role_count}")
            print(f"⚙️  配置数量: {config_count}")
            
            return True
            
        except Exception as e:
            print(f"❌ 状态检查失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await Tortoise.close_connections()
    
    async def insert_default_data(self):
        """插入默认数据"""
        self.print_banner("插入默认数据")
        
        try:
            # 导入init_database的数据插入函数
            from init_database import insert_default_data
            
            await Tortoise.init(config=self.config)
            result = await insert_default_data()
            
            if result:
                print("✅ 默认数据插入成功!")
            return result
            
        except Exception as e:
            print(f"❌ 默认数据插入失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await Tortoise.close_connections()
    
    async def full_setup(self):
        """完整设置流程"""
        self.print_banner("完整数据库设置")
        
        print("📝 执行步骤:")
        print("  1. 创建表结构")
        print("  2. 插入默认数据")
        print()
        
        # 步骤1: 创建表结构
        if not await self.create_tables():
            print("❌ 表结构创建失败，终止流程")
            return False
        
        # 步骤2: 插入默认数据
        if not await self.insert_default_data():
            print("❌ 默认数据插入失败")
            return False
        
        # 最终检查
        await self.check_status()
        
        self.print_banner("🎉 数据库设置完成")
        print("📝 默认登录信息:")
        print("  管理员: admin / 123456")
        print("  测试员: tester / tester")
        print("  负责人: manager / manager")
        print("\n💡 下一步:")
        print("  1. 初始化 aerich: python -m aerich init -t app.configs.config.tortoise_orm_conf")
        print("  2. 初始化数据库: python -m aerich init-db")
        print("  3. 启动应用: python main.py")
        
        return True


def show_help():
    """显示帮助信息"""
    help_text = """
数据库管理工具

推荐使用 aerich 标准命令：

首次初始化:
    python -m aerich init -t app.configs.config.tortoise_orm_conf
    python -m aerich init-db
    python init_database.py --data  # 插入默认数据

模型变更后:
    python -m aerich migrate --name 描述性名称
    python -m aerich upgrade

辅助命令:
    status      检查数据库连接和状态
    setup       完整初始化（创建表+插入数据）
    help        显示此帮助信息

"""
    print(help_text)


async def main():
    """主函数"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    manager = DatabaseManager()
    
    try:
        if command == "status":
            await manager.check_status()
        elif command == "setup":
            await manager.full_setup()
        elif command == "help":
            show_help()
        else:
            print(f"❌ 未知命令: {command}")
            print("\n推荐直接使用 aerich 命令，详见 DATABASE_GUIDE.md")
            show_help()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作已取消")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
