# -*- coding: utf-8 -*-
import time
import hmac
import hashlib
import base64
import urllib.parse

import httpx

from ..base_model import fields, BaseModel
from app.schemas.enums import WebHookTypeEnum


class WebHook(BaseModel):
    """ webhook管理 """

    num = fields.IntField(null=True, description="排序")
    name = fields.CharField(255, null=True, description="webhook名字")
    addr = fields.CharField(255, null=True, description="webhook地址")
    secret = fields.CharField(255, null=True, description="webhook秘钥")
    webhook_type = fields.CharEnumField(
        WebHookTypeEnum, default=WebHookTypeEnum.DING_DING, description="webhook类型，钉钉、企业微信、飞书")
    desc = fields.CharField(255, null=True, description="描述")

    class Meta:
        table = "config_webhook"
        table_description = "webhook管理表"


    @classmethod
    async def get_webhook_list(cls, webhook_type: WebHookTypeEnum, webhook_list: list):
        query_list = await cls.filter(webhook_type=webhook_type, id__in=webhook_list).all().values("addr", "secret")
        return [cls.build_webhook_addr(webhook_type, data["addr"], data["secret"]) for data in query_list]

    @classmethod
    def build_webhook_addr(cls, webhook_type: str, addr: str, secret: str):
        """ 解析webhook地址 """
        if secret:
            if webhook_type == WebHookTypeEnum.DING_DING.value:
                return cls.build_ding_ding_addr(addr, secret)
        return addr

    @classmethod
    def build_ding_ding_addr(cls, addr: str, secret: str):
        """ 钉钉加签 """
        timestamp = str(round(time.time() * 1000))
        secret_enc = secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return f'{addr}&timestamp={timestamp}&sign={sign}'

    async def debug(self, msg):
        """ 调试 """
        addr = self.build_webhook_addr(self.webhook_type, self.addr, self.secret)
        try:
            async with httpx.AsyncClient(verify=False) as client:
                res = await client.post(addr, json=msg, timeout=30)
            return res.json()
        except Exception as e:
            raise
