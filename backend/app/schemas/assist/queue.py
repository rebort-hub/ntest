from typing import Optional, Union
from pydantic import Field

from ..base_form import PaginationForm, BaseForm, ChangeSortForm
from ...schemas.enums import QueueTypeEnum

class GetQueueInstanceListForm(PaginationForm):
    host: Optional[str] = Field(default=None, title="队列实例地址")
    queue_type: Optional[str] = Field(default=None, title="队列类型")
    instance_id: Optional[str] = Field(default=None, title="rocket_mq 实例id")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.host:
            filter_dict["host__icontains"] = self.host
        if self.queue_type:
            filter_dict["queue_type"] = self.queue_type
        if self.instance_id:
            filter_dict["instance_id__icontains"] = self.instance_id
        return filter_dict


class GetQueueInstanceForm(BaseForm):
    id: int = Field(..., title="队列实例数据id")


class CreatQueueInstanceForm(BaseForm):
    queue_type: QueueTypeEnum = Field(title="队列类型", description="rocket_mq、rabbit_mq、redis，目前只支持mq")
    instance_id: Optional[str] = Field(default=None, title="rocket_mq 实例id")
    host: str = Field(..., title="地址")
    port: Optional[int] = Field(default=None, title="端口")
    account: Optional[str] = Field(default=None, title="rabbit_mq - 账号")
    password: Optional[str] = Field(default=None, title="rabbit_mq - 密码")
    access_id: Optional[str] = Field(default=None, title="rocket_mq - access_id")
    access_key: Optional[str] = Field(default=None, title="rocket_mq - access_key")
    desc: Optional[str] = Field(default=None, title="描述")


class EditQueueInstanceForm(GetQueueInstanceForm):
    """ 修改消息队列实例 """
    queue_type: QueueTypeEnum = Field(title="队列类型", description="rocket_mq、rabbit_mq、redis，目前只支持mq")
    instance_id: Optional[str] = Field(default=None, title="rocket_mq 实例id")
    host: str = Field(..., title="地址")
    desc: Optional[str] = Field(default=None, title="描述")


class GetQueueTopicListForm(PaginationForm):
    instance_id: Optional[str] = Field(default=None, title="队列实例数据id")
    topic: Optional[str] = Field(default=None, title="topic名字")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.instance_id:
            filter_dict["instance_id"] = self.instance_id
        if self.topic:
            filter_dict["topic__icontains"] = self.topic
        return filter_dict


class GetQueueTopicForm(BaseForm):
    id: int = Field(..., title="topic id")


class CreatQueueTopicForm(BaseForm):
    """ 创建消息队列 """
    instance_id: int = Field(..., title="所属消息队列实例数据id")
    topic: Optional[str] = Field(default=None, title="rocket_mq对应topic，rabbit_mq对应queue_name")
    desc: Optional[str] = Field(default=None, title="备注")


class EditQueueTopicForm(GetQueueTopicForm, CreatQueueTopicForm):
    """ 修改消息队列 """


class SendMessageForm(GetQueueTopicForm):
    """ 发送消息 """
    tag: Optional[str] = Field(default=None, title="tag")
    options: Optional[dict] = Field({}, title="用于指定参数，KEYS、或者其他自定义参数")
    message: Union[list, dict, str] = Field({}, title="消息内容")
    message_type: str = Field(..., title="消息类型")


class GetQueueMsgLogForm(PaginationForm):
    """ 获取消息队列的消息记录列表 """
    topic_id: int = Field(..., title="队列id")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        return {"topic_id": self.topic_id}
