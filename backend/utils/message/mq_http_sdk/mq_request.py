# coding=utf-8


class RequestBase:
    def __init__(self, instance_id):
        self.method = ""
        if instance_id is None:
            self.instance_id = ""
        else:
            self.instance_id = instance_id


class ResponseBase:
    def __init__(self):
        self.status = -1
        self.header = {}
        self.error_data = ""

    def get_req_id(self):
        return self.header.get("x-mq-request-id")


class PublishMessageRequest(RequestBase):
    def __init__(self, instance_id, topic_name, message_body, message_tag="", properties=""):
        RequestBase.__init__(self, instance_id)
        self.topic_name = topic_name
        self.message_body = message_body
        self.message_tag = message_tag
        self.properties = properties
        self.method = "POST"


class PublishMessageResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
        self.message_id = ""
        self.message_body_md5 = ""
        self.receipt_handle = ""


class ConsumeMessageRequest(RequestBase):
    def __init__(self, instance_id, topic_name, consumer, batch_size, message_tag, wait_seconds=-1):
        RequestBase.__init__(self, instance_id)
        self.topic_name = topic_name
        self.consumer = consumer
        self.batch_size = batch_size
        self.message_tag = message_tag
        self.wait_seconds = wait_seconds
        self.method = "GET"
        self.trans = ""

    def set_trans_pop(self):
        self.trans = "pop"

    def set_order(self):
        self.trans = "order"


class ConsumeMessageResponseEntry:
    def __init__(self):
        self.consumed_times = -1
        self.publish_time = -1
        self.first_consume_time = -1
        self.message_body = ""
        self.message_id = ""
        self.message_body_md5 = ""
        self.next_consume_time = ""
        self.receipt_handle = ""
        self.message_tag = ""
        self.properties = ""


class ConsumeMessageResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
        self.message_list = []


class AckMessageRequest(RequestBase):
    def __init__(self, instance_id, topic_name, consumer, receipt_handle_list):
        RequestBase.__init__(self, instance_id)
        self.topic_name = topic_name
        self.consumer = consumer
        self.receipt_handle_list = receipt_handle_list
        self.method = "DELETE"
        self.trans = ""

    def set_trans_commit(self):
        self.trans = "commit"

    def set_trans_rollback(self):
        self.trans = "rollback"


class AckMessageResponse(ResponseBase):
    def __init__(self):
        ResponseBase.__init__(self)
