import traceback
from typing import Optional, List
from pydantic import Field

from utils.logs.log import logger
from ..base_form import BaseForm, PaginationForm, AddCaseDataForm, VariablesModel, SkipIfModel, \
    HeaderModel, ChangeSortForm
from app.models.assist.script import Script
from app.schemas.enums import CaseStatusEnum


class FindCaseForm(PaginationForm):
    """ 根据用例集查找用例 """
    name: Optional[str] = Field(default=None, title="用例名")
    status: Optional[int] = Field(default=None, 
        title="用例调试状态",
        description="0未调试-不执行，1调试通过-要执行，2调试通过-不执行，3调试不通过-不执行，默认未调试-不执行")
    has_step: Optional[int] = Field(default=None, title="标识用例下是否有步骤")
    suite_id: int = Field(..., title="用例集")

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        filter_dict = {"suite_id": self.suite_id}
        if self.name:
            filter_dict["name__icontains"] = self.name
        if self.status:
            filter_dict["status"] = self.status
        return filter_dict


class GetAssistCaseForm(BaseForm):
    """ 根据服务查找用例 """
    project_id: int = Field(..., title="服务id")


class GetCaseNameForm(BaseForm):
    """ 获取用例的名字 """
    case_list: List[int] = Field(..., title="用例id list")


class GetCaseForm(BaseForm):
    """ 获取用例信息 """
    id: int = Field(..., title="用例id")


class DeleteCaseForm(BaseForm):
    """ 删除用例 """
    id_list: List[int] = Field(..., title="用例id list")

class ChangeCaseStatusForm(DeleteCaseForm):
    """ 批量修改用例状态 """
    status: CaseStatusEnum = Field(
        ..., title="用例调试状态",
        description="0未调试-不执行，1调试通过-要执行，2调试通过-不执行，3调试不通过-不执行，默认未调试-不执行")


class ChangeCaseParentForm(BaseForm):
    id_list: list = Field(..., title="用例id列表")
    suite_id: int = Field(..., title="用例集id")


class CopyCaseStepForm(BaseForm):
    """ 复制用例的步骤 """

    from_case: int = Field(..., title="复制源用例id")
    to_case: int = Field(..., title="当前用例id")


class AddCaseForm(BaseForm):
    """ 添加用例的校验 """
    suite_id: int = Field(..., title="用例集id")
    case_list: List[AddCaseDataForm] = Field(..., title="用例")


class EditCaseForm(GetCaseForm):
    """ 修改用例 """
    suite_id: int = Field(..., title="用例集id")
    name: str = Field(..., title="用例名称")
    desc: str = Field(..., title="用例描述")
    skip_if: List[SkipIfModel] = Field(..., title="跳过条件")
    variables: List[VariablesModel] = Field(..., title="变量")
    headers: Optional[List[HeaderModel]] = Field(..., title="头部信息")
    run_times: int = Field(default=1, title="运行次数")

    def validate_variables(self, all_func_name, all_variables):
        """ 公共变量参数的校验
        1.校验是否存在引用了自定义函数但是没有引用脚本文件的情况
        2.校验是否存在引用了自定义变量，但是自定义变量未声明的情况
        """
        variables = [variable.dict() for variable in self.variables]
        self.validate_variable_format(variables)  # 校验格式
        self.validate_func(all_func_name, content=self.dumps(variables))  # 校验引用的自定义函数
        self.validate_variable(all_variables, self.dumps(variables), "自定义变量")  # 校验变量

    def validate_headers(self, all_func_name, all_variables):
        """ 头部参数的校验
        1.校验是否存在引用了自定义函数但是没有引用脚本文件的情况
        2.校验是否存在引用了自定义变量，但是自定义变量未声明的情况
        """
        if self.headers:
            headers = [header.dict() for header in self.headers]
            self.validate_header_format(headers)  # 校验格式
            self.validate_func(all_func_name, content=self.dumps(headers))  # 校验引用的自定义函数
            self.validate_variable(all_variables, self.dumps(headers), "头部信息")  # 校验引用的变量

    async def validate_request(self, *args, **kwargs):
        # TODO 优化校验位置到 services
        # 合并项目选择的自定义函数和用例选择的脚本文件
        project_script_list = kwargs["project_script_list"]
        all_func_name = await Script.get_func_by_script_id(project_script_list)

        # 合并环境的变量和case的变量
        variables = kwargs["project_env_variables"]
        variables.extend([variable.dict() for variable in self.variables])
        all_variables = {variable.get("key"): variable.get("value") for variable in variables if variable.get("key")}

        self.validate_variables(all_func_name, all_variables)
        self.validate_headers(all_func_name, all_variables)


class RunCaseForm(BaseForm):
    """ 运行用例 """
    id_list: List[int] = Field(..., title="用例id list")
    env_list: List[str] = Field(..., title="运行环境code", min_length=1)
    temp_variables: Optional[dict] = Field(default=None, title="临时指定参数")
    is_async: int = Field(default=0, title="执行模式", description="0：用例维度串行执行，1：用例维度并行执行")
    tigger_type: Optional[str] = Field(default=0, title="触发类型")
    browser: Optional[str] = Field(default="chrome", title="运行浏览器（ui自动化必传）")
    server_id: Optional[int] = Field(default=None, title="执行服务器（app自动化必传）")
    phone_id: Optional[int] = Field(default=None, title="执行手机（app自动化必传）")
    no_reset: Optional[bool] = Field(default=False, title="是否不重置手机（app自动化必传）")
    insert_to: Optional[int] = Field(default=None, title="要插入到的报告id", description="把结果、执行记录，插入到指定的报告下")

    async def validate_request(self, project_model, project_env_model, case_suite_model, case_model, *args, **kwargs):

        # TODO 优化校验位置到 services
        # 公共变量参数的校验
        # 1.校验是否存在引用了自定义函数但是没有引用脚本文件的情况
        # 2.校验是否存在引用了自定义变量，但是自定义变量未声明的情况
        if self.temp_variables and len(self.id_list) == 1:
            variables, headers = self.temp_variables.get("variables", []), self.temp_variables.get("headers", [])

            # 1、先校验数据格式
            if len(variables) > 0:  # 校验变量
                self.validate_variable_format(variables)  # 校验格式

            if len(headers) > 0:  # 校验头部参数
                self.validate_header_format(headers)  # 校验格式

            # 2、校验数据引用是否合法
            case = await case_model.filter(id=self.id_list[0]).first().values("suite_id", "variables")
            suite = await case_suite_model.filter(id=case["suite_id"]).first().values("project_id")
            project = await project_model.filter(id=suite["project_id"]).first()

            # 自定义函数
            project_script_list = project.script_list
            try:
                all_func_name = await Script.get_func_by_script_id(project_script_list)
            except:
                logger.error(traceback.format_exc())
                raise ValueError('自定义函数导入错误，请检查脚本和语法')
            self.validate_func(all_func_name, content=self.dumps(variables))  # 校验引用的自定义函数

            # 变量
            env = await project_env_model.filter(project_id=project.id).first()
            env_variables = env.variables
            env_variables.extend(case["variables"])
            all_variables = {
                variable.get("key"): variable.get("value") for variable in env_variables if variable.get("key")
            }
            if len(variables) > 0:  # 校验变量
                self.validate_variable(all_variables, self.dumps(variables), "自定义变量")  # 校验变量

            if len(headers) > 0:  # 校验头部参数
                self.validate_func(all_func_name, content=self.dumps(headers))  # 校验引用的自定义函数
                self.validate_variable(all_variables, self.dumps(headers), "头部信息")  # 校验引用的变量
