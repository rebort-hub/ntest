from ..base_model import SaveRequestLog, fields, pydantic_model_creator


class CallBack(SaveRequestLog):
    """ 自动化测试回调记录 """

    status = fields.IntField(default=1, description="回调状态, 0失败，1回调中，2成功")
    result = fields.JSONField(default={}, null=True, description="回调响应")

    class Meta:
        table = "auto_test_call_back"
        table_description = "自动化测试回调流水线记录"

    def success(self, call_back_res):
        """ 回调成功 """
        self.model_update({"status": 2, "result": call_back_res})

    def fail(self):
        """ 回调失败 """
        self.model_update({"status": 0})


CallBackPydantic = pydantic_model_creator(CallBack, name="CallBack")
