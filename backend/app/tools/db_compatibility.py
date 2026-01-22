"""
数据库兼容性工具类，处理不同数据库之间的差异
"""
import os
from typing import Dict, Any
from tortoise import Tortoise


class DatabaseCompatibility:
    """数据库兼容性处理类"""
    
    @staticmethod
    def get_db_type() -> str:
        """获取当前数据库类型"""
        return os.environ.get('DB_TYPE', 'mysql').lower()
    
    @staticmethod
    def is_mysql() -> bool:
        """判断是否为MySQL"""
        return DatabaseCompatibility.get_db_type() == 'mysql'
    
    @staticmethod
    def is_postgresql() -> bool:
        """判断是否为PostgreSQL"""
        return DatabaseCompatibility.get_db_type() == 'postgresql'
    
    @staticmethod
    def get_limit_offset_sql(limit: int, offset: int = 0) -> str:
        """获取分页SQL语句"""
        if DatabaseCompatibility.is_postgresql():
            return f"LIMIT {limit} OFFSET {offset}"
        else:  # MySQL
            return f"LIMIT {offset}, {limit}"
    
    @staticmethod
    def get_datetime_format() -> str:
        """获取日期时间格式"""
        if DatabaseCompatibility.is_postgresql():
            return "YYYY-MM-DD HH24:MI:SS"
        else:  # MySQL
            return "%Y-%m-%d %H:%i:%s"
    
    @staticmethod
    def get_json_extract_sql(column: str, path: str) -> str:
        """获取JSON字段提取SQL"""
        if DatabaseCompatibility.is_postgresql():
            return f"{column}->'{path}'"
        else:  # MySQL
            return f"JSON_EXTRACT({column}, '$.{path}')"
    
    @staticmethod
    def get_concat_sql(*columns) -> str:
        """获取字符串连接SQL"""
        if DatabaseCompatibility.is_postgresql():
            return " || ".join(columns)
        else:  # MySQL
            return f"CONCAT({', '.join(columns)})"
    
    @staticmethod
    def get_regex_sql(column: str, pattern: str) -> str:
        """获取正则表达式匹配SQL"""
        if DatabaseCompatibility.is_postgresql():
            return f"{column} ~ '{pattern}'"
        else:  # MySQL
            return f"{column} REGEXP '{pattern}'"
    
    @staticmethod
    def adapt_sql_for_db(sql: str) -> str:
        """根据数据库类型调整SQL语句"""
        if DatabaseCompatibility.is_postgresql():
            # PostgreSQL特定调整
            # 将MySQL的反引号替换为双引号
            sql = sql.replace('`', '"')
        else:
            # MySQL特定调整
            # 保持反引号或将双引号替换为反引号
            sql = sql.replace('"', '`')
        
        return sql
    
    @staticmethod
    async def execute_raw_sql(sql: str, params: list = None) -> list:
        """执行原生SQL，自动适配数据库类型"""
        adapted_sql = DatabaseCompatibility.adapt_sql_for_db(sql)
        db = Tortoise.get_connection("default")
        
        try:
            if params:
                result = await db.execute_query_dict(adapted_sql, params)
            else:
                result = await db.execute_query_dict(adapted_sql)
            
            # execute_query_dict直接返回list[dict]
            return result if result else []
        except Exception as e:
            # 记录错误并返回空列表
            print(f"Error executing SQL: {e}")
            print(f"SQL: {adapted_sql}")
            return []
    
    @staticmethod
    def get_migration_sql_adjustments() -> Dict[str, str]:
        """获取迁移SQL调整映射"""
        if DatabaseCompatibility.is_postgresql():
            return {
                'LONGTEXT': 'TEXT',
                'TINYINT(1)': 'BOOLEAN',
                'DATETIME': 'TIMESTAMP',
                'AUTO_INCREMENT': 'SERIAL',
                '`': '"',
            }
        else:
            return {
                'TEXT': 'LONGTEXT',
                'BOOLEAN': 'TINYINT(1)',
                'TIMESTAMP': 'DATETIME',
                'SERIAL': 'AUTO_INCREMENT',
                '"': '`',
            }