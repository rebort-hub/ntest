# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields, pydantic_model_creator
from app.schemas.enums import DataStatusEnum, ApiBodyTypeEnum


class BaseStep(BaseModel):
    """ 测试步骤基类表 """

    name = fields.CharField(255, default="", description="步骤名称")
    desc = fields.TextField(default="", description="步骤描述")
    num = fields.IntField(null=True, default=0, description="步骤序号，执行顺序按此序号来")
    status = fields.CharEnumField(DataStatusEnum, default=DataStatusEnum.ENABLE,
                                  description="是否执行此步骤, enable/disable，默认enable")
    run_times = fields.IntField(default=1, description="执行次数，默认执行1次")
    up_func = fields.JSONField(default=[], description="步骤执行前的函数")
    down_func = fields.JSONField(default=[], description="步骤执行后的函数")
    skip_if = fields.JSONField(
        default=[
            {
                "skip_type": "and", "data_source": None, "check_value": None, "comparator": None, "data_type": None,
                "expect": None
            }
        ],
        description="是否跳过的判断条件")
    skip_on_fail = fields.IntField(default=1, description="当用例有失败的步骤时，是否跳过此步骤，1跳过，0不跳过，默认跳过")
    data_driver = fields.JSONField(default=[], description="数据驱动，若此字段有值，则走数据驱动的解析")
    quote_case = fields.IntField(null=True, description="引用用例的id")
    case_id = fields.IntField(index=True, description="步骤所在的用例的id")

    class Meta:
        abstract = True  # 不生成表

    @classmethod
    async def set_has_step_for_step(cls, step_list, case_model):
        """ 增加步骤下是否有步骤的标识（是否为引用用例，为引用用例的话，该用例下是否有步骤）"""
        data_list = []
        for step in step_list:
            if isinstance(step, dict) is False:
                step = dict(step)

            if step["quote_case"]:  # 若果是引用用例，把对应用例的入参出参、用例来源一起返回
                case = await case_model.filter(id=step["quote_case"]).first()
                if case:  # 如果手动从数据库删过数据，可能没有
                    step["children"] = []
                    step["desc"] = case.desc
                    step["skip_if"] = case.skip_if
                    step["variables"] = case.variables
                    step["output"] = case.output

            data_list.append(step)
        return data_list

    @classmethod
    async def set_has_step_for_case(cls, case_list):
        """ 增加是否有步骤的标识 """
        data_list = []
        for case in case_list:
            if isinstance(case, dict) is False:
                case = dict(case)
            step = await cls.filter(case_id=case["id"]).first()
            case["hasStep"] = step is not None
            case["children"] = []
            data_list.append(case)
        return data_list


class ApiStep(BaseStep):
    """ 测试步骤表 """

    time_out = fields.IntField(default=60, null=True, description="request超时时间，默认60秒")
    replace_host = fields.IntField(default=0,
                                   description="是否使用用例所在项目的域名，1使用用例所在服务的域名，0使用步骤对应接口所在服务的域名")
    headers = fields.JSONField(default=[{"key": None, "remark": None, "value": None}], description="头部信息")
    params = fields.JSONField(default=[{"key": None, "value": None}], description="url参数")
    data_form = fields.JSONField(
        default=[{"data_type": None, "key": None, "remark": None, "value": None}],
        description="form-data参数")
    data_urlencoded = fields.JSONField(default={}, description="form_urlencoded参数")
    data_json = fields.JSONField(default={}, description="json参数")
    data_text = fields.TextField(null=True, default="", description="文本参数")
    body_type = fields.CharEnumField(ApiBodyTypeEnum, default=ApiBodyTypeEnum.JSON,
                                     description="请求体数据类型，json/form/text/urlencoded")
    extracts = fields.JSONField(
        default=[
            {"status": 1, "key": None, "data_source": None, "value": None, "remark": None, "update_to_header": None}],
        description="提取信息"
    )
    validates = fields.JSONField(
        default=[{"status": 1, "key": None, "value": None, "remark": None, "data_type": None, "data_source": None,
                  "validate_type": "data", "validate_method": None}],
        description="断言信息")

    pop_header_filed = fields.JSONField(default=[], description="头部参数中去除指定字段")

    api_id = fields.IntField(null=True, description="步骤所引用的接口的id")
    allow_redirect = fields.BooleanField(default=False, description="是否允许重定向")

    class Meta:
        table = "api_test_step"
        table_description = "接口测试用例步骤表"


class AppStep(BaseStep):
    """ 测试步骤表 """

    wait_time_out = fields.IntField(default=10, null=True, description="等待元素出现的时间，默认10秒")
    execute_type = fields.CharField(255, description="执行方式")
    send_keys = fields.CharField(255, description="要输入的文本内容")
    extracts = fields.JSONField(
        default=[{"key": None, "extract_type": None, "value": None, "remark": None}],
        description="提取信息"
    )
    validates = fields.JSONField(
        default=[{"data_source": None, "key": None, "validate_type": "page", "validate_method": None, "data_type": None,
                  "value": None, "remark": None}],
        description="断言信息")
    element_id = fields.IntField(null=True, description="步骤所引用的元素的id")

    class Meta:
        table = "app_ui_test_step"
        table_description = "APP测试步骤表"


class UiStep(BaseStep):
    """ 测试步骤表 """

    wait_time_out = fields.IntField(default=10, null=True, description="等待元素出现的时间，默认10秒")
    execute_type = fields.CharField(255, description="执行方式")
    send_keys = fields.CharField(255, description="要输入的文本内容")
    extracts = fields.JSONField(
        default=[{"key": None, "extract_type": None, "value": None, "remark": None}],
        description="提取信息"
    )
    validates = fields.JSONField(
        default=[{"data_source": None, "key": None, "validate_type": "page", "validate_method": None, "data_type": None,
                  "value": None, "remark": None}],
        description="断言信息")
    element_id = fields.IntField(null=True, description="步骤所引用的元素的id")

    class Meta:
        table = "web_ui_test_step"
        table_description = "web-ui测试步骤表"


UiStepPydantic = pydantic_model_creator(UiStep, name="UiStep")
AppStepPydantic = pydantic_model_creator(AppStep, name="AppStep")
ApiStepPydantic = pydantic_model_creator(ApiStep, name="ApiStep")
