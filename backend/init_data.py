# -*- coding: utf-8 -*-
import json
import os

from tortoise import Tortoise, run_async

from app.schemas.enums import DataStatusEnum
from config import tortoise_orm_conf, password_secret_key
from app.models.system.model_factory import Permission, Role, RolePermissions, User, UserRoles
from app.models.config.model_factory import BusinessLine, ConfigType, Config, RunEnv
from app.models.assist.model_factory import Script


def print_start_delimiter(content):
    print(f'{"*" * 20} {content} {"*" * 20}')


def print_type_delimiter(content):
    print(f'    {"=" * 16} {content} {"=" * 16}')


def print_item_delimiter(content):
    print(f'        {"=" * 12} {content} {"=" * 12}')


def print_detail_delimiter(content):
    print(f'            {"=" * 8} {content} {"=" * 8}')


kym_keyword = [
    {
        "topic": "使用群体",
        "children": [
            {"topic": "产品使用群体是哪些？"},
            {"topic": "用户与用户之间有什么关联？"},
            {"topic": "用户为什么提这个需求？"},
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
        "topic": "涉及人员",
        "children": [
            {"topic": "负责迭代的产品是谁？"},
            {"topic": "后端开发是谁经验如何？"},
            {"topic": "前端开发是谁经验如何？"},
            {"topic": "测试人员是谁？"}
        ]
    },
    {
        "topic": "涉及模块",
        "children": [
            {"topic": "项目中涉及哪些模块，对应的开发责任人是谁？"}
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
    },
    {
        "topic": "测试信息",
        "children": [
            {"topic": "会使用到的测试账号有哪些？"},
            {"topic": "会用到的测试地址？"},
            {"topic": "有没有不太熟悉、掌握的流程？"}
        ]
    },
    {
        "topic": "设备工具",
        "children": [
            {"topic": "测试过程中是否会用到其他测试设备资源是否够（Ukey、手机、平板）？"},
            {"topic": "会用到什么测试工具会不会使用？"}
        ]
    },
    {
        "topic": "测试团队",
        "children": [
            {"topic": "有几个测试团队负责测试？"},
            {"topic": "负责测试的人员组成情况？"},
            {"topic": "测试人员的经验如何？"},
            {"topic": "测试人员对被测对象的熟悉程度如何？"},
            {"topic": "测试人员是专职的还是兼职的？"},
            {"topic": "测试人手是否充足？"}
        ]
    },
    {
        "topic": "测试项",
        "children": [
            {"topic": "主要的测试内容有哪些？"},
            {"topic": "哪部分可以降低优先级或者先不测试？"},
            {"topic": "哪些内容是新增或修改？"},
            {"topic": "是否涉及历史数据迁移测试？"},
            {"topic": "是否涉及与外系统联调测试？"},
            {"topic": "是否需要进行性能、兼容性、安全测试？"}
        ]
    }
]

device_extends = {
    "contact_count": "联系人个数",
    "contact_person_count": "通讯录条数",
    "note_record_count": "短信条数",
    "app_installed_record_count": "APP安装数量"
}

# 2025 年的节假日，每年需手动更新
holiday_list = [
    "01-01",
    "01-28", "01-29", "01-30", "01-31", "02-01", "02-02", "02-03", "02-04",
    "04-04", "04-05", "04-06",
    "05-01", "05-02", "05-03", "05-04", "05-05",
    "05-31", "06-01", "06-02",
    "10-01", "10-02", "10-03", "10-04", "10-05", "10-06", "10-07", "10-08"
]

# 接口自动化测试内置断言，用于添加相似断言方式时，快速选择
api_default_validator = [
    {
        "label": "code=0",
        "value": {"key": "code", "value": "0", "status": 1, "data_type": "int", "data_source": "content", "validate_type": "data", "validate_method": "相等"}
    },
    {
        "label": "data长度大于0",
        "value": {"key": "data", "value": "0", "status": 1, "data_type": "int", "data_source": "content", "validate_type": "data", "validate_method": "长度大于"}
    }
]

# 测试步骤响应时间级别的映射，毫秒
response_time_level = {"slow": 300, "very_slow": 1000}

# 回调流水线消息内容
call_back_msg_addr = ""

# 暂停测试步骤执行的超时时间
pause_step_time_out = 10 * 60 # 10分钟

# shell 造数据的，服务器信息
shell_command_info = {
    "ip": "",
    "port": 22,
    "username": "",
    "password": "",
    "file_path": "",
    "log_path": ""
}

with open('rules.json', 'r', encoding='utf8') as rules:
    permission_dict = json.load(rules)


async def init_permission():
    """ 初始化权限 """
    print_type_delimiter("开始创建权限")
    add_permission_list = []
    for source_type, permission_rules in permission_dict.items():
        for rule_type, permission_list in permission_rules.items():
            for permission in permission_list:
                data = await Permission.filter(source_addr=permission["source_addr"], source_type=source_type).filter()
                if not data:
                    permission["source_type"] = source_type
                    permission["source_class"] = "menu" if permission["source_addr"] != "admin" else "admin"
                    add_permission_list.append(Permission(**permission))
    await Permission.bulk_create(add_permission_list)
    print_type_delimiter("权限创建完成")


async def init_role():
    """ 初始化角色和对应的权限 """
    print_type_delimiter("开始创建角色")

    print_type_delimiter("开始创建【后端管理员】角色")
    if not await Role.filter(name="管理员-后端").first():
        admin_role = await Role.model_create({"name": "管理员-后端", "desc": "后端管理员, 有权限访问任何接口"})
        admin_permission = await Permission.filter(source_addr='admin', source_type='api').first()
        await RolePermissions.model_create({"role_id": admin_role.id, "permission_id": admin_permission.id})
    print_type_delimiter("【后端管理员】创建完成")

    print_type_delimiter("开始创建【前端管理员】角色")
    if not await Role.filter(name="管理员-前端").first():
        admin_role = await Role.model_create({"name": "管理员-前端", "desc": "前端管理员, 有权限访问任何页面、按钮"})
        admin_permission = await Permission.filter(source_addr='admin', source_type='front').first()
        await RolePermissions.model_create({"role_id": admin_role.id, "permission_id": admin_permission.id})
    print_type_delimiter("【前端管理员】创建完成")

    print_type_delimiter("开始创建开发/测试人员角色")
    if not await Role.filter(name="开发/测试人员").first():
        test_role = await Role.model_create({"name": "开发/测试人员", "desc": "能访问项目的基本信息，不能访问配置管理"})
        for source_type, permission_rules in permission_dict.items():
            if source_type == "front":
                for rule_type, source_addr_list in permission_rules.items():
                    for source in source_addr_list:
                        addr = source["source_addr"]
                        # 管理员权限、系统管理、配置管理、帮助、任务管理，排除
                        if addr.startswith(('/system', '/config', '/help', 'admin')) is False:
                            permission = await Permission.filter(source_addr=addr).first()
                            await RolePermissions.model_create(
                                {"role_id": test_role.id, "permission_id": permission.id})
    print_type_delimiter("开发/测试人员角色创建完成")

    print_type_delimiter("开始创建业务线负责人角色")
    if not await Role.filter(name="业务线负责人").first():
        test_role = await Role.filter(name="开发/测试人员").first()
        manager_role = await Role.create(
            **{"name": "业务线负责人", "desc": "有权限访问业务线下项目的任何页面、按钮和配置管理、用户管理",
               "extend_role": [test_role.id]}
        )
        for source_type, permission_rules in permission_dict.items():
            if source_type == "front":
                for rule_type, source_addr_list in permission_rules.items():
                    for source in source_addr_list:
                        addr = source["source_addr"]
                        if addr == '/system' or addr.startswith(('/config', '/system/user')):  # 负责人给配置管理、用户管理权限
                            permission = await Permission.filter(source_addr=addr).first()
                            await RolePermissions.model_create(
                                {"role_id": manager_role.id, "permission_id": permission.id})

            if source_type == "api":
                for rule_type, source_addr_list in permission_rules.items():
                    for source in source_addr_list:
                        addr = source["source_addr"]
                        if addr == '/api/system/role/list' or addr.startswith('/api/system/user'):  # 负责人给用户管理接口/权限列表权限
                            permission = await Permission.filter(source_addr=addr, source_type='api').first()
                            await RolePermissions.model_create(
                                {"role_id": manager_role.id, "permission_id": permission.id})

    print_type_delimiter("业务线负责人角色创建完成")

    print_type_delimiter("角色创建完成")


async def init_user():
    """ 初始化用户和对应的角色 """

    # 创建业务线
    print_type_delimiter("开始创建业务线")
    business_dict = {"name": "公共业务线", "code": "common", "desc": "公共业务线，所有人都可见、可操作", "num": 0}
    business = await BusinessLine.filter(code=business_dict["code"]).first()
    if not business:
        run_env_id = await RunEnv.filter().all().values('id')
        business_dict["env_list"] = [data["id"] for data in run_env_id]
        business = await BusinessLine.model_create(business_dict)
        print_item_delimiter(f'业务线【{business.name}】创建成功')
    print_type_delimiter("业务线创建完成")

    # 创建用户
    print_type_delimiter("开始创建用户")
    user_list = [
        {"account": "admin1", "password": "123456", "name": "管理员1", "role": ["管理员-后端", "管理员-前端"]},
        {"account": "manager", "password": "manager", "name": "业务线负责人", "role": ["业务线负责人"]},
        {"account": "common", "password": "common", "name": "测试员", "role": ["开发/测试人员"]}
    ]
    for user_info in user_list:
        if not await User.filter(account=user_info["account"]).first():
            user_info["status"] = DataStatusEnum.ENABLE
            user_info["password"] = User.password_to_hash(user_info["password"], password_secret_key)
            user_info["business_list"] = [business.id]
            user = await User.model_create(user_info)
            for role_name in user_info["role"]:
                role = await Role.filter(name=role_name).first()
                await UserRoles.model_create({"user_id": user.id, "role_id": role.id})
            print_item_delimiter(f'用户【{user_info["name"]}】创建成功')

    print_type_delimiter("用户创建完成")


async def init_config_type():
    """ 初始化配置类型 """
    print_type_delimiter("开始创建配置类型")
    config_type_list = [
        {"name": "系统配置", "desc": "全局配置"},
        {"name": "邮箱", "desc": "邮箱服务器"},
        {"name": "接口自动化", "desc": "接口自动化测试"},
        {"name": "ui自动化", "desc": "ui自动化测试"},
        {"name": "app自动化", "desc": "app自动化测试"}
    ]
    for data in config_type_list:
        if not await ConfigType.filter(name=data["name"]).first():
            await ConfigType.model_create(data)
            print_item_delimiter(f'配置类型【{data["name"]}】创建成功')
    print_type_delimiter("配置类型创建完成")


async def init_config():
    """ 初始化配置 """

    print_type_delimiter("开始创建配置")

    # 配置
    type_dict = {config_type.name: config_type.id for config_type in await ConfigType.filter().all()}  # 所有配置类型
    conf_dict = {
        "邮箱": [
            {"name": "QQ邮箱", "value": "smtp.qq.com", "desc": "QQ邮箱服务器"}
        ],

        "系统配置": [
            {"name": "platform_name", "value": "N-Tester平台", "desc": "测试平台名字"},
            {"name": "platform_logo", "value": "/images/logo.svg", "desc": "平台Logo图片路径"},
            {"name": "login_background", "value": "/images/loginBackground.jpg", "desc": "登录页面背景图片路径"},
            {"name": "kym", "value": json.dumps(kym_keyword, ensure_ascii=False), "desc": "KYM分析项"},
            {"name": "sync_mock_data", "value": {}, "desc": "同步回调数据源"},
            {"name": "async_mock_data", "value": {}, "desc": "异步回调数据源"},
            {"name": "holiday_list", "value": json.dumps(holiday_list, ensure_ascii=False), "desc": "节假日/调休日期，需每年手动更新"},
            {"name": "default_diff_message_send_addr", "value": "", "desc": "yapi接口监控报告默认发送钉钉机器人地址"},
            {"name": "run_time_out", "value": "600", "desc": "前端运行测试时，等待的超时时间，秒"},
            {"name": "report_host", "value": "http://localhost", "desc": "查看报告域名"},
            {"name": "callback_webhook", "value": "", "desc": "接口收到回调请求后即时通讯通知的地址"},
            {"name": "call_back_msg_addr", "value": call_back_msg_addr, "desc": "发送回调流水线消息内容地址"},

            {"name": "default_account", "value": json.dumps({"account": "admin", "password": "123456"}),
             "desc": "默认登录账号"},
            {"name": "save_func_permissions", "value": "0", "desc": "保存脚本权限，0所有人都可以，1管理员才可以"},
            {"name": "pause_step_time_out", "value": pause_step_time_out, "desc": "暂停测试步骤执行的超时时间"},
            {"name": "shell_command_info", "value": json.dumps(shell_command_info), "desc": "shell 造数据的，服务器信息"},
            {"name": "pip_command", "value": "pip", "desc": "执行 'pip install' 时指定的pip，或者pip的绝对路径，用于在线管理第三方库"},
            {
                "name": "call_back_response",
                "value": "",
                "desc": "回调接口的响应信息，若没有设置值，则回调代码里面的默认响应"
            },
            {
                "name": "func_error_addr",
                "value": "/#/assist/error-record",
                "desc": "展示自定义函数错误记录的前端地址（用于即时通讯通知）"
            }
        ],

        "接口自动化": [
            {"name": "run_time_error_message_send_addr", "value": "", "desc": "运行测试用例时，有错误信息实时通知地址"},
            {"name": "request_time_out", "value": 60, "desc": "运行测试步骤时，request超时时间"},
            {"name": "response_time_level", "value": json.dumps(response_time_level), "desc": "测试步骤响应时间级别的映射，毫秒"},
            {
                "name": "api_report_addr",
                "value": "/#/api-test/report-show?id=",
                "desc": "展示测试报告页面的前端地址（用于即时通讯通知）"
            },
            {"name": "api_default_validator", "value": json.dumps(api_default_validator), "desc": "接口自动化测试内置断言，用于添加相似断言方式时，快速选择"}
        ],

        "ui自动化": [
            {"name": "wait_time_out", "value": 10, "desc": "等待元素出现时间"},
            {
                "name": "web_ui_report_addr",
                "value": "/#/ui-test/report-show?id=",
                "desc": "展示测试报告页面的前端地址（用于即时通讯通知）"
            }
        ],

        "app自动化": [
            {"name": "device_extends", "value": json.dumps(device_extends, ensure_ascii=False),
             "desc": "创建设备时，默认的设备详细数据"},
            {
                "name": "appium_new_command_timeout",
                "value": 120,
                "desc": "两条appium命令间的最长时间间隔，若超过这个时间，appium会自动结束并退出app，单位为秒"
            },
            {
                "name": "app_ui_report_addr",
                "value": "/#/app-test/report-show?id=",
                "desc": "展示测试报告页面的前端地址（用于即时通讯通知）"
            }
        ]
    }
    for conf_type, conf_list in conf_dict.items():
        for conf in conf_list:
            if not await Config.filter(name=conf["name"]).first():
                conf["type"] = type_dict[conf_type]
                await Config.model_create(conf)
                print_item_delimiter(f'配置【{conf["name"]}】创建成功')
    print_type_delimiter("配置创建完成")


async def init_script():
    """ 初始化脚本文件模板 """
    print_type_delimiter("开始创建函数文件模板")
    func_file_list = [
        {"name": "base_template", "num": 0, "desc": "自定义函数文件使用规范说明"},
        {"name": "utils_template", "num": 1, "desc": "工具类自定义函数操作模板"},
        {"name": "database_template", "num": 2, "desc": "数据库操作类型的自定义函数文件模板"}
    ]
    if not await Script.filter().first():
        for data in func_file_list:
            with open(os.path.join("static", f'{data["name"]}.py'), "r", encoding="utf-8") as fp:
                func_data = fp.read()
            data["script_data"] = func_data
            await Script.model_create(data)
            print_item_delimiter(f'函数文件【{data["name"]}】创建成功')
    print_type_delimiter("函数文件模板创建完成")


async def init_run_env():
    """ 初始化运行环境 """
    print_type_delimiter("开始创建运行环境")
    env_dict = [
        {"name": "开发环境", "code": "dev_qa", "desc": "开发环境", "group": "QA环境"},
        {"name": "测试环境", "code": "test_qa", "desc": "测试环境", "group": "QA环境"},
        {"name": "uat环境", "code": "uat_qa", "desc": "uat环境", "group": "QA环境"},
        {"name": "生产环境", "code": "production_qa", "desc": "生产环境", "group": "QA环境"},
    ]
    if not await RunEnv.filter().first():  # 没有运行环境则创建
        for index, env in enumerate(env_dict):
            if not await RunEnv.filter(code=env["code"]).first():
                env["num"] = index
                await RunEnv.model_create(env)
                print_item_delimiter(f'运行环境【{env["name"]}】创建成功')
    print_type_delimiter("运行环境创建完成")


async def init_data():
    await Tortoise.init(tortoise_orm_conf, timezone="Asia/Shanghai")
    print_start_delimiter("开始初始化数据")
    await init_run_env()
    await init_permission()
    await init_role()
    await init_user()
    await init_config_type()
    await init_config()
    await init_script()
    print_start_delimiter("数据初始化完毕")


def run_init():
    run_async(init_data())


if __name__ == '__main__':
    run_init()
"""
# 1. 先初始化
aerich init -t config.tortoise_orm_conf

# 2. 初次使用生成表 和 迁移文件
aerich init-db

# 3. 模型字段有变更时， 生成迁移文件
aerich migrate

# 4. 迁移文件生成表
aerich upgrade
"""
