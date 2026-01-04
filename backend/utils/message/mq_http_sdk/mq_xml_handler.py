# coding=utf-8

import xml.dom.minidom
import sys
from .mq_exception import *
from .mq_request import *

try:
    import json
except ImportError as e:
    import simplejson as json

XMLNS = "http://mq.aliyuncs.com/doc/v1/"


class EncoderBase:
    @staticmethod
    def insert_if_valid(item_name, item_value, invalid_value, data_dic):
        if item_value != invalid_value:
            data_dic[item_name] = item_value

    @staticmethod
    def list_to_xml(tag_name1, tag_name2, data_list):
        doc = xml.dom.minidom.Document()
        rootNode = doc.createElement(tag_name1)
        rootNode.attributes["xmlns"] = XMLNS
        doc.appendChild(rootNode)
        if data_list:
            for item in data_list:
                keyNode = doc.createElement(tag_name2)
                rootNode.appendChild(keyNode)
                keyNode.appendChild(doc.createTextNode(item))
        else:
            nullNode = doc.createTextNode("")
            rootNode.appendChild(nullNode)
        return doc.toxml("utf-8")

    @staticmethod
    def dic_to_xml(tag_name, data_dic):
        doc = xml.dom.minidom.Document()
        rootNode = doc.createElement(tag_name)
        rootNode.attributes["xmlns"] = XMLNS
        doc.appendChild(rootNode)
        if data_dic:
            for k, v in list(data_dic.items()):
                keyNode = doc.createElement(k)
                if type(v) is dict:
                    for subkey, subv in list(v.items()):
                        subNode = doc.createElement(subkey)
                        subNode.appendChild(doc.createTextNode(subv))
                        keyNode.appendChild(subNode)
                else:
                    keyNode.appendChild(doc.createTextNode(v))
                rootNode.appendChild(keyNode)
        else:
            nullNode = doc.createTextNode("")
            rootNode.appendChild(nullNode)
        return doc.toxml("utf-8")


class TopicMessageEncoder:
    @staticmethod
    def encode(req):
        message = {}
        # xml only support unicode when contains Chinese
        if sys.version > '3':
            EncoderBase.insert_if_valid("MessageBody", req.message_body, "", message)
            EncoderBase.insert_if_valid("Properties", req.properties, "", message)
        else:
            msgbody = req.message_body.decode('utf-8') if isinstance(req.message_body, str) else req.message_body
            EncoderBase.insert_if_valid("MessageBody", msgbody, "", message)
            msgprops = req.properties.decode('utf-8') if isinstance(req.properties, str) else req.properties
            EncoderBase.insert_if_valid("Properties", msgprops, "", message)
        EncoderBase.insert_if_valid("MessageTag", req.message_tag, "", message)
        return EncoderBase.dic_to_xml("Message", message)


class ReceiptHandlesEncoder:
    @staticmethod
    def encode(receipt_handle_list):
        return EncoderBase.list_to_xml("ReceiptHandles", "ReceiptHandle", receipt_handle_list)


# -------------------------------------------------decode-----------------------------------------------------#
class DecoderBase:
    @staticmethod
    def xml_to_nodes(tag_name, xml_data):
        if xml_data == "":
            raise MQClientNetworkException("RespDataDamaged", "Xml data is \"\"!")

        try:
            dom = xml.dom.minidom.parseString(xml_data)
        except Exception as e:
            raise MQClientNetworkException("RespDataDamaged", xml_data)

        nodelist = dom.getElementsByTagName(tag_name)
        if not nodelist:
            raise MQClientNetworkException("RespDataDamaged",
                                            "No element with tag name '%s'.\nData:%s" % (tag_name, xml_data))

        return nodelist[0].childNodes

    @staticmethod
    def xml_to_dic(tag_name, xml_data, data_dic, req_id=None):
        try:
            for node in DecoderBase.xml_to_nodes(tag_name, xml_data):
                if node.nodeName != "#text":
                    if node.childNodes != []:
                        data_dic[node.nodeName] = node.firstChild.data
                    else:
                        data_dic[node.nodeName] = ""
        except MQClientNetworkException as e:
            raise MQClientNetworkException(e.type, e.message, req_id)

    @staticmethod
    def xml_to_listofdic(root_tagname, sec_tagname, xml_data, data_listofdic, req_id=None):
        try:
            for message in DecoderBase.xml_to_nodes(root_tagname, xml_data):
                if message.nodeName != sec_tagname:
                    continue

                data_dic = {}
                for property in message.childNodes:
                    if property.nodeName != "#text" and property.childNodes != []:
                        data_dic[property.nodeName] = property.firstChild.data
                data_listofdic.append(data_dic)
        except MQClientNetworkException as e:
            raise MQClientNetworkException(e.type, e.message, req_id)


class ConsumeMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_listofdic = []
        message_list = []
        DecoderBase.xml_to_listofdic("Messages", "Message", xml_data, data_listofdic, req_id)
        try:
            for data_dic in data_listofdic:
                msg = ConsumeMessageResponseEntry()
                msg.message_body = data_dic["MessageBody"]
                msg.consumed_times = int(data_dic["ConsumedTimes"])
                msg.publish_time = int(data_dic["PublishTime"])
                msg.first_consume_time = int(data_dic["FirstConsumeTime"])
                msg.message_id = data_dic["MessageId"]
                if "MessageBodyMD5" in data_dic:
                    msg.message_body_md5 = data_dic["MessageBodyMD5"]
                msg.next_consume_time = int(data_dic["NextConsumeTime"])
                msg.receipt_handle = data_dic["ReceiptHandle"]
                if "MessageTag" in data_dic:
                    msg.message_tag = data_dic["MessageTag"]
                if "Properties" in data_dic:
                    msg.properties = data_dic["Properties"]
                message_list.append(msg)
        except Exception as e:
            raise MQClientNetworkException("RespDataDamaged", xml_data, req_id)
        return message_list


class AckMessageDecoder(DecoderBase):
    @staticmethod
    def decodeError(xml_data, req_id=None):
        try:
            return ErrorDecoder.decodeError(xml_data, req_id)
        except Exception as e:
            pass

        data_listofdic = []
        DecoderBase.xml_to_listofdic("Errors", "Error", xml_data, data_listofdic, req_id)
        if len(data_listofdic) == 0:
            raise MQClientNetworkException("RespDataDamaged", xml_data, req_id)

        key_list = sorted(["ErrorCode", "ErrorMessage", "ReceiptHandle"])
        for data_dic in data_listofdic:
            for key in key_list:
                keys = sorted(data_dic.keys())
                if keys != key_list:
                    raise MQClientNetworkException("RespDataDamaged", xml_data, req_id)
        return data_listofdic[0]["ErrorCode"], data_listofdic[0]["ErrorMessage"], None, None, data_listofdic


class PublishMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic, req_id)
        key_list = ["MessageId", "MessageBodyMD5"]
        for key in key_list:
            if key not in list(data_dic.keys()):
                raise MQClientNetworkException("RespDataDamaged", xml_data, req_id)

        if "ReceiptHandle" in data_dic:
            return data_dic["MessageId"], data_dic["MessageBodyMD5"], data_dic["ReceiptHandle"]

        return data_dic["MessageId"], data_dic["MessageBodyMD5"], ""


class ErrorDecoder(DecoderBase):
    @staticmethod
    def decodeError(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Error", xml_data, data_dic, req_id)
        key_list = ["Code", "Message", "RequestId", "HostId"]
        for key in key_list:
            if key not in list(data_dic.keys()):
                raise MQClientNetworkException("RespDataDamaged", xml_data, req_id)
        return data_dic["Code"], data_dic["Message"], data_dic["RequestId"], data_dic["HostId"], None
