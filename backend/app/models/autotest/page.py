# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields, pydantic_model_creator
from app.schemas.enums import ApiLevelEnum, ApiMethodEnum, DataStatusEnum, ApiBodyTypeEnum


class BaseApi(BaseModel):
    """ 页面表 """
    name = fields.CharField(255, default="", description="接口名称")
    num = fields.IntField(null=True, description="接口序号")
    desc = fields.CharField(255, null=True, default="", description="接口描述")
    project_id = fields.IntField(null=True, index=True, description="所属的服务id")
    module_id = fields.IntField(null=True, index=True, description="所属的模块id")

    class Meta:
        abstract = True  # 不生成表


class ApiMsg(BaseApi):
    """ 接口表 """

    time_out = fields.IntField(default=60, null=True, description="request超时时间，默认60秒")
    addr = fields.CharField(255, null=True, description="接口地址")
    method = fields.CharEnumField(ApiMethodEnum, default=ApiMethodEnum.GET, description="请求方式")
    level = fields.CharEnumField(ApiLevelEnum, default=ApiLevelEnum.P1, description="接口重要程度：P0、P1、P2")
    headers = fields.JSONField(default=[{"key": None, "value": None, "remark": None}], description="头部信息")
    params = fields.JSONField(default=[{"key": None, "value": None, "remark": None}], description="url参数")
    body_type = fields.CharEnumField(ApiBodyTypeEnum, default=ApiBodyTypeEnum.JSON,
                                     description="请求体数据类型，json/form/text/urlencoded")
    data_form = fields.JSONField(
        default=[{"data_type": None, "key": None, "remark": None, "value": None}], description="form-data参数")
    data_urlencoded = fields.JSONField(default={}, description="form_urlencoded参数")
    data_json = fields.JSONField(default={}, description="json参数")
    data_text = fields.TextField(null=True, description="文本参数")
    response = fields.JSONField(default={}, description="响应对象")
    extracts = fields.JSONField(
        default=[
            {"status": 1, "key": None, "data_source": None, "value": None, "remark": None, "update_to_header": None}],
        description="提取信息"
    )
    validates = fields.JSONField(
        default=[{"status": 1, "key": None, "value": None, "remark": None, "data_type": None, "data_source": None,
                  "validate_type": "data", "validate_method": None}],
        description="断言信息")
    status = fields.CharEnumField(
        DataStatusEnum, default=DataStatusEnum.ENABLE, description="此接口状态，对应swagger的废弃状态, enable/disable")
    use_count = fields.IntField(default=0, description="被引用次数，即多少个步骤直接使用了此接口")
    mock_response = fields.JSONField(default={}, comment="mock响应对象，用于前端提前对接后端进行调试")

    class Meta:
        table = "api_test_api"
        table_description = "接口测试接口信息表"


class AppPage(BaseApi):
    """ 页面表 """

    class Meta:
        table = "app_ui_test_page"
        table_description = "APP测试页面表"


class UiPage(BaseApi):
    """ 页面表 """

    addr = fields.CharField(255, null=True, default='', description="地址")

    class Meta:
        table = "web_ui_test_page"
        table_description = "web-ui测试页面表"


ApiMsgPydantic = pydantic_model_creator(ApiMsg, name="ApiMsg")
AppPagePydantic = pydantic_model_creator(AppPage, name="AppPage")
UiPagePydantic = pydantic_model_creator(UiPage, name="UiPage")
