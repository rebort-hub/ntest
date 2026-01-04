# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields, pydantic_model_creator


class FuncErrorRecord(BaseModel):
    """ 自定义函数执行错误记录表 """

    name = fields.CharField(255, null=True, description="错误title")
    detail = fields.TextField(null=True, default=None, description="错误详情")

    class Meta:
        table = "func_error_record"
        table_description = "自定义函数执行错误记录表"


FuncErrorRecordPydantic = pydantic_model_creator(FuncErrorRecord, name="FuncErrorRecord")
