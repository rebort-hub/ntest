from enum import Enum


class AuthType(str, Enum):
    """ 身份验证类型 """
    login = "login"
    permission = "permission"
    admin = "admin"


class QueueTypeEnum(str, Enum):
    """ 消息队列类型 """
    RABBIT_MQ = "rabbit_mq"
    ROCKET_MQ = "rocket_mq"
    ACTIVE_MQ = "active_mq"
    REDIS = "redis"


class DataStatusEnum(str, Enum):
    ENABLE = "enable"
    DISABLE = "disable"


class ApiLevelEnum(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"


class ApiMethodEnum(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


class ApiBodyTypeEnum(str, Enum):
    JSON = "json"
    FORM = "form"
    TEXT = "text"
    URLENCODED = "urlencoded"


class AppiumVersionEnum(str, Enum):
     version1 = "1.x"
     version2 = "2.x"
     version3 = "3.x"

class CaseStatusEnum(int, Enum):
    """ 测试用例状态 """
    NOT_DEBUG_AND_NOT_RUN = 0  # 未调试-不执行
    DEBUG_PASS_AND_RUN = 1  # 调试通过-要执行
    DEBUG_PASS_AND_NOT_RUN = 2  # 调试通过-不执行
    NOT_DEBUG_PASS_AND_NOT_RUN = 3  # 调试不通过-不执行


class UiCaseSuiteTypeEnum(str, Enum):
    """ 用例集类型 """
    BASE = "base"  # 基础用例集
    QUOTE = "quote"  # 引用用例集
    PROCESS = "process"  # 流程用例集
    MAKE_DATA = "make_data"  # 造数据用例集


class ApiCaseSuiteTypeEnum(str, Enum):
    """ 用例集类型 """
    API = "api"  # 单接口用例集
    BASE = "base"  # 基础用例集
    QUOTE = "quote"  # 引用用例集
    PROCESS = "process"  # 流程用例集
    MAKE_DATA = "make_data"  # 造数据用例集


class ReceiveTypeEnum(str, Enum):
    """ 接收通知方式 """
    NOT_RECEIVE = "not_receive"  # 不接收
    DING_DING = "ding_ding"  # 钉钉
    WE_CHAT = "we_chat"  # 企业微信
    EMAIL = "email"  # 邮件


class WebHookTypeEnum(str, Enum):
    """ webhook枚举 """
    DING_DING = "ding_ding"  # 钉钉
    WE_CHAT = "we_chat"  # 微信
    FEI_SHU = "fei_shu"  # 飞书


class ReportStepStatusEnum(str, Enum):
    """ report_step 状态 """
    RESUME = "resume"  # 放行
    PAUSE = "pause"   # 暂停
    STOP = "stop"  # 中断


class SendReportTypeEnum(str, Enum):
    """ 发送报告方式 """
    NOT_SEND = "not_send"  # 不发送
    ALWAYS = "always"  # 始终发送
    ON_SUCCESS = "on_success"  # 全部通过时发送
    ON_FAIL = "on_fail"  # 仅用例不通过时发送


class BusinessLineBindEnvTypeEnum(str, Enum):
    """  业务线绑定环境机制 """
    AUTO = "auto"  # 新增环境时自动绑定
    HUMAN = "human"  # 新增环境后手动绑定


class TriggerTypeEnum(str, Enum):
    """ 触发测试的方式 """
    none = ""  # 空
    PIPELINE = "pipeline"  # 流水线
    PAGE = "page"  # 页面
    CRON = "cron"  # 定时任务


class TodoListEnum(str, Enum):
    """ 待办枚举 """
    TODO = "todo"
    DOING = "doing"
    TESTING = "testing"
    DONE = "done"
