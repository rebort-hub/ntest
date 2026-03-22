# -*- coding: utf-8 -*-
import asyncio
import importlib
import os
import types
from concurrent.futures import ThreadPoolExecutor
from functools import partial  # 处理关键字参数必备
from typing import Callable, Any

from ..base_model import fields, pydantic_model_creator, BaseModel
from app.models.config.run_env import RunEnv
from utils.util.file_util import FileUtil


class Script(BaseModel):
    """ python脚本 """

    name = fields.CharField(128, index=True, description="脚本名称")
    script_data = fields.TextField(default="", description="脚本代码")
    desc = fields.CharField(128, description="函数文件描述")
    num = fields.IntField(null=True, description="当前函数文件的序号")
    script_type = fields.CharField(
        16, default="test", index=True, description="脚本类型，test：执行测试、mock：mock脚本、encryption：加密、decryption：解密")

    class Meta:
        table = "auto_test_python_script"
        table_description = "python脚本"

    @classmethod
    async def create_script_file(cls, env_code=None, not_create_list=[]):
        """ 创建所有自定义函数 py 文件，默认在第一行加上运行环境
        示例：
            # coding:utf-8

            env_code = "test"

            脚本内容
        """
        if env_code is None:
            env_data = await RunEnv.first().values("code")
            env_code = env_data["code"]

        for script in await cls.all():
            if script.name not in not_create_list:
                FileUtil.save_script_data(f'{env_code}_{script.name}', script.script_data, env_code)

    @classmethod
    async def get_func_by_script_id(cls, script_id_list: list, env_id=None):
        """ 获取指定脚本中的函数 """
        if env_id is None:
            env_data = await RunEnv.first().values("code")
        else:
            env_data = await RunEnv.filter(id=env_id).first().values("code")
        env_code = env_data["code"]

        await cls.create_script_file(env_code)  # 创建所有函数文件
        func_dict = {}
        for script_id in script_id_list:
            script = await cls.filter(id=script_id).first().values("name")
            func_list = importlib.reload(importlib.import_module(f'script_list.{env_code}_{script["name"]}'))
            func_dict.update({
                name: item for name, item in vars(func_list).items() if isinstance(item, types.FunctionType)
            })
        return func_dict

    @classmethod
    async def run_func(cls, func: Callable, args: tuple = None, kwargs: dict = None, timeout: int = 600) -> Any:
        """线程安全的异步任务执行器，支持超时控制和自动资源回收"""
        args = args or ()
        kwargs = kwargs or {}
        max_workers = min(50, os.cpu_count() * 5)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            try:
                if not kwargs:
                    return await asyncio.wait_for(
                        asyncio.get_running_loop().run_in_executor(executor, func, *args), timeout=timeout)
                bound_func = partial(func, *args, **kwargs)
                return await asyncio.wait_for(
                    asyncio.get_running_loop().run_in_executor(executor, bound_func), timeout=timeout)
            except Exception as e:
                executor.shutdown(wait=True)  # 强制终止超时任务
                raise

ScriptPydantic = pydantic_model_creator(Script, name="Script")
