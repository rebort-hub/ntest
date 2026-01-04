# coding=utf-8

from .mq_request import *
from .mq_tool import *
from .mq_exception import *
from .mq_consumer import Message

try:
    import json
except ImportError as e:
    import simplejson as json


class MQProducer:
    def __init__(self, instance_id, topic_name, mq_client, debug=False):
        if instance_id is None:
            self.instance_id = ""
        else:
            self.instance_id = instance_id
        self.topic_name = topic_name
        self.mq_client = mq_client
        self.debug = debug

    def set_debug(self, debug):
        self.debug = debug

    def publish_message(self, message):
        """ 发送消息

            @type message: TopicMessage object
            @param message: 发布的TopicMessage object

            @rtype: TopicMessage object
            @return: 消息发布成功的返回属性，包含MessageId和MessageBodyMD5

            @note: Exception
            :: MQClientParameterException  参数格式异常
            :: MQClientNetworkException    网络异常
            :: MQServerException           处理异常
        """
        msg_properties_str = MQUtils.map_to_string(message.properties)
        req = PublishMessageRequest(self.instance_id, self.topic_name, message.message_body, message.message_tag,
                                    msg_properties_str)
        resp = PublishMessageResponse()
        self.mq_client.publish_message(req, resp)
        self.debuginfo(resp)
        return self.__publish_resp2msg__(resp)

    def debuginfo(self, resp):
        if self.debug:
            print("===================DEBUG INFO===================")
            print("RequestId: %s" % resp.header["x-mq-request-id"])
            print("================================================")

    def __publish_resp2msg__(self, resp):
        msg = TopicMessage()
        msg.message_id = resp.message_id
        msg.message_body_md5 = resp.message_body_md5
        msg.receipt_handle = resp.receipt_handle
        return msg


class TopicMessage:
    def __init__(self, message_body="", message_tag=""):
        """ Specify information of TopicMessage

            @note: publish_message params
            :: message_body        string
            :: message_tag         string, used to filter message

            @note: publish_message response information
            :: message_id
            :: message_body_md5
            :: receipt_handle       string, only publish transaction msg contains, is valid
                                    before TransCheckImmunityTime
        """
        self.message_body = message_body
        self.message_tag = message_tag
        self.properties = {}

        self.message_id = ""
        self.message_body_md5 = ""
        self.receipt_handle = ""

    def set_message_body(self, message_body):
        self.message_body = message_body

    def set_message_tag(self, message_tag):
        self.message_tag = message_tag

    def set_message_key(self, key):
        """ Set Message Key
            @type key: str
            @param key: message key
        """
        self.properties["KEYS"] = str(key)

    def set_trans_check_immunity_time(self, time_in_seconds):
        """ 在消息属性中添加第一次消息回查的最快时间，单位秒，并且表征这是一条事务消息
            @type time_in_seconds: int
            @param time_in_seconds: 第一次消息事务回查的时间，单位:秒
        """
        self.properties["__TransCheckT"] = str(time_in_seconds)

    def set_start_deliver_time(self, time_in_millis):
        """ 定时消息，单位毫秒（ms），在指定时间戳（当前时间之后）进行投递。
            @type time_in_millis: long
            @param time_in_millis: 定时时间戳，单位:秒
        """
        self.properties["__STARTDELIVERTIME"] = str(time_in_millis)

    def set_sharding_key(self, sharding_key):
        """ 分区顺序消息中区分不同分区的关键字段，sharding key 于普通消息的 key 是完全不同的概念。
            全局顺序消息，该字段可以设置为任意非空字符串。
            @type sharding_key: str
            @param sharding_key: 分区消息键值
        """
        self.properties["__SHARDINGKEY"] = sharding_key

    def put_property(self, key, value):
        """ 设置消息的属性
            @type key: str
            @param key: 属性键

            @type value: str
            @param value: 属性值
        """
        self.properties[str(key)] = str(value)


class MQTransProducer(MQProducer):
    def __init__(self, instance_id, topic_name, group_id, mq_client, debug=False):
        MQProducer.__init__(self, instance_id, topic_name, mq_client, debug)
        if group_id is None or group_id == "":
            raise MQClientParameterException("InitMQTransProducerError", "groupId is None or empty")
        self.group_id = group_id

    def consume_half_message(self, batch_size=1, wait_seconds=-1):
        """ 消费事务半消息

            @type batch_size: int
            @param batch_size: 本次请求最多获取的消息条数，1~16

            @type wait_seconds: int
            @param wait_seconds: 本次请求的长轮询时间，单位：秒，1～30

            @rtype: list of Message object
            @return 多条事务半消息消息，包含消息的基本属性、下次可消费时间和临时句柄

            @note: Exception
            :: MQClientParameterException  参数格式异常
            :: MQClientNetworkException    网络异常
            :: MQServerException           处理异常
        """
        req = ConsumeMessageRequest(self.instance_id, self.topic_name, self.group_id, batch_size, "", wait_seconds)
        req.set_trans_pop()
        resp = ConsumeMessageResponse()
        self.mq_client.consume_message(req, resp)
        self.debuginfo(resp)
        return self.__batchrecv_resp2msg__(resp)

    def commit(self, receipt_handle):
        """提交事务消息

            @type receipt_handle: basestring
            @param receipt_handle: consume_half_message返回的单条消息句柄或者是发送事务消息返回的句柄

            @note: Exception
            :: MQClientParameterException  参数格式异常
            :: MQClientNetworkException    网络异常
            :: MQServerException           处理异常
        """
        req = AckMessageRequest(self.instance_id, self.topic_name, self.group_id, [receipt_handle])
        req.set_trans_commit()
        resp = AckMessageResponse()
        self.mq_client.ack_message(req, resp)
        self.debuginfo(resp)

    def rollback(self, receipt_handle):
        """取消事务消息

            @type receipt_handle: basestring
            @param receipt_handle: consume_half_message返回的单条消息句柄或者是发送事务消息返回的句柄

            @note: Exception
            :: MQClientParameterException  参数格式异常
            :: MQClientNetworkException    网络异常
            :: MQServerException           处理异常
        """
        req = AckMessageRequest(self.instance_id, self.topic_name, self.group_id, [receipt_handle])
        req.set_trans_rollback()
        resp = AckMessageResponse()
        self.mq_client.ack_message(req, resp)
        self.debuginfo(resp)

    def __batchrecv_resp2msg__(self, resp):
        msg_list = []
        for entry in resp.message_list:
            msg = Message()
            msg.message_id = entry.message_id
            msg.message_body_md5 = entry.message_body_md5
            msg.consumed_times = entry.consumed_times
            msg.publish_time = entry.publish_time
            msg.first_consume_time = entry.first_consume_time
            msg.message_body = entry.message_body
            msg.next_consume_time = entry.next_consume_time
            msg.receipt_handle = entry.receipt_handle
            msg.message_tag = entry.message_tag
            msg.properties = MQUtils.string_to_map(entry.properties)
            msg_list.append(msg)
        return msg_list

