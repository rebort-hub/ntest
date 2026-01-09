#!/usr/bin/env python3
"""
数据库切换测试脚本
测试在MySQL和PostgreSQL之间切换的兼容性
"""
import asyncio
import os
from pathlib import Path
from tortoise import Tortoise
from config import tortoise_orm_conf
from app.tools.db_compatibility import DatabaseCompatibility


async def test_basic_operations():
    """测试基本数据库操作"""
    print(f"🧪 测试基本操作 - {DatabaseCompatibility.get_db_type().upper()}")
    
    try:
        await Tortoise.init(config=tortoise_orm_conf)
        
        # 测试用户查询
        from app.models.system.user import User
        users = await User.all().limit(5)
        print(f"✅ 用户查询成功，找到 {len(users)} 个用户")
        
        # 测试业务线查询
        from app.models.config.business import BusinessLine
        businesses = await BusinessLine.all()
        print(f"✅ 业务线查询成功，找到 {len(businesses)} 个业务线")
        
        # 测试配置查询
        from app.models.config.config import Config
        configs = await Config.all().limit(10)
        print(f"✅ 配置查询成功，找到 {len(configs)} 个配置")
        
        # 测试时间范围查询
        from app.models.autotest.report import ApiReport
        from datetime import datetime, timedelta
        
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        if DatabaseCompatibility.is_postgresql():
            reports = await ApiReport.filter(create_time__range=[start_time, end_time]).limit(5)
        else:
            reports = await ApiReport.filter(create_time__range=[start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')]).limit(5)
        
        print(f"✅ 时间范围查询成功，找到 {len(reports)} 个报告")
        
        # 测试JSON字段查询
        from app.models.system.user import User
        users_with_business = await User.filter(business_list__not=[]).limit(3)
        print(f"✅ JSON字段查询成功，找到 {len(users_with_business)} 个有业务线的用户")
        
        return True
        
    except Exception as e:
        print(f"❌ 基本操作测试失败: {e}")
        return False
    finally:
        await Tortoise.close_connections()


async def test_dashboard_apis():
    """测试仪表板API兼容性"""
    print(f"🧪 测试仪表板API - {DatabaseCompatibility.get_db_type().upper()}")
    
    try:
        await Tortoise.init(config=tortoise_orm_conf)
        
        # 测试dashboard统计
        from app.services.autotest.dashboard import get_data_by_time
        from app.models.autotest.project import ApiProject
        
        time_data = await get_data_by_time(ApiProject)
        print(f"✅ 仪表板时间统计成功: {time_data}")
        
        return True
        
    except Exception as e:
        print(f"❌ 仪表板API测试失败: {e}")
        return False
    finally:
        await Tortoise.close_connections()


async def test_stat_apis():
    """测试统计API兼容性"""
    print(f"🧪 测试统计API - {DatabaseCompatibility.get_db_type().upper()}")
    
    try:
        await Tortoise.init(config=tortoise_orm_conf)
        
        # 测试业务线分析
        from app.models.autotest.report import ApiReport
        from app.models.autotest.project import ApiProject
        from app.models.config.business import BusinessLine
        
        # 获取第一个业务线
        business = await BusinessLine.first()
        if business:
            project_list = await ApiProject.filter(business_id=business.id).values("id")
            filter_dict = {"project_id__in": [data["id"] for data in project_list]}
            
            # 测试统计查询
            all_count = await ApiReport.filter(**filter_dict).count()
            pass_count = await ApiReport.filter(**filter_dict, is_passed=1).count()
            
            print(f"✅ 统计查询成功: 总数={all_count}, 通过数={pass_count}")
        else:
            print("⚠️ 没有业务线数据，跳过统计测试")
        
        return True
        
    except Exception as e:
        print(f"❌ 统计API测试失败: {e}")
        return False
    finally:
        await Tortoise.close_connections()


async def run_compatibility_tests():
    """运行兼容性测试"""
    print("=" * 60)
    print("🚀 数据库兼容性测试")
    print("=" * 60)
    
    results = []
    
    # 基本操作测试
    results.append(await test_basic_operations())
    
    # 仪表板API测试
    results.append(await test_dashboard_apis())
    
    # 统计API测试
    results.append(await test_stat_apis())
    
    # 总结
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"数据库类型: {DatabaseCompatibility.get_db_type().upper()}")
    print(f"测试通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！数据库兼容性良好")
        return True
    else:
        print("⚠️ 部分测试失败，请检查兼容性问题")
        return False


if __name__ == "__main__":
    asyncio.run(run_compatibility_tests())