# coding=utf-8


class MQExceptionBase(Exception):
    """
    @type type: string
    @param type: 错误类型

    @type message: string
    @param message: 错误描述

    @type req_id: string
    @param req_id: 请求的request_id
    """

    def __init__(self, type, message, req_id=None):
        self.type = type
        self.message = message
        self.req_id = req_id

    def get_info(self):
        if self.req_id is not None:
            return "(\"%s\" \"%s\") RequestID:%s\n" % (self.type, self.message, self.req_id)
        else:
            return "(\"%s\" \"%s\")\n" % (self.type, self.message)

    def __str__(self):
        return "MQExceptionBase  %s" % (self.get_info())


class MQClientException(MQExceptionBase):
    def __init__(self, type, message, req_id=None):
        MQExceptionBase.__init__(self, type, message, req_id)

    def __str__(self):
        return "MQClientException  %s" % (self.get_info())


class MQServerException(MQExceptionBase):
    """ 处理异常

        @note: 根据type进行分类处理，常见错误类型：
             : InvalidArgument       参数不合法
             : AccessDenied          无权对该资源进行当前操作
             : TopicNotExist         主题不存在
             : MessageNotExist       队列中没有消息
             : 更多错误类型请移步阿里云消息和通知服务官网进行了解；
    """

    def __init__(self, type, message, request_id, host_id, sub_errors=None):
        MQExceptionBase.__init__(self, type, message, request_id)
        self.request_id = request_id
        self.host_id = host_id
        self.sub_errors = sub_errors

    def __str__(self):
        return "MQServerException  %s" % (self.get_info())


class MQClientNetworkException(MQClientException):
    """ 网络异常

        @note: 检查endpoint是否正确、本机网络是否正常等;
    """

    def __init__(self, type, message, req_id=None):
        MQClientException.__init__(self, type, message, req_id)

    def get_info(self):
        return "(\"%s\", \"%s\")\n" % (self.type, self.message)

    def __str__(self):
        return "MQClientNetworkException  %s" % (self.get_info())


class MQClientParameterException(MQClientException):
    """ 参数格式错误

        @note: 请根据提示修改对应参数;
    """

    def __init__(self, type, message, req_id=None):
        MQClientException.__init__(self, type, message, req_id)

    def __str__(self):
        return "MQClientParameterException  %s" % (self.get_info())
