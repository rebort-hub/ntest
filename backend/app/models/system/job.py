from ..base_model import BaseModel, fields, pydantic_model_creator


class ApschedulerJobs(BaseModel):
    """ apscheduler任务表 """
    cron = fields.CharField(128, description="cron表达式")
    task_code = fields.CharField(64, null=False)
    next_run_time = fields.CharField(128, description="任务下一次运行时间")
    job_id = fields.CharField(64, null=False, description="内存中的任务id")

    class Meta:
        table = "apscheduler_jobs"
        table_description = "定时任务执行计划表"


class JobRunLog(BaseModel):
    """ 系统job执行记录 """

    func_name = fields.CharField(255, description="执行方法")
    status = fields.IntField(default=1, description="执行状态：0失败、1执行中、2执行成功")
    business_id = fields.IntField(null=True, description="业务线id")
    detail = fields.JSONField(default={}, description="执行结果数据")

    class Meta:
        table = "system_job_run_log"
        table_description = "系统job执行记录表"

    async def run_fail(self, detail=None):
        """ 执行失败 """
        await self.model_update({"status": 0, "detail": detail})

    async def run_success(self, detail):
        """ 执行成功 """
        await self.model_update({"status": 2, "detail": detail})


ApschedulerJobsPydantic = pydantic_model_creator(ApschedulerJobs, name="ApschedulerJobs")
JobRunLogPydantic = pydantic_model_creator(JobRunLog, name="JobRunLog")
