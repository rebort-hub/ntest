from typing import Optional, Union, List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ApiListModel, ParamModel, HeaderModel, \
    DataFormModel, ExtractModel, ValidateModel, ChangeSortForm
from app.schemas.enums import ApiMethodEnum, DataStatusEnum, ApiBodyTypeEnum


class ApiListForm(PaginationForm):
    """ 查询接口信息 """
    module_id: int = Field(..., title="模块id")
    name: Optional[str] = Field(default=None, title="接口名")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {"module_id": self.module_id}
        if self.name:
            filter_dict["name__icontains"] = self.name
        return filter_dict


class GetApiForm(BaseForm):
    """ 获取api信息 """
    id: int = Field(..., title="接口id")


class ChangeLevel(GetApiForm):
    level: str = Field(..., title="接口等级", description="P0、P1、P2")


class ChangeStatus(GetApiForm):
    status: DataStatusEnum = Field(..., title="接口状态", description="此接口状态，enable/disable")


class GetApiFromForm(BaseForm):
    """ 查询api归属 """
    id: Optional[int] = Field(default=None, title="接口id")
    api_addr: Optional[str] = Field(default=None, title="接口地址")

    async def validate_request(self, *args, **kwargs):
        self.validate_is_true("请传入接口地址或接口id", self.id or self.api_addr)


class DeleteApiForm(GetApiForm):
    """ 删除接口 """


class AddApiForm(BaseForm):
    """ 添加接口信息的校验 """
    project_id: int = Field(..., title="服务id")
    module_id: int = Field(..., title="模块id")
    api_list: List[ApiListModel] = Field(..., title="接口列表")


class EditApiForm(GetApiForm):
    """ 修改接口信息 """
    project_id: int = Field(..., title="服务id")
    module_id: int = Field(..., title="模块id")
    name: str = Field(..., title="接口名")
    desc: Optional[str] = Field(default=None, title="备注")
    method: ApiMethodEnum = Field(..., title="请求方法")
    addr: str = Field(..., title="接口地址")
    headers: List[HeaderModel] = Field(title="头部信息")
    params: List[ParamModel] = Field(title="url参数")
    body_type: ApiBodyTypeEnum = Field(..., title="请求体数据类型", description="json/form/text/urlencoded")
    data_form: List[DataFormModel] = Field(title="data-form参数")
    data_json: Union[list, dict] = Field(title="json参数")
    data_urlencoded: dict = Field(title="urlencoded参数")
    data_text: Optional[str] = Field(default=None, title="文本参数")
    extracts: List[ExtractModel] = Field(title="提取信息")
    validates: List[ValidateModel] = Field(title="断言信息")
    time_out: Optional[int] = Field(default=None, title="请求超时时间")

    async def validate_add_api_request(self, *args, **kwargs):
        # 校验数据结构
        self.validate_api_extracts([extract.dict() for extract in self.extracts])
        self.validate_base_validates([validate.dict() for validate in self.validates])
        self.validate_variable_format([data_form.dict() for data_form in self.data_form], msg_title='form-data')

    async def validate_request(self, *args, **kwargs):
        self.validate_is_true(self.addr, "接口地址必填")
        await self.validate_add_api_request()


class RunApiMsgForm(BaseForm):
    """ 运行接口 """
    id_list: List[int] = Field(..., title="要运行的接口id")
    env_list: List[str] = Field(..., title="运行环境code")
