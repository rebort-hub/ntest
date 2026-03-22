# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields, pydantic_model_creator


class BaseModule(BaseModel):
    """ 模块基类表 """

    name = fields.CharField(255, default="", description="模块名")
    num = fields.IntField(null=True, description="模块在对应服务下的序号")
    parent = fields.IntField(null=True, description="父级模块id")
    project_id = fields.IntField(index=True, description="所属的服务id")

    class Meta:
        abstract = True  # 不生成表


class ApiModule(BaseModule):
    """ 模块表 """

    controller = fields.CharField(255, null=True, description="当前模块在swagger上的controller名字")

    class Meta:
        table = "api_test_module"
        table_description = "接口测试模块表"


class AppModule(BaseModule):
    """ 模块表 """

    class Meta:
        table = "app_ui_test_module"
        table_description = "APP测试模块表"


class UiModule(BaseModule):
    """ 模块表 """

    class Meta:
        table = "web_ui_test_module"
        table_description = "web-ui测试模块表"


ApiModulePydantic = pydantic_model_creator(ApiModule, name="ApiModule")
AppModulePydantic = pydantic_model_creator(AppModule, name="AppModule")
UiModulePydantic = pydantic_model_creator(UiModule, name="UiModule")
