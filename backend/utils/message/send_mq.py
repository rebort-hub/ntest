# -*- coding: utf-8 -*-
import datetime
import struct
import uuid

import pika
import stomp
from .mq_http_sdk.mq_producer import *
from .mq_http_sdk.mq_client import *


def send_rocket_mq(host, access_id, access_key, topic, instance_id, message_body, message_tag, options: dict):
    mq_client = MQClient(host, access_id, access_key)  # 初始化client。
    producer = mq_client.get_producer(instance_id, topic)
    try:
        body = message_body if isinstance(message_body, str) else json.dumps(message_body)
        message = TopicMessage(body, message_tag)
        for key, value in options.items():  # 自定义的属性
            if value:
                message.set_message_key(value) if key.upper() == "KEYS" else message.put_property(key, value)
        re_msg = producer.publish_message(message)
        return {"status": "success", "res": f"MessageID: {re_msg.message_id}, BodyMD5: {re_msg.message_body_md5}"}
    except MQExceptionBase as error:
        return {"status": "fail", "res": error}


def send_rabbit_mq(host, port, account, password, topic, message):  # 消息生产者
    user_info = pika.PlainCredentials(account, password)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=host, port=port, credentials=user_info))
    channel = connection.channel()
    channel.queue_declare(queue=topic)  # 声明消息队列，消息将在这个队列传递，如不存在，则创建
    # 向队列插入数值 routing_key的队列名为tester，body 就是放入的消息内容，exchange指定消息在哪个队列传递，
    # 这里是空的exchange但仍然能够发送消息到队列中，因为使用的是定义的空字符串"" exchange（默认的exchange）
    channel.basic_publish(exchange='', routing_key=topic, body=message)
    connection.close()  # 关闭连接


def send_active_mq(host, port, account, password, client_id, topic, message):
    try:
        build_message = build_active_mq_body(message, topic, client_id)
        message_body, message_id = build_message[0], build_message[1]
        conn = stomp.Connection([(host, port)], keepalive=True, auto_decode=False)  # 创建STOMP连接
        conn.connect(account, password, wait=True)  # ActiveMQ的用户名和密码，默认为admin/admin
        conn.send(body=message_body, destination=topic)  # 发送消息
        conn.disconnect()  # 断开连接
        return {"status": "success", "res": f"messageId: {message_id}"}
    except Exception as error:
        return {"status": "fail", "res": error}


class ActiveMqBinaryMessage:
    def __init__(self, header, payload: bytes):
        self.header = header
        self.payload = payload


class ActiveMqMessageHeader:
    def __init__(self, topic: str, client_id):
        self.messageId = int(uuid.uuid1().int >> 72)
        self.fromId = client_id
        self.topic = topic
        self.timestamp = int(time.time())


def writeMUTF(to_write: str):  # 将Python的值根据格式符，转换为字节(Byte)类型
    to_write_len = len(to_write)
    compose_format = '!H' + str(
        to_write_len) + 's'  # 格式符, !表示网络大端字节对齐用于配合C语言，H表示integer是C语言中的unsigned short, s表示string是C语言中的char[]型
    return struct.pack(compose_format, to_write_len, to_write.encode(
        'utf-8'))  # 将Python的值根据格式符，转换为字节流, buffer是2个字节的toWriteLen，len长度char[]型的toWrite.encode('utf-8')


def build_active_mq_body(content, topic: str, client_id: str):
    if isinstance(content, bytes) is False:
        if isinstance(content, str) is False and isinstance(content, bytearray) is False:
            content = json.dumps(content)
        content = content.encode('utf-8')

    header = ActiveMqMessageHeader(topic, client_id)
    binary_message = ActiveMqBinaryMessage(header, content)

    bytes_to_send = struct.pack('!qqi', header.messageId, header.timestamp, len(binary_message.payload))
    bytes_to_send += writeMUTF(topic)
    bytes_to_send += writeMUTF(client_id)
    bytes_to_send += binary_message.payload
    return bytes_to_send, header.messageId


if __name__ == "__main__":
    pass