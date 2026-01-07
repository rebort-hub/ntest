import os
import platform

from utils.client.test_runner import validate_func as assert_func_file
from utils.client.test_runner.webdriver_action import Actions

is_linux = platform.platform().startswith("Linux")
basedir = os.path.abspath(".")

token_secret_key = "localhost"  # 生成token的加密字符串
access_token_time_out = 60 * 60  # access_token 有效期，1个小时
refresh_token_time_out = 7 * 24 * 60 * 60  # refresh_token 有效期，7天
password_secret_key = "PASSWORD_password_secret_key"  # 密码加密的字符串，一旦生成用户，不可更改，否则两次加密密文会不一致

main_server_port = 8018  # 主程序端口
main_server_host = f'http://localhost:{main_server_port}'  # 主程序后端服务

job_server_port = 8019  # job服务端口
job_server_host = f'http://localhost:{job_server_port}/api/job'  # job服务接口

# 默认的webhook地址，用于接收系统状态通知、系统异常/错误通知...
_default_web_hook_type = 'ding_ding'  # 默认通知的webhook类型，见枚举类apps.enums.WebHookTypeEnum
_default_web_hook = 'https://oapi.dingtalk.com/robot/send?'
_web_hook_secret = ''  # secret，若是关键词模式，不用设置


# 从 testRunner.built_in 中获取断言方式并映射为字典和列表，分别给前端和运行测试用例时反射断言
assert_mapping, assert_mapping_list = {}, []
for func in dir(assert_func_file):
    if func.startswith("_") and not func.startswith("__"):
        doc = getattr(assert_func_file, func).__doc__.strip()  # 函数注释
        assert_mapping.setdefault(doc, func)
        assert_mapping_list.append({"value": doc})

# UI自动化的行为事件
action_mapping = Actions.get_action_mapping()
ui_action_mapping_dict, ui_action_mapping_list = action_mapping["mapping_dict"], action_mapping["mapping_list"]
ui_action_mapping_reverse = dict(zip(ui_action_mapping_dict.values(), ui_action_mapping_dict.keys()))

# UI自动化的断言事件
ui_assert_mapping = Actions.get_assert_mapping()
ui_assert_mapping_dict, ui_assert_mapping_list = ui_assert_mapping["mapping_dict"], ui_assert_mapping["mapping_list"]

# UI自动化的数据提取事件
extract_mapping = Actions.get_extract_mapping()
ui_extract_mapping, ui_extract_mapping_list = extract_mapping["mapping_dict"], extract_mapping["mapping_list"]
ui_extract_mapping.setdefault("自定义函数", "func")
ui_extract_mapping_list.extend([
    {"label": "常量", "value": "const"},
    {"label": "自定义变量", "value": "variable"},
    {"label": "自定义函数", "value": "func"}
])

# 跳过条件判断类型映射
skip_if_type_mapping = [
    {"label": "且", "value": "and"},
    {"label": "或", "value": "or"}
]

# 测试类型
test_type = [
    {"key": "api", "label": "接口测试"},
    {"key": "app", "label": "app测试"},
    {"key": "ui", "label": "ui测试"}
]

# 运行测试的类型
run_type = {
    "api": "接口",
    "case": "用例",
    "suite": "用例集",
    "task": "任务",
}

# 执行模式
run_model = {0: "串行执行", 1: "并行执行"}

# 请求方法
http_method = ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"]

# 创建项目/服务时，默认要同时创建的用例集列表
api_suite_list = [
    {"key": "base", "value": "基础用例集"},
    {"key": "quote", "value": "引用用例集"},
    {"key": "api", "value": "单接口用例集"},
    {"key": "process", "value": "流程用例集"},
    {"key": "make_data", "value": "造数据用例集"}
]

ui_suite_list = [
    {"key": "base", "value": "基础用例集"},
    {"key": "quote", "value": "引用用例集"},
    {"key": "process", "value": "流程用例集"},
    {"key": "make_data", "value": "造数据用例集"}
]

# 数据提取类型
extracts_mapping = [
    {"label": "响应体", "value": "content"},
    {"label": "响应头部信息", "value": "headers"},
    {"label": "响应cookies", "value": "cookies"},
    {"label": "正则表达式（从响应体提取）", "value": "regexp"},
    {"label": "常量", "value": "const"},
    {"label": "自定义变量", "value": "variable"},
    {"label": "自定义函数", "value": "func"},
    {"label": "其他（常量、自定义变量、自定义函数）", "value": "other"}
]

# python数据类型
data_type_mapping = [
    {"label": "普通字符串", "value": "str"},
    {"label": "json字符串", "value": "json"},
    {"label": "整数", "value": "int"},
    {"label": "小数", "value": "float"},
    {"label": "列表", "value": "list"},
    {"label": "字典", "value": "dict"},
    {"label": "布尔值True", "value": "true"},
    {"label": "布尔值False", "value": "false"},
    {"label": "自定义函数", "value": "func"},
    {"label": "自定义变量", "value": "variable"}
]

# ui自动化支持的浏览器
browser_name = {
    "chrome": "chrome",
    "gecko": "火狐"
}

# 运行app自动化的服务器设备系统映射
server_os_mapping = ["Windows", "Mac", "Linux"]

# 运行app自动化的手机设备系统映射
phone_os_mapping = ["Android", "iOS"]

# APP模拟键盘输入的code
app_key_code = {
    "7": "按键'0'",
    "8": "按键'1'",
    "9": "按键'2'",
    "10": "按键'3'",
    "11": "按键'4'",
    "12": "按键'5'",
    "13": "按键'6'",
    "14": "按键'7'",
    "15": "按键'8'",
    "16": "按键'9'",
    "29": "按键'A'",
    "30": "按键'B'",
    "31": "按键'C'",
    "32": "按键'D'",
    "33": "按键'E'",
    "34": "按键'F'",
    "35": "按键'G'",
    "36": "按键'H'",
    "37": "按键'I'",
    "38": "按键'J'",
    "39": "按键'K'",
    "40": "按键'L'",
    "41": "按键'M'",
    "42": "按键'N'",
    "43": "按键'O'",
    "44": "按键'P'",
    "45": "按键'Q'",
    "46": "按键'R'",
    "47": "按键'S'",
    "48": "按键'T'",
    "49": "按键'U'",
    "50": "按键'V'",
    "51": "按键'W'",
    "52": "按键'X'",
    "53": "按键'Y'",
    "54": "按键'Z'",
    "4": "返回键",
    "5": "拨号键",
    "6": "挂机键",
    "82": "菜单键",
    "3": "home键",
    "27": "拍照键"
}

# faker 造数据方法映射
make_user_info_mapping = {
    "name": "姓名",
    "ssn": "身份证号",
    "phone_number": "手机号",
    "credit_card_number": "银行卡",
    "address": "地址",
    "company": "公司名",
    "credit_code": "统一社会信用代码",
    "company_email": "公司邮箱",
    "job": "工作",
    "ipv4": "ipv4地址",
    "ipv6": "ipv6地址"
}

# faker 造数据语言映射
make_user_language_mapping = {
    'zh_CN': '简体中文',
    'en_US': '英语-美国',
    'ja_JP': '日语-日本',
    'hi_IN': '印地语-印度',
    'ko_KR': '朝鲜语-韩国',
    'es_ES': '西班牙语-西班牙',
    'pt_PT': '葡萄牙语-葡萄牙',
    'es_MX': '西班牙语-墨西哥',
    # 'ar_EG': '阿拉伯语-埃及',
    # 'ar_PS': '阿拉伯语-巴勒斯坦',
    # 'ar_SA': '阿拉伯语-沙特阿拉伯',
    # 'bg_BG': '保加利亚语-保加利亚',
    # 'cs_CZ': '捷克语-捷克',
    # 'de_DE': '德语-德国',
    # 'dk_DK': '丹麦语-丹麦',
    # 'el_GR': '希腊语-希腊',
    # 'en_AU': '英语-澳大利亚',
    # 'en_CA': '英语-加拿大',
    # 'en_GB': '英语-英国',
    # 'et_EE': '爱沙尼亚语-爱沙尼亚',
    # 'fa_IR': '波斯语-伊朗',
    # 'fi_FI': '芬兰语-芬兰',
    # 'fr_FR': '法语-法国',
    # 'hr_HR': '克罗地亚语-克罗地亚',
    # 'hu_HU': '匈牙利语-匈牙利',
    # 'hy_AM': '亚美尼亚语-亚美尼亚',
    # 'it_IT': '意大利语-意大利',
    # 'ka_GE': '格鲁吉亚语-格鲁吉亚',
    # 'lt_LT': '立陶宛语-立陶宛',
    # 'lv_LV': '拉脱维亚语-拉脱维亚',
    # 'ne_NP': '尼泊尔语-尼泊尔',
    # 'nl_NL': '德语-荷兰',
    # 'no_NO': '挪威语-挪威',
    # 'pl_PL': '波兰语-波兰',
    # 'pt_BR': '葡萄牙语-巴西',
    # 'ru_RU': '俄语-俄国',
    # 'sl_SI': '斯诺文尼亚语-斯诺文尼亚',
    # 'sv_SE': '瑞典语-瑞典',
    # 'tr_TR': '土耳其语-土耳其',
    # 'uk_UA': '乌克兰语-乌克兰',
    # 'zh_TW': '繁体中文'
}

auth_type = 'test_platform'  # 身份验证机制 SSO, SAML, test_platform

# ============================================================================
# OAuth 2.0 配置说明
# ============================================================================
# 推荐使用UI界面进行OAuth配置管理（/config/oauth），支持多个OAuth提供商
# 以下配置文件中的OAuth配置仅作为后备方案，当UI中没有启用的配置时才会使用
# 
# 迁移建议：
# 1. 访问 /api/config/oauth/migrate 接口将配置文件配置迁移到UI中
# 2. 在UI中管理所有OAuth配置，支持启用/禁用、设置默认等功能
# 3. 配置文件中的配置可以保留作为后备，但建议主要使用UI配置
# ============================================================================

class _Sso:
    """ 身份验证如果是走SSO，则以下配置项必须正确 """
    # 开放平台SSO地址
    sso_host = "https://xxx/oauth/" if is_linux else "https://xxxx/oauth/"
    sso_authorize_endpoint = "/oauth2/authorize"
    sso_token_endpoint = "/oauth2/token"
    client_id = "xxxx" if is_linux else "xxxx"
    client_secret = "xxxx" if is_linux else "xxxx"
    # N-Tester测试平台SSO方式登录的前端地址
    redirect_uri = "http://172.16.60.204/sso/login" if is_linux else "http://172.16.60.204/sso/login"
    front_redirect_addr = (f"{sso_host}{sso_authorize_endpoint}?"
                           f"response_type=code&client_id={client_id}&"
                           f"scope=openid&"
                           f"state=41E9zTYrLymXGyQMyFO6BxYj2HZaPzSeEv-_Rk-Vjho=&"
                           f"redirect_uri={redirect_uri}&"
                           f"nonce=DPRhbLXo-SvEnVoIw4PC9PNnBEseUUh9xzHUtdrbqG8")

# aitestrebort AI 配置
openai_api_key = os.environ.get('OPENAI_API_KEY', '')  # OpenAI API Key
openai_base_url = os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com/v1')  # OpenAI API 基础URL

# tortoise-orm 配置
tortoise_orm_conf = {
    'connections': {
        'default': {
            # 连接字符串的形式特殊符号（#）会被解析为分隔符，所以用指定参数的形式
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                "echo": True if not is_linux else False,  # 非Linux则打印sql语句

                # 支持环境变量配置
                'host': os.environ.get('DB_HOST', 'localhost'),
                'port': os.environ.get('DB_PORT', '3306'),
                'user': os.environ.get('DB_USER', 'root'),
                'password': os.environ.get('DB_PASSWORD', 'Rebort'),
                'database': os.environ.get('DB_NAME', 'test_platform')
            }

        }
    },
    'apps': {
        'test_platform': {
            'models': [
                "aerich.models",  # 数据库迁移要用
                'app.models.autotest.model_factory',
                'app.models.system.model_factory',
                'app.models.config.model_factory',
                'app.models.assist.model_factory',
                'app.models.manage.model_factory',
                # aitestrebort 集成模块
                'app.models.aitestrebort.project',
                'app.models.aitestrebort.testcase',
                'app.models.aitestrebort.automation',
                'app.models.aitestrebort.knowledge',  # 知识库模块
                'app.models.aitestrebort.requirements',  # 需求管理模块
            ],
            "default_connection": "default",  # 数据库迁移会用到
        }
    },
    "timezone": "Asia/Shanghai"
}