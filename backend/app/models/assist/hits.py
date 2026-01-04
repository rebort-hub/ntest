# -*- coding: utf-8 -*-
from datetime import datetime

from ..base_model import BaseModel, fields, pydantic_model_creator


class Hits(BaseModel):
    """ 自动化测试触发的问题记录 """

    date = fields.DatetimeField(default=datetime.now, description="问题触发日期")
    hit_type = fields.CharField(128, default=None, description="问题类型")
    hit_detail = fields.TextField(null=True, default=None, description="问题内容")
    test_type = fields.CharField(8, default=None, description="测试类型，接口、app、ui")
    project_id = fields.IntField(index=True, description="服务id")
    env = fields.CharField(128, index=True, description="运行环境")
    record_from = fields.IntField(index=True, default=1, description="数据记录的来源，1、人为/2、自动")
    report_id = fields.IntField(index=True, description="测试报告id")
    desc = fields.TextField(null=True, default=None, description="备注")

    class Meta:
        table = "auto_test_hits"
        table_description = "自动化测试触发问题记录"


HitsPydantic = pydantic_model_creator(Hits, name="Hits")
