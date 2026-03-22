"""
数据库初始化脚本 -MySQL和PostgreSQL的自动初始化，包括表结构创建和默认数据插入

使用说明：
1. 首次部署：python init_database.py --full
2. 仅创建表：python init_database.py --tables
3. 仅插入数据：python init_database.py --data
4. 检查兼容性：python init_database.py --check

环境要求：
- 已配置正确的数据库连接信息（.env文件）
- 已安装所需的Python依赖包
- 数据库服务已启动并可连接
"""
import os
import sys
import asyncio
import json
from pathlib import Path
from tortoise import Tortoise
from app.configs.config import tortoise_orm_conf, password_secret_key
from app.tools.db_compatibility import DatabaseCompatibility
from app.schemas.enums import DataStatusEnum

# 导入模型
from app.models.system.model_factory import Permission, Role, RolePermissions, User, UserRoles
from app.models.config.model_factory import BusinessLine, ConfigType, Config, RunEnv
from app.models.assist.model_factory import Script


def print_banner():
    """打印"""
    print("=" * 80)
    print("数据库初始化脚本")
    print(f"数据库类型: {DatabaseCompatibility.get_db_type().upper()}")
    print("=" * 80)


def print_section(title):
    """打印章节标题"""
    print(f"\n{'*' * 20} {title} {'*' * 20}")


def print_subsection(title):
    """打印子章节标题"""
    print(f"    {'=' * 16} {title} {'=' * 16}")


def print_item(title):
    """打印项目标题"""
    print(f"        {'=' * 12} {title} {'=' * 12}")


def print_detail(title):
    """打印详细信息"""
    print(f"            {'=' * 8} {title} {'=' * 8}")


async def create_database_tables():
    """创建数据库表结构"""
    print_section("创建数据库表结构")
    
    try:
        print("正在初始化Tortoise ORM...")
        print(f"数据库配置: {tortoise_orm_conf['connections']['default']}")
        
        # 初始化Tortoise ORM
        await Tortoise.init(config=tortoise_orm_conf)
        print("Tortoise ORM 初始化成功")
        
        # 检查已加载的模型
        print(f"\n Tortoise 注册的模型数量: {len(Tortoise.apps)}")
        total_models = 0
        for app_name, models in Tortoise.apps.items():
            model_count = len(models)
            total_models += model_count
            print(f"  {app_name}: {model_count} 个模型")
        
        print(f"\n 正在生成 {total_models} 个模型的数据库表结构...")
        # 生成数据库表结构
        await Tortoise.generate_schemas()
        print(" 数据库表结构生成成功!")
        
        # 验证表创建
        await verify_table_creation()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库表结构创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_table_creation():
    """验证表创建情况"""
    try:
        db = Tortoise.get_connection("default")
        
        if DatabaseCompatibility.is_postgresql():
            result = await db.execute_query_dict("""
                SELECT COUNT(*) as count
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
            table_count = result[0]['count']
        else:
            result = await db.execute_query_dict("SELECT COUNT(*) as count FROM information_schema.tables WHERE table_schema = DATABASE();")
            table_count = result[0]['count']
        
        print(f"📊 成功创建 {table_count} 个数据库表")
        
    except Exception as e:
        print(f"⚠️ 表验证失败: {e}")


# 默认数据配置
DEFAULT_DATA_CONFIG = {
    # KYM分析项
    "kym_keyword": [
        {
            "topic": "使用群体",
            "children": [
                {"topic": "产品使用群体是哪些？"},
                {"topic": "用户与用户之间有什么关联？"},
                {"topic": "用户为什么提这个需求？"},
                {"topic": "用户最关心的是什么？"},
                {"topic": "用户的实际使用环境是什么？"}
            ]
        },
        {
            "topic": "里程碑",
            "children": [
                {"topic": "需求评审时间？"},
                {"topic": "开发提测时间？"},
                {"topic": "测试周期测试时间多长？"},
                {"topic": "轮次安排进行几轮测试？"},
                {"topic": "UAT验收时间？"},
                {"topic": "上线时间？"}
            ]
        },
        {
            "topic": "项目信息",
            "children": [
                {"topic": "项目背景是什么？"},
                {"topic": "这个项目由什么需要特别注意的地方？"},
                {"topic": "可以向谁进一步了解项目信息？"},
                {"topic": "有没有文档、手册、材料等可供参考？"},
                {"topic": "这是全新的产品还是维护升级的？"},
                {"topic": "有没有竞品分析结果或同类产品可供参考？"},
                {"topic": "历史版本曾今发生过那些重大故障？"}
            ]
        }
    ],
    
    # 节假日列表 (2025年)
    "holiday_list": [
        "01-01",
        "01-28", "01-29", "01-30", "01-31", "02-01", "02-02", "02-03", "02-04",
        "04-04", "04-05", "04-06",
        "05-01", "05-02", "05-03", "05-04", "05-05",
        "05-31", "06-01", "06-02",
        "10-01", "10-02", "10-03", "10-04", "10-05", "10-06", "10-07", "10-08"
    ],
    
    # 接口自动化测试内置断言
    "api_default_validator": [
        {
            "label": "code=0",
            "value": {"key": "code", "value": "0", "status": 1, "data_type": "int", "data_source": "content", "validate_type": "data", "validate_method": "相等"}
        },
        {
            "label": "data长度大于0",
            "value": {"key": "data", "value": "0", "status": 1, "data_type": "int", "data_source": "content", "validate_type": "data", "validate_method": "长度大于"}
        }
    ],
    
    # 响应时间级别映射
    "response_time_level": {"slow": 300, "very_slow": 1000},
    
    # 设备扩展信息
    "device_extends": {
        "contact_count": "联系人个数",
        "contact_person_count": "通讯录条数",
        "note_record_count": "短信条数",
        "app_installed_record_count": "APP安装数量"
    }
}


async def init_permissions():
    """初始化权限数据"""
    print_subsection("开始创建权限")
    
    try:
        # 读取权限配置文件
        rules_file = Path(__file__).parent / 'rules.json'
        if not rules_file.exists():
            print("⚠️ rules.json 文件不存在，跳过权限初始化")
            return
        
        with open(rules_file, 'r', encoding='utf8') as f:
            permission_dict = json.load(f)
        
        add_permission_list = []
        for source_type, permission_rules in permission_dict.items():
            for rule_type, permission_list in permission_rules.items():
                for permission in permission_list:
                    existing = await Permission.filter(
                        source_addr=permission["source_addr"], 
                        source_type=source_type
                    ).first()
                    if not existing:
                        permission["source_type"] = source_type
                        permission["source_class"] = "menu" if permission["source_addr"] != "admin" else "admin"
                        add_permission_list.append(Permission(**permission))
        
        if add_permission_list:
            await Permission.bulk_create(add_permission_list)
            print(f"✅创建了 {len(add_permission_list)} 个权限")
        else:
            print("ℹ️ 权限已存在，跳过创建")
            
    except Exception as e:
        print(f"❌ 权限创建失败: {e}")


async def init_roles():
    """初始化角色数据"""
    print_subsection("开始创建角色")
    
    try:
        # 创建管理员角色
        if not await Role.filter(name="管理员-后端").first():
            admin_role = await Role.model_create({"name": "管理员-后端", "desc": "后端管理员, 有权限访问任何接口"})
            admin_permission = await Permission.filter(source_addr='admin', source_type='api').first()
            if admin_permission:
                await RolePermissions.model_create({"role_id": admin_role.id, "permission_id": admin_permission.id})
            print("✅ 创建【后端管理员】角色")
        
        if not await Role.filter(name="管理员-前端").first():
            admin_role = await Role.model_create({"name": "管理员-前端", "desc": "前端管理员, 有权限访问任何页面、按钮"})
            admin_permission = await Permission.filter(source_addr='admin', source_type='front').first()
            if admin_permission:
                await RolePermissions.model_create({"role_id": admin_role.id, "permission_id": admin_permission.id})
            print("✅ 创建【前端管理员】角色")
        
        if not await Role.filter(name="开发/测试人员").first():
            test_role = await Role.model_create({"name": "开发/测试人员", "desc": "能访问项目的基本信息，不能访问配置管理"})
            print("✅ 创建【开发/测试人员】角色")
        
        if not await Role.filter(name="业务线负责人").first():
            manager_role = await Role.model_create({"name": "业务线负责人", "desc": "有权限访问业务线下项目的任何页面、按钮和配置管理、用户管理"})
            print("✅ 创建【业务线负责人】角色")
            
    except Exception as e:
        print(f"❌ 角色创建失败: {e}")


async def init_run_environments():
    """初始化运行环境"""
    print_subsection("开始创建运行环境")
    
    try:
        env_list = [
            {"name": "开发环境", "code": "dev_qa", "desc": "开发环境", "group": "QA环境", "num": 0},
            {"name": "测试环境", "code": "test_qa", "desc": "测试环境", "group": "QA环境", "num": 1},
            {"name": "UAT环境", "code": "uat_qa", "desc": "UAT环境", "group": "QA环境", "num": 2},
            {"name": "生产环境", "code": "production_qa", "desc": "生产环境", "group": "QA环境", "num": 3},
        ]
        
        created_count = 0
        for env in env_list:
            if not await RunEnv.filter(code=env["code"]).first():
                await RunEnv.model_create(env)
                created_count += 1
                print(f"✅ 创建运行环境【{env['name']}】")
        
        if created_count == 0:
            print("ℹ️ 运行环境已存在，跳过创建")
            
    except Exception as e:
        print(f"❌ 运行环境创建失败: {e}")


async def init_business_lines():
    """初始化业务线"""
    print_subsection("开始创建业务线")
    
    try:
        business_dict = {
            "name": "公共业务线", 
            "code": "common", 
            "desc": "公共业务线，所有人都可见、可操作", 
            "num": 0
        }
        
        business = await BusinessLine.filter(code=business_dict["code"]).first()
        if not business:
            # 获取所有运行环境ID
            run_env_ids = await RunEnv.all().values_list('id', flat=True)
            business_dict["env_list"] = list(run_env_ids)
            business = await BusinessLine.model_create(business_dict)
            print(f"✅ 创建业务线【{business.name}】")
        else:
            print("ℹ️ 业务线已存在，跳过创建")
            
        return business
        
    except Exception as e:
        print(f"❌ 业务线创建失败: {e}")
        return None


async def init_users(business):
    """初始化用户"""
    print_subsection("开始创建用户")
    
    try:
        user_list = [
            {"account": "admin", "password": "123456", "name": "系统管理员", "role": ["管理员-后端", "管理员-前端"]},
            {"account": "manager", "password": "manager", "name": "业务线负责人", "role": ["业务线负责人"]},
            {"account": "tester", "password": "tester", "name": "测试人员", "role": ["开发/测试人员"]}
        ]
        
        created_count = 0
        for user_info in user_list:
            if not await User.filter(account=user_info["account"]).first():
                user_data = {
                    "account": user_info["account"],
                    "password": User.password_to_hash(user_info["password"], password_secret_key),
                    "name": user_info["name"],
                    "status": DataStatusEnum.ENABLE,
                    "business_list": [business.id] if business else []
                }
                
                user = await User.model_create(user_data)
                
                # 分配角色
                for role_name in user_info["role"]:
                    role = await Role.filter(name=role_name).first()
                    if role:
                        await UserRoles.model_create({"user_id": user.id, "role_id": role.id})
                
                created_count += 1
                print(f"✅ 创建用户【{user_info['name']}】- 账号: {user_info['account']}, 密码: {user_info['password']}")
        
        if created_count == 0:
            print("ℹ️ 用户已存在，跳过创建")
            
    except Exception as e:
        print(f"❌ 用户创建失败: {e}")


async def init_config_types():
    """初始化配置类型"""
    print_subsection("开始创建配置类型")
    
    try:
        config_types = [
            {"name": "系统配置", "desc": "全局配置"},
            {"name": "邮箱", "desc": "邮箱服务器"},
            {"name": "接口自动化", "desc": "接口自动化测试"},
            {"name": "UI自动化", "desc": "UI自动化测试"},
            {"name": "APP自动化", "desc": "APP自动化测试"}
        ]
        
        created_count = 0
        for config_type in config_types:
            if not await ConfigType.filter(name=config_type["name"]).first():
                await ConfigType.model_create(config_type)
                created_count += 1
                print(f"✅ 创建配置类型【{config_type['name']}】")
        
        if created_count == 0:
            print("ℹ️ 配置类型已存在，跳过创建")
            
    except Exception as e:
        print(f"❌ 配置类型创建失败: {e}")


async def init_configs():
    """初始化配置"""
    print_subsection("开始创建配置")
    
    try:
        # 获取配置类型映射
        config_types = await ConfigType.all()
        type_dict = {ct.name: ct.id for ct in config_types}
        
        # 配置数据
        configs = {
            "系统配置": [
                {"name": "platform_name", "value": "N-Tester平台", "desc": "测试平台名字"},
                {"name": "platform_logo", "value": "/images/logo.svg", "desc": "平台Logo图片路径"},
                {"name": "login_background", "value": "/images/loginBackground.jpg", "desc": "登录页面背景图片路径"},
                {"name": "kym", "value": json.dumps(DEFAULT_DATA_CONFIG["kym_keyword"], ensure_ascii=False), "desc": "KYM分析项"},
                {"name": "holiday_list", "value": json.dumps(DEFAULT_DATA_CONFIG["holiday_list"], ensure_ascii=False), "desc": "节假日/调休日期，需每年手动更新"},
                {"name": "run_time_out", "value": "600", "desc": "前端运行测试时，等待的超时时间，秒"},
                {"name": "report_host", "value": "http://localhost", "desc": "查看报告域名"},
                {"name": "default_account", "value": json.dumps({"account": "admin", "password": "123456"}), "desc": "默认登录账号"},
            ],
            "接口自动化": [
                {"name": "request_time_out", "value": "60", "desc": "运行测试步骤时，request超时时间"},
                {"name": "response_time_level", "value": json.dumps(DEFAULT_DATA_CONFIG["response_time_level"]), "desc": "测试步骤响应时间级别的映射，毫秒"},
                {"name": "api_default_validator", "value": json.dumps(DEFAULT_DATA_CONFIG["api_default_validator"]), "desc": "接口自动化测试内置断言"},
            ],
            "UI自动化": [
                {"name": "wait_time_out", "value": "10", "desc": "等待元素出现时间"},
            ],
            "APP自动化": [
                {"name": "device_extends", "value": json.dumps(DEFAULT_DATA_CONFIG["device_extends"], ensure_ascii=False), "desc": "创建设备时，默认的设备详细数据"},
                {"name": "appium_new_command_timeout", "value": "120", "desc": "两条appium命令间的最长时间间隔"},
            ]
        }
        
        created_count = 0
        for config_type_name, config_list in configs.items():
            if config_type_name in type_dict:
                for config in config_list:
                    if not await Config.filter(name=config["name"]).first():
                        config["type"] = type_dict[config_type_name]
                        await Config.model_create(config)
                        created_count += 1
                        print(f"✅ 创建配置【{config['name']}】")
        
        if created_count == 0:
            print("ℹ️ 配置已存在，跳过创建")
            
    except Exception as e:
        print(f"❌ 配置创建失败: {e}")


async def init_scripts():
    """初始化脚本模板"""
    print_subsection("开始创建脚本模板")
    
    try:
        script_templates = [
            {"name": "base_template", "num": 0, "desc": "自定义函数文件使用规范说明"},
            {"name": "utils_template", "num": 1, "desc": "工具类自定义函数操作模板"},
            {"name": "database_template", "num": 2, "desc": "数据库操作类型的自定义函数文件模板"}
        ]
        
        created_count = 0
        for template in script_templates:
            if not await Script.filter(name=template["name"]).first():
                # 尝试读取模板文件
                template_file = Path(__file__).parent / "static" / f"{template['name']}.py"
                if template_file.exists():
                    with open(template_file, "r", encoding="utf-8") as f:
                        template["script_data"] = f.read()
                else:
                    template["script_data"] = f"# {template['desc']}\n# 模板文件不存在，请手动添加内容"
                
                await Script.model_create(template)
                created_count += 1
                print(f"✅ 创建脚本模板【{template['name']}】")
        
        if created_count == 0:
            print("ℹ️ 脚本模板已存在，跳过创建")
            
    except Exception as e:
        print(f"❌ 脚本模板创建失败: {e}")


async def insert_default_data():
    """插入默认数据"""
    print_section("插入默认数据")
    
    try:
        # 按依赖顺序初始化数据
        await init_run_environments()
        await init_permissions()
        await init_roles()
        
        business = await init_business_lines()
        await init_users(business)
        
        await init_config_types()
        await init_configs()
        await init_scripts()
        
        print("✅ 默认数据插入完成!")
        return True
        
    except Exception as e:
        print(f"❌ 默认数据插入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def check_database_status():
    """检查数据库状态"""
    print_section("检查数据库状态")
    
    try:
        await Tortoise.init(config=tortoise_orm_conf)
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
        
        # 检查关键数据
        user_count = await User.all().count()
        role_count = await Role.all().count()
        config_count = await Config.all().count()
        
        print(f"👥 用户数量: {user_count}")
        print(f"🔐 角色数量: {role_count}")
        print(f"⚙️ 配置数量: {config_count}")
        
        if user_count > 0:
            print("\n📋 默认用户账号:")
            users = await User.all().values('account', 'name')
            for user in users:
                print(f"  - {user['name']}: {user['account']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库状态检查失败: {e}")
        return False


async def full_initialization():
    """完整初始化"""
    print_banner()
    
    try:
        # 1. 创建表结构
        if not await create_database_tables():
            return False
        
        # 2. 插入默认数据
        if not await insert_default_data():
            return False
        
        # 3. 检查状态
        await check_database_status()
        
        print_section("🎉 数据库初始化完成!")
        print("📝 默认登录信息:")
        print("  管理员账号: admin / 123456")
        print("  测试账号: tester / tester")
        print("  负责人账号: manager / manager")
        print("\n🚀 现在可以启动应用了: python main.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 完整初始化失败: {e}")
        return False
    finally:
        await Tortoise.close_connections()


def show_help():
    """显示帮助信息"""
    help_text = """
数据库初始化脚本使用说明

用法:
    python init_database.py [选项]

选项:
    --full, -f      完整初始化（创建表 + 插入数据）[默认]
    --tables, -t    仅创建数据库表结构
    --data, -d      仅插入默认数据（需要表已存在）
    --check, -c     检查数据库状态和兼容性
    --help, -h      显示此帮助信息

示例:
    python init_database.py --full      # 完整初始化
    python init_database.py --tables    # 只创建表
    python init_database.py --data      # 只插入数据
    python init_database.py --check     # 检查状态

注意事项:
1. 确保数据库服务已启动
2. 确保 .env 文件中的数据库配置正确
3. 首次部署建议使用 --full 选项
4. 如果表已存在，使用 --data 选项补充数据
"""
    print(help_text)


async def main():
    """主函数"""
    args = sys.argv[1:] if len(sys.argv) > 1 else ['--full']
    
    if '--help' in args or '-h' in args:
        show_help()
        return
    
    try:
        if '--check' in args or '-c' in args:
            await Tortoise.init(config=tortoise_orm_conf)
            await check_database_status()
        elif '--tables' in args or '-t' in args:
            await create_database_tables()
        elif '--data' in args or '-d' in args:
            await Tortoise.init(config=tortoise_orm_conf)
            await insert_default_data()
        else:  # --full 或默认
            await full_initialization()
    finally:
        await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())