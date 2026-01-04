from ..base_model import BaseModel, fields, pydantic_model_creator


class AutoTestUser(BaseModel):
    """ 自动化测试用户表 """

    mobile = fields.CharField(128, index=True, null=True, default=None, description="手机号")
    company_name = fields.CharField(128, null=True, default=None, description="公司名")
    access_token = fields.CharField(2048, null=True, default=None, description="access_token")
    refresh_token = fields.CharField(2048, null=True, default=None, description="refresh_token")
    user_id = fields.CharField(128, null=True, default=None, description="用户id")
    company_id = fields.CharField(128, null=True, default=None, description="公司id")
    password = fields.CharField(256, null=True, default=None, description="密码")
    role = fields.CharField(128, null=True, default=None, description="角色")
    comment = fields.CharField(1024, null=True, default=None, description="备注")
    env = fields.CharField(64, index=True, null=True, default=None, description="数据对应的环境")

    class Meta:
        table = "auto_test_user"
        table_description = "自动化测试用户数据池"


class DataPool(BaseModel):
    """ 数据池 """

    env = fields.CharField(64, null=True, index=True, default=None, description="数据对应的环境")
    mobile = fields.CharField(128, null=True, index=True, default=None, description="手机号")
    password = fields.CharField(256, null=True, default=None, description="密码")
    business_order_no = fields.CharField(256, null=True, default=None, description="业务流水号")
    amount = fields.CharField(64, null=True, default=None, description="金额")
    business_status = fields.CharField(64, null=True, default=None, description="业务状态，自定义")
    use_status = fields.CharField(64, null=True, default="not_used",
                                  description="使用状态，未使用：not_used、使用中：in_use、已使用：used")
    desc = fields.CharField(256, null=True, default=None, description="备注")

    class Meta:
        table = "auto_test_data_pool"
        table_description = "测试数据池"


class WebSocketMessage(BaseModel):
    command = fields.CharField(16, null=True, default=None, description="消息command")
    message_id = fields.CharField(64, null=True, index=True, default=None, description="message-id")
    destination = fields.CharField(64, null=True, index=True, default=None, description="destination")
    headers = fields.TextField(null=True, default=None, description="headers")
    message_body = fields.TextField(null=True, default=None, description="消息内容")

    class Meta:
        table = "auto_test_websocket"
        table_description = "WebSocket消息监控"

AutoTestUserPydantic = pydantic_model_creator(AutoTestUser, name="AutoTestUser")
DataPoolPydantic = pydantic_model_creator(DataPool, name="DataPool")
