# coding=utf-8

import base64
import time
import hashlib
import hmac
import platform
from . import pkg_info
from .mq_xml_handler import *
from .mq_tool import *
from .mq_http import *
from .mq_consumer import MQConsumer
from .mq_producer import MQProducer, MQTransProducer

URI_SEC_MESSAGE = "messages"
URI_SEC_TOPIC = "topics"
MQ_VERSION_HEADER = "2015-06-06"


class MQClient:
    def __init__(self, host, access_id, access_key, security_token="", debug=False, logger=None):
        """
            @type host: string
            @param host: 访问的url，例如：http://$accountid.mqrest.cn-hangzhou.aliyuncs.com

            @type access_id: string
            @param access_id: 用户的AccessId, 阿里云官网获取

            @type access_key: string
            @param access_key: 用户的AccessKey，阿里云官网获取

            @type security_token: string
            @param security_token: 如果用户使用STS Token访问，需要提供security_token

            @note: Exception
            :: MQClientParameterException host格式错误
        """
        self.host, self.is_https = self.process_host(host)
        self.access_id = access_id
        self.access_key = access_key
        self.version = MQ_VERSION_HEADER
        self.security_token = security_token
        self.logger = logger
        self.debug = debug
        self.http = MQHttp(self.host, logger=logger, is_https=self.is_https)
        if self.logger:
            self.logger.info("InitClient Host:%s Version:%s" % (host, self.version))

    def get_consumer(self, instance_id, topic_name, consumer, message_tag=""):
        """ 获取MQClient的一个Consumer对象
            @type instance_id: string
            @param instance_id: 实例ID

            @type topic_name: string
            @param topic_name: topic名字

            @type consumer: string
            @param consumer: 消费者名字/mq cid

            @type message_tag: string
            @param message_tag: 消费过滤消息的tag,可空

            @rtype: MQConsumer object
            @return: 返回该MQClient的一个Consumer对象
        """
        return MQConsumer(instance_id, topic_name, consumer, message_tag, self, self.debug)

    def get_producer(self, instance_id, topic_name):
        """ 获取MQClient的一个Producer对象
            @type instance_id: string
            @param instance_id: 实例ID

            @type topic_name: string
            @param topic_name: topic名字

            @rtype: MQProducer object
            @return: 返回该MQClient的一个Producer对象
        """
        return MQProducer(instance_id, topic_name, self, self.debug)

    def get_trans_producer(self, instance_id, topic_name, group_id):
        """ 获取MQClient的一个事务发送者(MQTransProducer)对象
            @type instance_id: string
            @param instance_id: 实例ID

            @type topic_name: string
            @param topic_name: topic名字

            @type group_id: string
            @param group_id: 控制台申请的group id

            @rtype: MQTransProducer object
            @return: 返回该MQClient的一个事务发送者(MQTransProducer)对象
        """
        return MQTransProducer(instance_id, topic_name, group_id, self, self.debug)

    def set_log_level(self, log_level):
        if self.logger:
            MQLogger.validate_loglevel(log_level)
            self.logger.setLevel(log_level)
            self.http.set_log_level(log_level)

    def close_log(self):
        self.logger = None
        self.http.close_log()

    def set_connection_timeout(self, connection_timeout):
        self.http.set_connection_timeout(connection_timeout)

    def set_keep_alive(self, keep_alive):
        self.http.set_keep_alive(keep_alive)

    def close_connection(self):
        self.http.conn.close()

    def consume_message(self, req, resp):
        # check parameter
        ConsumeMessageValidator.validate(req)

        # make request internal
        req_url = "/%s/%s/%s?consumer=%s&numOfMessages=%s" % (URI_SEC_TOPIC, req.topic_name, URI_SEC_MESSAGE, req.consumer, req.batch_size)
        if req.instance_id != "":
            req_url += "&ns=%s" % req.instance_id
        if req.wait_seconds != -1:
            req_url += "&waitseconds=%s" % req.wait_seconds
        if req.message_tag != "":
            req_url += "&tag=%s" % req.message_tag
        if req.trans != "":
            req_url += "&trans=%s" % req.trans

        req_inter = RequestInternal(req.method, req_url)
        self.build_header(req, req_inter)

        # send request
        resp_inter = self.http.send_request(req_inter)

        # handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.message_list = ConsumeMessageDecoder.decode(resp_inter.data, resp.get_req_id())
            if self.logger:
                self.logger.info("ConsumeMessage RequestId:%s TopicName:%s WaitSeconds:%s BatchSize:%s Tag:%s MessageCount:%s \
                    MessagesInfo\n%s" % (
                    resp.get_req_id(), req.topic_name, req.wait_seconds, req.batch_size, req.message_tag, len(resp.message_list), \
                    "\n".join([
                        "MessageId:%s MessageBodyMD5:%s NextConsumeTime:%s ReceiptHandle:%s PublishTime:%s ConsumedTimes:%s" % \
                        (msg.message_id, msg.message_body_md5, msg.next_consume_time, msg.receipt_handle,
                         msg.publish_time, msg.consumed_times) for msg in resp.message_list])))

    def ack_message(self, req, resp):
        # check parameter
        AckMessageValidator.validate(req)

        # make request internal
        req_url = "/%s/%s/%s?consumer=%s" % (URI_SEC_TOPIC, req.topic_name, URI_SEC_MESSAGE, req.consumer)
        if req.instance_id != "":
            req_url += "&ns=%s" % req.instance_id
        if req.trans != "":
            req_url += "&trans=%s" % req.trans

        req_inter = RequestInternal(req.method, req_url)
        req_inter.data = ReceiptHandlesEncoder.encode(req.receipt_handle_list)
        self.build_header(req, req_inter)

        # send request
        resp_inter = self.http.send_request(req_inter)

        # handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp, AckMessageDecoder)
        if self.logger:
            self.logger.info("AckMessage RequestId:%s TopicName:%s ReceiptHandles\n%s" % \
                             (resp.get_req_id(), req.topic_name, "\n".join(req.receipt_handle_list)))

    def publish_message(self, req, resp):
        # check parameter
        PublishMessageValidator.validate(req)

        # make request internal
        req_url = "/%s/%s/%s" % (URI_SEC_TOPIC, req.topic_name, URI_SEC_MESSAGE)
        if req.instance_id != "":
            req_url += "?ns=%s" % req.instance_id

        req_inter = RequestInternal(req.method, req_url)
        req_inter.data = TopicMessageEncoder.encode(req)
        self.build_header(req, req_inter)

        # send request
        resp_inter = self.http.send_request(req_inter)

        # handle result, make response
        resp.status = resp_inter.status
        resp.header = resp_inter.header
        self.check_status(resp_inter, resp)
        if resp.error_data == "":
            resp.message_id, resp.message_body_md5, resp.receipt_handle = PublishMessageDecoder.decode(resp_inter.data,
                                                                                  resp.get_req_id())
            if self.logger:
                self.logger.info("PublishMessage RequestId:%s TopicName:%s MessageId:%s MessageBodyMD5:%s" % \
                                 (resp.get_req_id(), req.topic_name, resp.message_id, resp.message_body_md5))

    ###################################################################################################
    # ----------------------internal-------------------------------------------------------------------#
    def build_header(self, req, req_inter):
        if self.http.is_keep_alive():
            req_inter.header["Connection"] = "Keep-Alive"
        if req_inter.data != "":
            req_inter.header["content-type"] = "text/xml;charset=UTF-8"
        req_inter.header["x-mq-version"] = self.version
        req_inter.header["host"] = self.host
        req_inter.header["date"] = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        req_inter.header["user-agent"] = "mq-python-sdk/%s(%s/%s;%s)" % \
                                         (pkg_info.version, platform.system(), platform.release(),
                                          platform.python_version())
        req_inter.header["Authorization"] = self.get_signature(req_inter.method, req_inter.header, req_inter.uri)
        if self.security_token != "":
            req_inter.header["security-token"] = self.security_token

    def get_signature(self, method, headers, resource):
        content_md5 = self.get_element('content-md5', headers)
        content_type = self.get_element('content-type', headers)
        date = self.get_element('date', headers)
        canonicalized_resource = resource
        canonicalized_mq_headers = ""
        if len(headers) > 0:
            x_header_list = list(headers.keys())
            x_header_list.sort()
            for k in x_header_list:
                if k.startswith('x-mq-'):
                    canonicalized_mq_headers += k + ":" + headers[k] + "\n"
        string_to_sign = "%s\n%s\n%s\n%s\n%s%s" % (
            method, content_md5, content_type, date, canonicalized_mq_headers, canonicalized_resource)
        # hmac only support str in python2.7

        if sys.version > '3':
            tmp_key = self.access_key.encode('utf-8') if isinstance(self.access_key, str) else self.access_key
            h = hmac.new(tmp_key, string_to_sign.encode('utf-8'), hashlib.sha1)
            signature = base64.b64encode(h.digest())
            signature = "MQ " + self.access_id + ":" + signature.decode('utf-8')
            return signature
        else:
            tmp_key = self.access_key.encode('utf-8') if isinstance(self.access_key, unicode) else self.access_key
            h = hmac.new(tmp_key, string_to_sign, hashlib.sha1)
            signature = base64.b64encode(h.digest())
            signature = "MQ " + self.access_id + ":" + signature
            return signature

    def get_element(self, name, container):
        if name in container:
            return container[name]
        else:
            return ""

    def check_status(self, resp_inter, resp, decoder=ErrorDecoder):
        if 200 <= resp_inter.status < 400:
            resp.error_data = ""
        else:
            resp.error_data = resp_inter.data
            if 400 <= resp_inter.status <= 600:
                excType, excMessage, reqId, hostId, subErr = decoder.decodeError(resp.error_data,
                                                                                 resp.get_req_id())
                if reqId is None:
                    reqId = resp.header["x-mq-request-id"]
                raise MQServerException(excType, excMessage, reqId, hostId, subErr)
            else:
                raise MQClientNetworkException("UnkownError", resp_inter.data, resp.get_req_id())

    def process_host(self, host):
        if host.startswith("http://"):
            if host.endswith("/"):
                host = host[:-1]
            host = host[len("http://"):]
            return host, False
        elif host.startswith("https://"):
            if host.endswith("/"):
                host = host[:-1]
            host = host[len("https://"):]
            return host, True
        else:
            raise MQClientParameterException("InvalidHost", "Only support http prototol. Invalid host:%s" % host)
