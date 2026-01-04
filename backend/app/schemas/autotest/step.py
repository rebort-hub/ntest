from typing import Optional, Union, List
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ExtractModel, ValidateModel, HeaderModel, ParamModel, \
    DataFormModel, SkipIfModel, ChangeSortForm
from app.schemas.enums import ApiBodyTypeEnum, DataStatusEnum


class GetStepListForm(PaginationForm):
    """ 根据用例id获取步骤列表 """
    case_id: int = Field(..., title="用例id")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """

        return {"case_id": self.case_id}


class GetStepForm(BaseForm):
    """ 根据步骤id获取步骤 """
    id: int = Field(..., title="步骤id")


class ChangeStepElement(GetStepForm):
    """ 修改步骤的元素/接口 """
    element_id: int = Field(..., title="接口/元素id")


class DeleteStepForm(BaseForm):
    """ 批量删除步骤 """
    id_list: list = Field(..., title="步骤id list")


class ChangeStepStatusForm(BaseForm):
    """ 批量修改步骤状态 """
    id_list: list = Field(..., title="步骤id list")
    status: DataStatusEnum = Field(..., title="步骤状态")


class CopyStepForm(GetStepForm):
    """ 复制步骤 """
    case_id: Optional[int] = Field(default=None, title="要复制到的用例id")


class AddStepForm(BaseForm):
    """ 添加步骤校验 """
    case_id: int = Field(..., title="步骤所属的用例id")
    quote_case: Optional[int] = Field(default=None, title="引用用例id（步骤为引用用例时必传）")
    name: str = Field(..., title="步骤名称")
    desc: Optional[str] = Field('', title="步骤描述")
    up_func: Optional[list] = Field(default=[], title="前置条件")
    down_func: Optional[list] = Field(default=[], title="后置条件")
    skip_if: List[SkipIfModel] = Field(..., title="跳过条件")
    run_times: int = Field(default=1, title="执行次数")
    extracts: List[ExtractModel] = Field(..., title="数据提取")
    skip_on_fail: int = Field(default=1, title="当用例有失败的步骤时，是否跳过此步骤")
    validates: List[ValidateModel] = Field(..., title="断言")
    data_driver: Union[list, dict] = Field([], title="数据驱动")

    # 接口自动化
    api_id: Optional[int] = Field(default=None, title="步骤对应的接口id（步骤为接口时必传）")
    headers: Optional[List[HeaderModel]] = Field(None, title="跳过条件")
    params: Optional[List[ParamModel]] = Field(None, title="查询字符串参数")
    body_type: ApiBodyTypeEnum = Field(
        ApiBodyTypeEnum.JSON.value, title="请求体数据类型", description="json/form/text/urlencoded")
    data_form: Optional[List[DataFormModel]] = Field(None, title="form-data参数")
    data_json: Union[list, dict] = Field({}, title="json参数")
    data_urlencoded: Optional[dict] = Field({}, title="urlencoded")
    data_text: Optional[str] = Field('', title="字符串参数")
    replace_host: Optional[int] = Field(0, title="是否使用用例所在项目的域名")
    pop_header_filed: Optional[list] = Field([], title="头部参数中去除指定字段")
    time_out: Optional[int] = Field(60, title="请求超时时间")
    allow_redirect: Optional[bool] = Field(False, title="是否允许重定向, true/false")

    # app自动化
    element_id: Optional[int] = Field(default=None, title="步骤对应的元素id")
    send_keys: Optional[str] = Field(default=None, title="输入内容")
    execute_type: Optional[str] = Field('', title="执行动作")
    wait_time_out: Optional[int] = Field(5, title="等待元素超时时间")


    async def validate_add_step_request(self):
        self.validate_is_true(f"不能自己引用自己", self.quote_case != self.case_id)

        if not self.quote_case:
            self.validate_api_extracts([data.dict() for data in self.extracts if data])
            self.validate_base_validates([data.dict() for data in self.validates if data])
            if self.data_form:
                self.validate_variable_format([data.dict() for data in self.data_form if data], msg_title='form-data')

    async def validate_request(self, *args, **kwargs):
        await self.validate_add_step_request()


class EditStepForm(GetStepForm, AddStepForm):
    """ 修改步骤校验 """

    async def validate_request(self, *args, **kwargs):
        await self.validate_add_step_request()

