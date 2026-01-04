# coding=utf-8

import os
import logging
import logging.handlers
from .mq_exception import *

METHODS = ["PUT", "POST", "GET", "DELETE"]


class MQLogger:
    @staticmethod
    def get_logger(log_name=None, log_file=None, log_level=logging.INFO):
        if log_name is None:
            log_name = "mq_python_sdk"
        if log_file is None:
            log_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], "mq_python_sdk.log")
        logger = logging.getLogger(log_name)
        if logger.handlers == []:
            fileHandler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024)
            formatter = logging.Formatter(
                '[%(asctime)s] [%(name)s] [%(levelname)s] [%(filename)s:%(lineno)d] [%(thread)d] %(message)s',
                '%Y-%m-%d %H:%M:%S')
            fileHandler.setFormatter(formatter)
            logger.addHandler(fileHandler)
        MQLogger.validate_loglevel(log_level)
        logger.setLevel(log_level)
        return logger

    @staticmethod
    def validate_loglevel(log_level):
        log_levels = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]
        if log_level not in log_levels:
            raise MQClientParameterException("LogLevelInvalid", "Bad value: '%s', expect levels: '%s'." % \
                                             (log_level, ','.join([str(item) for item in log_levels])))


class ValidatorBase:
    @staticmethod
    def validate(req):
        pass

    @staticmethod
    def type_validate(item, valid_type, param_name=None):
        if not (type(item) is valid_type):
            if param_name is None:
                raise MQClientParameterException("TypeInvalid", "Bad type: '%s', '%s' expect type '%s'." % (
                    type(item), item, valid_type))
            else:
                raise MQClientParameterException("TypeInvalid",
                                                 "Param '%s' in bad type: '%s', '%s' expect type '%s'." % (
                                                     param_name, type(item), item, valid_type))

    @staticmethod
    def is_str(item, param_name=None):
        if not isinstance(item, str):
            if param_name is None:
                raise MQClientParameterException("TypeInvalid",
                                                 "Bad type: '%s', '%s' expect basestring." % (type(item), item))
            else:
                raise MQClientParameterException("TypeInvalid",
                                                 "Param '%s' in bad type: '%s', '%s' expect basestring." % (
                                                     param_name, type(item), item))

    @staticmethod
    def name_validate(name, nameType):
        # type
        ValidatorBase.is_str(name)

        # length
        if len(name) < 1:
            raise MQClientParameterException("NameInvalid",
                                             "Bad value: '%s', the length of %s should larger than 1." % (
                                                 name, nameType))


class MessageValidator(ValidatorBase):
    @staticmethod
    def receiphandle_validate(receipt_handle):
        if receipt_handle == "":
            raise MQClientParameterException("ReceiptHandleInvalid", "The receipt handle should not be null.")

    @staticmethod
    def consumer_validate(consumer):
        if consumer == "":
            raise MQClientParameterException("ConsumerInvalid", "The consumer should not be null.")

    @staticmethod
    def waitseconds_validate(wait_seconds):
        if wait_seconds != -1 and wait_seconds < 0:
            raise MQClientParameterException("WaitSecondsInvalid",
                                             "Bad value: '%d', wait_seconds should larger than 0." % wait_seconds)

    @staticmethod
    def consume_tag_validate(message_tag):
        if len(message_tag) > 64:
            raise MQClientParameterException("ConsumeTagInvalid",
                                             "The length of message tag should be between 1 and 64.")

    @staticmethod
    def batchsize_validate(batch_size):
        if batch_size != -1 and batch_size < 0:
            raise MQClientParameterException("BatchSizeInvalid",
                                             "Bad value: '%d', batch_size should larger than 0." % batch_size)

    @staticmethod
    def publishmessage_attr_validate(req):
        # type
        ValidatorBase.is_str(req.message_body, "message_body")
        ValidatorBase.is_str(req.message_tag, "message_tag")
        # value
        if req.message_body == "":
            raise MQClientParameterException("MessageBodyInvalid", "Bad value: '', message body should not be ''.")
        if len(req.message_tag) > 64:
            raise MQClientParameterException("MessageTagInvalid",
                                             "The length of message tag should be between 1 and 64.")


class ConsumeMessageValidator(MessageValidator):
    @staticmethod
    def validate(req):
        MessageValidator.validate(req)
        ValidatorBase.name_validate(req.topic_name, "topic_name")
        ValidatorBase.name_validate(req.consumer, "consumer")
        MessageValidator.batchsize_validate(req.batch_size)
        MessageValidator.waitseconds_validate(req.wait_seconds)
        MessageValidator.consumer_validate(req.consumer)


class AckMessageValidator(MessageValidator):
    @staticmethod
    def validate(req):
        MessageValidator.validate(req)
        ValidatorBase.name_validate(req.topic_name, "topic_name")
        ValidatorBase.name_validate(req.consumer, "consumer")
        MessageValidator.consumer_validate(req.consumer)
        for receipt_handle in req.receipt_handle_list:
            MessageValidator.receiphandle_validate(receipt_handle)


class PublishMessageValidator(MessageValidator):
    @staticmethod
    def validate(req):
        MessageValidator.validate(req)
        ValidatorBase.name_validate(req.topic_name, "topic_name")
        MessageValidator.publishmessage_attr_validate(req)


class MQUtils:
    def __init__(self):
        pass

    @staticmethod
    def check_property(prop):
        # if ":" in prop or "|" in prop or "\"" in prop or "&" in prop or "'" in prop or "<" in prop or ">" in prop:
        if "|" in prop or "\"" in prop or "&" in prop or "'" in prop or "<" in prop or ">" in prop:
            return False

        return True

    @staticmethod
    def map_to_string(properties):
        if properties is None:
            return ""
        ret = ""
        for key, value in list(properties.items()):
            if MQUtils.check_property(key) is False or MQUtils.check_property(value) is False:
                raise MQClientParameterException("MessagePropertyInvalid", "Message's property['%s':'%s'] ] can't "
                                                                           "contains: & \" ' < > : |" % (key, value))
            ret += key + ":" + value + "|"
        return ret

    @staticmethod
    def string_to_map(property_str):
        if property_str is None or property_str == "":
            return {}

        kv_array = property_str.split("|")
        properties = {}
        for kv in kv_array:
            if kv is None or kv == "" or ":" not in kv:
                continue
            k_and_v = list(kv.split(":"))
            if len(k_and_v) != 2:
                continue
            if k_and_v[0] != "" and k_and_v[1] != "":
                try:
                    properties[str(k_and_v[0])] = str(k_and_v[1])
                except UnicodeEncodeError:
                    properties[k_and_v[0].encode('utf-8')] = k_and_v[1].encode('utf-8')
        return properties
