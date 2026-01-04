from ..base_model import BaseModel, fields, NumFiled
from ...schemas.enums import QueueTypeEnum


class QueueInstance(NumFiled):
    """ 消息队列 """
    
    class Meta:
        table = "auto_test_queue_instance"
        table_description = "消息队列实例管理"

    # 消息队列链接属性
    queue_type = fields.CharEnumField(QueueTypeEnum, default=QueueTypeEnum.ACTIVE_MQ, description="消息队列类型")
    instance_id = fields.CharField(128, default="test_platform_client", description="rocket_mq 对应的 instance_id")
    desc = fields.CharField(512, null=True, default=None, description="描述")

    # rabbit_mq
    host = fields.CharField(128, default="", description="rabbit_mq 地址")
    port = fields.IntField(null=True, default=None, description="rabbit_mq 端口")
    account = fields.CharField(128, null=True, default=None, description="rabbit_mq 账号")
    password = fields.CharField(128, null=True, default=None, description="rabbit_mq 密码")

    # rocket_mq
    access_id = fields.CharField(128, null=True, default=None, description="rocket_mq access_id")
    access_key = fields.CharField(128, null=True, default=None, description="rocket_mq access_key")


class QueueTopic(NumFiled):
    
    class Meta:
        table = "auto_test_queue_topic"
        table_description = "topic 管理"

    instance_id = fields.IntField(null=True, description="rocket_mq 实例数据id")
    topic = fields.CharField(128, default="", description="rocket_mq topic，rabbit_mq queue_name")
    desc = fields.CharField(512, null=True, default=None, description="描述")


class QueueMsgLog(BaseModel):

    class Meta:
        table = "auto_test_queue_message_log"
        table_description = "消息发送记录表"

    instance_id = fields.IntField(description="消息队列实例数据id")
    topic_id = fields.IntField(description="topic id")
    tag = fields.CharField(128, description="tag")
    options = fields.JSONField(description="自定义内容")
    message_type = fields.CharField(8, description="消息类型")
    message = fields.JSONField(description="消息内容")
    status = fields.TextField(description="消息发送状态")
    response = fields.TextField(description="消息发送响应")
