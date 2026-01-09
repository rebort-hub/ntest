#!/usr/bin/env python3
"""
数据库兼容性检查工具
检查项目中可能存在的数据库兼容性问题
"""
import os
import re
import asyncio
from pathlib import Path
from tortoise import Tortoise
from config import tortoise_orm_conf
from app.tools.db_compatibility import DatabaseCompatibility


class CompatibilityChecker:
    """兼容性检查器"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.suggestions = []
    
    def add_issue(self, file_path: str, line_no: int, issue: str, suggestion: str = ""):
        """添加兼容性问题"""
        self.issues.append({
            "file": file_path,
            "line": line_no,
            "issue": issue,
            "suggestion": suggestion
        })
    
    def add_warning(self, file_path: str, line_no: int, warning: str):
        """添加警告"""
        self.warnings.append({
            "file": file_path,
            "line": line_no,
            "warning": warning
        })
    
    def check_time_util_usage(self):
        """检查时间工具函数的使用"""
        print("🔍 检查时间工具函数使用...")
        
        # 查找所有Python文件
        for py_file in Path("app").rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_no, line in enumerate(lines, 1):
                    # 检查是否直接使用字符串格式的日期时间
                    if re.search(r'create_time__range.*\[.*["\'].*["\'].*\]', line):
                        self.add_issue(
                            str(py_file), line_no,
                            "直接使用字符串格式的日期时间范围查询",
                            "使用DatabaseCompatibility处理日期时间格式"
                        )
                    
                    # 检查time_calculate和get_now的使用
                    if 'time_calculate(' in line or 'get_now(' in line:
                        if 'DatabaseCompatibility' not in line:
                            self.add_warning(
                                str(py_file), line_no,
                                "使用时间工具函数，请确保已考虑数据库兼容性"
                            )
            
            except Exception as e:
                print(f"⚠️ 无法读取文件 {py_file}: {e}")
    
    def check_raw_sql_usage(self):
        """检查原生SQL的使用"""
        print("🔍 检查原生SQL使用...")
        
        for py_file in Path("app").rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for line_no, line in enumerate(lines, 1):
                    # 检查execute_sql的使用
                    if 'execute_sql(' in line:
                        if 'DatabaseCompatibility.execute_raw_sql' not in line:
                            self.add_issue(
                                str(py_file), line_no,
                                "使用execute_sql而非DatabaseCompatibility.execute_raw_sql",
                                "使用DatabaseCompatibility.execute_raw_sql以确保兼容性"
                            )
                    
                    # 检查SQL语法
                    if re.search(r'SELECT.*FROM.*WHERE', line, re.IGNORECASE):
                        # 检查字段引用
                        if '`' in line and '"' not in line:
                            self.add_warning(
                                str(py_file), line_no,
                                "SQL中使用MySQL特有的反引号，可能在PostgreSQL中不兼容"
                            )
                        elif '"' in line and '`' not in line:
                            self.add_warning(
                                str(py_file), line_no,
                                "SQL中使用PostgreSQL特有的双引号，可能在MySQL中不兼容"
                            )
            
            except Exception as e:
                print(f"⚠️ 无法读取文件 {py_file}: {e}")
    
    def check_model_field_types(self):
        """检查模型字段类型"""
        print("🔍 检查模型字段类型...")
        
        for py_file in Path("app/models").rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                for line_no, line in enumerate(lines, 1):
                    # 检查可能有兼容性问题的字段类型
                    if 'fields.TextField(' in line:
                        if 'max_length' not in line:
                            self.add_warning(
                                str(py_file), line_no,
                                "TextField未指定max_length，在不同数据库中行为可能不同"
                            )
                    
                    if 'fields.JSONField(' in line:
                        self.add_warning(
                            str(py_file), line_no,
                            "JSONField在MySQL和PostgreSQL中实现不同，请测试兼容性"
                        )
            
            except Exception as e:
                print(f"⚠️ 无法读取文件 {py_file}: {e}")
    
    async def check_database_functions(self):
        """检查数据库函数兼容性"""
        print("🔍 检查数据库函数兼容性...")
        
        try:
            await Tortoise.init(config=tortoise_orm_conf)
            db = Tortoise.get_connection("default")
            
            # 测试常用函数
            test_queries = [
                "SELECT COUNT(*) as count FROM system_user",
                "SELECT NOW() as current_time" if DatabaseCompatibility.is_mysql() else "SELECT CURRENT_TIMESTAMP as current_time",
            ]
            
            for query in test_queries:
                try:
                    await db.execute_query_dict(query)
                    print(f"✅ 查询测试通过: {query}")
                except Exception as e:
                    self.add_issue(
                        "database_functions", 0,
                        f"数据库函数不兼容: {query}",
                        f"错误: {e}"
                    )
        
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
        finally:
            await Tortoise.close_connections()
    
    def generate_report(self):
        """生成兼容性报告"""
        print("\n" + "="*80)
        print("📋 数据库兼容性检查报告")
        print("="*80)
        print(f"当前数据库类型: {DatabaseCompatibility.get_db_type().upper()}")
        
        if self.issues:
            print(f"\n❌ 发现 {len(self.issues)} 个兼容性问题:")
            for i, issue in enumerate(self.issues, 1):
                print(f"{i}. 文件: {issue['file']}")
                print(f"   行号: {issue['line']}")
                print(f"   问题: {issue['issue']}")
                if issue['suggestion']:
                    print(f"   建议: {issue['suggestion']}")
                print()
        
        if self.warnings:
            print(f"\n⚠️ 发现 {len(self.warnings)} 个警告:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. 文件: {warning['file']}")
                print(f"   行号: {warning['line']}")
                print(f"   警告: {warning['warning']}")
                print()
        
        if not self.issues and not self.warnings:
            print("\n✅ 未发现明显的兼容性问题!")
        
        print("\n💡 兼容性建议:")
        print("1. 使用DatabaseCompatibility工具类处理数据库差异")
        print("2. 避免使用数据库特定的SQL语法")
        print("3. 使用Tortoise ORM的标准字段类型")
        print("4. 在切换数据库后进行充分测试")
        print("5. 使用时间工具函数的兼容版本")
    
    async def run_full_check(self):
        """运行完整检查"""
        print("🚀 开始数据库兼容性检查...")
        
        self.check_time_util_usage()
        self.check_raw_sql_usage()
        self.check_model_field_types()
        await self.check_database_functions()
        
        self.generate_report()


async def main():
    """主函数"""
    checker = CompatibilityChecker()
    await checker.run_full_check()


if __name__ == "__main__":
    asyncio.run(main())