# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields, pydantic_model_creator
from ...schemas.enums import AppiumVersionEnum


class AppRunServer(BaseModel):
    """ 运行服务器表 """

    name = fields.CharField(255, null=True, unique=True, description="服务器名字")
    num = fields.IntField(null=True, description="序号")
    os = fields.CharField(8, null=True, description="服务器系统类型：windows/mac/linux")
    ip = fields.CharField(32, null=True, description="服务器ip地址")
    port = fields.CharField(8, null=True, default="4723", description="服务器端口号")
    appium_version = fields.CharEnumField(AppiumVersionEnum, default=AppiumVersionEnum.version1, max_length=8, null=True, description="appium版本")
    status = fields.IntField(default=0, description="最近一次访问状态，0:未访问，1:访问失败，2:访问成功")

    class Meta:
        table = "app_ui_test_run_server"
        table_description = "APP测试运行服务器表"

    async def request_fail(self):
        await self.model_update({"status": 1})

    async def request_success(self):
        await self.model_update({"status": 2})

    async def get_appium_config(self, app_package, app_activity, phone, no_reset=False, command_timeout=120):
        """ 获取appium配置 """
        appium_config = {
            "host": self.ip,
            "port": self.port,
            "remote_path": '/wd/hub' if self.appium_version == AppiumVersionEnum.version1 else '',  # appium1.x的请求地址为/wd/hub，2.x及以上为/
            "newCommandTimeout": int(command_timeout),  # 两条appium命令间的最长时间间隔，若超过这个时间，appium会自动结束并退出app，单位为秒
            "noReset": no_reset,  # 控制APP记录的信息是否不重置
            # "unicodeKeyboard": True,  # 使用 appium-ime 输入法
            # "resetKeyboard": True,  # 表示在测试结束后切回系统输入法

            # 设备参数
            "platformName": phone.os,
            "platformVersion": phone.os_version,
            "deviceName": phone.device_id,

            # 用于后续自动化测试中的参数
            "server_id": self.id,  # 用于判断跳过条件
            "phone_id": phone.id,  # 用于判断跳过条件
            "device": phone.to_format_dict(),  # 用于插入到公共变量
            "udid": phone.device_id  # 设备唯一识别号(可以使用Itunes查看UDID, 点击左上角手机图标 - 点击序列号直到出现UDID为止)
        }
        if phone.os == "Android":  # 安卓参数
            appium_config["automationName"] = "UIAutomator2"
            appium_config["appPackage"] = app_package
            appium_config["appActivity"] = app_activity
        else:  # IOS参数
            appium_config["automationName"] = "XCUITest"
            appium_config["xcodeOrgId"] = ""  # 开发者账号id，可在xcode的账号管理中查看
            appium_config["xcodeSigningId"] = "iPhone Developer"

        return appium_config


class AppRunPhone(BaseModel):
    """ 运行终端表 """

    name = fields.CharField(255, null=True, unique=True, description="设备名字")
    num = fields.IntField(null=True, description="序号")
    os = fields.CharField(8, null=True, description="设备系统类型：Android/ios")
    os_version = fields.CharField(255, null=True, description="设备系统版本号")
    device_id = fields.CharField(255, null=True, description="终端设备id")
    extends = fields.JSONField(default={}, description="设备扩展字段")
    screen = fields.CharField(64, null=True, description="屏幕分辨率")

    class Meta:
        table = "app_ui_test_run_phone"
        table_description = "APP测试运行终端表"


AppRunServerPydantic = pydantic_model_creator(AppRunServer, name="AppRunServer")
AppRunPhonePydantic = pydantic_model_creator(AppRunPhone, name="AppRunPhone")
