import re
import importlib
import traceback

from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm
from ...models.assist.model_factory import Script
from utils.util.file_util import FileUtil


class FindScriptForm(PaginationForm):
    """ 查找脚本form """
    detail: Optional[str] = Field(default=None, title="是否获取更多数据")
    file_name: Optional[str] = Field(default=None, title="脚本名")
    script_type: Optional[str] = Field(default=None, title="脚本类型")
    create_user: Optional[int] = Field(default=None, title="创建者")
    update_user: Optional[int] = Field(default=None, title="修改者")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {}
        if self.file_name:
            filter_dict["file_name__icontains"] = self.file_name
        if self.script_type:
            filter_dict["script_type"] = self.script_type
        if self.create_user:
            filter_dict["create_user"] = self.create_user
        if self.create_user:
            filter_dict["create_user"] = self.create_user
        return filter_dict


class GetScriptForm(BaseForm):
    """ 获取自定义脚本文件 """
    id: int = Field(..., title="脚本文件id")


class DeleteScriptForm(GetScriptForm):
    """ 删除脚本文件 """


class DebugScriptForm(GetScriptForm):
    """ 调试函数 """
    expression: str = Field(..., title="调试表达式")
    env: str = Field(..., title="运行环境")


class CreatScriptForm(BaseForm):
    """ 创建自定义脚本文件 """
    name: str = Field(..., title="脚本文件名")
    script_type: str = Field(..., title="脚本类型")
    desc: Optional[str] = Field(default=None, title="脚本描述")
    script_data: str = Field(..., title="脚本内容")

    async def validate_script_name(self, *args, **kwargs):
        """  校验Python脚本文件名 """
        self.validate_is_true(f"脚本文名错误，支持大小写字母和下划线", re.match('^[a-zA-Z_]+$', self.name))

    async def validate_script_data(self, user, save_func_permissions, *args, **kwargs):
        """ 校验自定义脚本文件内容合法 """
        default_env = 'debug'
        if self.script_data:
            # 校验当前用户是否有权限保存脚本文件内容
            if save_func_permissions == '1':
                if self.is_not_admin(user.api_permissions):
                    raise ValueError({
                        "msg": "当前用户暂无权限保存脚本文件内容",
                        "result": "当前用户暂无权限保存脚本文件内容"
                    })

            if self.script_type != 'mock':
                # 防止要改函数时不知道函数属于哪个脚本的情况，强校验函数名必须以脚本名开头
                # importlib.import_module有缓存，所有用正则提取
                functions_name_list = re.findall('\ndef (.+?):', self.script_data)

                for func_name in functions_name_list:
                    if func_name.startswith(self.name) is False:
                        raise ValueError(f'函数【{func_name}】命名格式错误，请以【脚本名_函数名】命名')

            # 把自定义函数脚本内容写入到python脚本中,
            await Script.create_script_file(default_env)  # 重新发版时会把文件全部删除，所以全部创建
            FileUtil.save_script_data(f'{default_env}_{self.name}', self.script_data, env=default_env)

            # 动态导入脚本，语法有错误则不保存
            try:
                script_obj = importlib.reload(importlib.import_module(f'script_list.{default_env}_{self.name}'))
            except Exception as e:
                raise ValueError({
                    "msg": "语法错误，请检查",
                    "result": "\n".join("{}".format(traceback.format_exc()).split("↵"))
                })

    async def validate_request(self, user, save_func_permissions, *args, **kwargs):
        await self.validate_script_name()
        await self.validate_script_data(user, save_func_permissions)


class EditScriptForm(GetScriptForm, CreatScriptForm):
    """ 修改自定义脚本文件 """
