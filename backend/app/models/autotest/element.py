# -*- coding: utf-8 -*-
from .page import BaseApi
from ..base_model import BaseModel, fields, pydantic_model_creator


class BaseElement(BaseApi):
    """ 页面元素表 """

    by = fields.CharField(255, null=True, description="定位方式")
    element = fields.TextField(default="", null=True, description="元素值")
    wait_time_out = fields.IntField(default=5, null=True, description="等待元素出现的时间，默认5秒")
    page_id = fields.IntField(null=True, index=True, description="所属的页面id")

    class Meta:
        abstract = True  # 不生成表

    @classmethod
    async def copy_element(cls, old_page_id, new_page_id, user):
        old_element_list, new_element_list = await cls.filter(page_id=old_page_id).all(), []
        for index, element in enumerate(old_element_list):
            element_dict = dict(element)
            element_dict.pop("id")
            element_dict["num"], element_dict["page_id"] = index, new_page_id
            element_dict["create_user"] = element_dict["update_user"] = user.id
            new_element_list.append(cls(**element_dict))
        await cls.bulk_create(new_element_list)


class AppElement(BaseElement):
    """ 页面元素表 """

    template_device = fields.IntField(
        null=True, description="元素定位时参照的设备，定位方式为bounds时根据此设备参照分辨率")

    class Meta:
        table = "app_ui_test_element"
        table_description = "APP测试元素表"


class UiElement(BaseElement):
    """ 页面元素表 """

    class Meta:
        table = "web_ui_test_element"
        table_description = "web-ui测试元素表"


UiElementPydantic = pydantic_model_creator(UiElement, name="UiElement")
AppElementPydantic = pydantic_model_creator(AppElement, name="AppElement")
