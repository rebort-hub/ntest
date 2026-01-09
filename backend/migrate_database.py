"""
数据库迁移工具，从MySQL迁移到PostgreSQL或反向迁移
"""
import os
import asyncio
import json
from typing import Dict, Any, List
from tortoise import Tortoise
from tortoise.models import Model
from app.tools.db_compatibility import DatabaseCompatibility


class DatabaseMigrator:
    """数据库迁移器"""
    
    def __init__(self, source_config: Dict, target_config: Dict):
        self.source_config = source_config
        self.target_config = target_config
    
    async def migrate_data(self, model_classes: List[Model]):
        """迁移数据"""
        print("开始数据迁移...")
        
        # 初始化源数据库连接
        await Tortoise.init(config=self.source_config)
        source_db = Tortoise.get_connection("default")
        
        # 导出数据
        exported_data = {}
        for model_class in model_classes:
            table_name = model_class._meta.db_table
            print(f"导出表: {table_name}")
            
            # 获取所有数据
            data = await model_class.all().values()
            exported_data[table_name] = data
            print(f"导出 {len(data)} 条记录")
        
        await Tortoise.close_connections()
        
        # 初始化目标数据库连接
        await Tortoise.init(config=self.target_config)
        
        # 生成目标数据库表结构
        await Tortoise.generate_schemas()
        
        # 导入数据
        for model_class in model_classes:
            table_name = model_class._meta.db_table
            data_list = exported_data.get(table_name, [])
            
            if data_list:
                print(f"导入表: {table_name}")
                
                # 批量插入数据
                await model_class.bulk_create([
                    model_class(**self._adapt_data_for_target(data))
                    for data in data_list
                ])
                print(f"导入 {len(data_list)} 条记录")
        
        await Tortoise.close_connections()
        print("数据迁移完成!")
    
    def _adapt_data_for_target(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """适配数据格式到目标数据库"""
        adapted_data = data.copy()
        
        # 处理日期时间字段
        for key, value in adapted_data.items():
            if isinstance(value, str) and 'T' in value:
                # 可能是ISO格式的日期时间
                try:
                    from datetime import datetime
                    datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
        
        return adapted_data
    
    async def export_schema(self, output_file: str):
        """导出数据库结构"""
        await Tortoise.init(config=self.source_config)
        
        # 这里可以添加导出表结构的逻辑
        # 由于Tortoise ORM的限制，这部分需要根据具体需求实现
        
        await Tortoise.close_connections()


async def create_migration_configs():
    """创建迁移配置"""
    mysql_config = {
        'connections': {
            'default': {
                'engine': 'tortoise.backends.mysql',
                'credentials': {
                    'host': os.environ.get('SOURCE_DB_HOST', 'localhost'),
                    'port': int(os.environ.get('SOURCE_DB_PORT', '3306')),
                    'user': os.environ.get('SOURCE_DB_USER', 'root'),
                    'password': os.environ.get('SOURCE_DB_PASSWORD', ''),
                    'database': os.environ.get('SOURCE_DB_NAME', 'test_platform')
                }
            }
        },
        'apps': {
            'test_platform': {
                'models': [
                    "aerich.models",
                    'app.models.autotest.model_factory',
                    'app.models.system.model_factory',
                    'app.models.config.model_factory',
                    'app.models.assist.model_factory',
                    'app.models.manage.model_factory',
                    'app.models.aitestrebort.project',
                    'app.models.aitestrebort.testcase',
                    'app.models.aitestrebort.automation',
                    'app.models.aitestrebort.knowledge',
                    'app.models.aitestrebort.requirements',
                ],
                "default_connection": "default",
            }
        },
        "timezone": "Asia/Shanghai"
    }
    
    postgresql_config = {
        'connections': {
            'default': {
                'engine': 'tortoise.backends.asyncpg',
                'credentials': {
                    'host': os.environ.get('TARGET_DB_HOST', 'localhost'),
                    'port': int(os.environ.get('TARGET_DB_PORT', '5432')),
                    'user': os.environ.get('TARGET_DB_USER', 'postgres'),
                    'password': os.environ.get('TARGET_DB_PASSWORD', ''),
                    'database': os.environ.get('TARGET_DB_NAME', 'test_platform'),
                    'minsize': 1,
                    'maxsize': 10,
                }
            }
        },
        'apps': {
            'test_platform': {
                'models': [
                    "aerich.models",
                    'app.models.autotest.model_factory',
                    'app.models.system.model_factory',
                    'app.models.config.model_factory',
                    'app.models.assist.model_factory',
                    'app.models.manage.model_factory',
                    'app.models.aitestrebort.project',
                    'app.models.aitestrebort.testcase',
                    'app.models.aitestrebort.automation',
                    'app.models.aitestrebort.knowledge',
                    'app.models.aitestrebort.requirements',
                ],
                "default_connection": "default",
            }
        },
        "timezone": "Asia/Shanghai"
    }
    
    return mysql_config, postgresql_config


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("用法: python migrate_database.py [mysql_to_pg|pg_to_mysql]")
        sys.exit(1)
    
    migration_type = sys.argv[1]
    
    async def run_migration():
        mysql_config, postgresql_config = await create_migration_configs()
        
        if migration_type == "mysql_to_pg":
            migrator = DatabaseMigrator(mysql_config, postgresql_config)
            print("从MySQL迁移到PostgreSQL")
        elif migration_type == "pg_to_mysql":
            migrator = DatabaseMigrator(postgresql_config, mysql_config)
            print("从PostgreSQL迁移到MySQL")
        else:
            print("不支持的迁移类型")
            return
        
        # 这里需要导入所有的模型类
        # from app.models import ... 
        # model_classes = [...]
        # await migrator.migrate_data(model_classes)
        
        print("请根据实际情况导入模型类并执行迁移")
    
    asyncio.run(run_migration())