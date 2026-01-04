# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields, pydantic_model_creator


class SwaggerDiffRecord(BaseModel):
    """ yapi数据比对记录 """

    name = fields.CharField(255, description="比对标识，全量比对，或者具体分组的比对")
    is_changed = fields.IntField(default=0, description="对比结果，1有改变，0没有改变")
    diff_summary = fields.TextField(description="比对结果数据")

    class Meta:
        table = "swagger_diff_record"
        table_description = "yapi数据比对记录"


class SwaggerPullLog(BaseModel):
    """ swagger拉取日志 """

    status = fields.IntField(null=True, default=1, description="拉取结果，0失败，1拉取中，2拉取成功")
    project_id = fields.IntField(description="服务id")
    desc = fields.TextField(null=True, description="备注")
    pull_args = fields.JSONField(default=[], description="拉取时的参数")

    class Meta:
        table = "auto_test_swagger_pull_log"
        table_description = "swagger拉取日志"

    async def pull_fail(self, project, desc=None):
        """ 拉取失败 """
        await self.model_update({"status": 0, "desc": desc})
        await project.last_pull_is_fail()

    async def pull_success(self, project):
        """ 拉取成功 """
        await self.model_update({"status": 2})
        await project.last_pull_is_success()


SwaggerDiffRecordPydantic = pydantic_model_creator(SwaggerDiffRecord, name="SwaggerDiffRecord")
SwaggerPullLogPydantic = pydantic_model_creator(SwaggerPullLog, name="SwaggerPullLog")
