# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields, pydantic_model_creator
from app.schemas.enums import CaseStatusEnum
from utils.parse.parse import parse_list_to_dict, parse_dict_to_list


class BaseCase(BaseModel):
    """ 用例基类表 """

    name = fields.CharField(255, default="", description="用例名称")
    num = fields.IntField(null=True, description="用例序号")
    desc = fields.TextField(null=True, description="用例描述")
    status = fields.IntField(
        default=CaseStatusEnum.NOT_DEBUG_AND_NOT_RUN.value,
        description="用例状态，0未调试-不执行，1调试通过-要执行，2调试通过-不执行，3调试不通过-不执行，默认未调试-不执行")
    run_times = fields.IntField(null=True, default=1, description="执行次数，默认执行1次")
    variables = fields.JSONField(
        default=[{"key": "", "value": "", "remark": "", "data_type": ""}], description="用例级的公共参数")
    output = fields.JSONField(default=[], description="用例出参（步骤提取的数据）")
    skip_if = fields.JSONField(
        default=[
            {
                "skip_type": "and", "data_source": None, "check_value": None, "comparator": None, "data_type": None,
                "expect": None
            }
        ],
        description="是否跳过的判断条件")
    suite_id = fields.IntField(index=True, description="所属的用例集id")

    class Meta:
        abstract = True  # 不生成表

    async def delete_case(self, step_model):
        """ 删除用例和用例下的步骤 """
        await step_model.filter(case_id=self.id).delete()
        await self.__class__.filter(id=self.id).delete()

    @classmethod
    async def batch_delete_step(cls, step_model):
        """ 清理测试用例不存在的步骤 """
        case_id_list = [data["id"] for data in await cls.all().values("id")]
        await step_model.filter(case_id__notin=case_id_list).delete()

    # @classmethod
    # def get_quote_case_from(cls, case_id, project_model, suite_model, case_model):
    #     """ 获取用例的归属 """
    #     case = case_model.get_first(id=case_id)
    #     suite_path_name = suite_model.get_from_path(case.suite_id)
    #     suite = suite_model.get_first(id=case.suite_id)
    #     project = project_model.get_first(id=suite.project_id)
    #     return f'{project.name}/{suite_path_name}/{case.name}'

    async def get_quote_case_from(self,  project_model, suite_model):
        """ 获取用例的归属 """
        suite_path_name = await suite_model.get_from_path(self.suite_id)
        suite = await suite_model.filter(id=self.suite_id).first()
        project = await project_model.filter(id=suite.project_id).first()
        return f'{project.name}/{suite_path_name}/{self.name}'

    @classmethod
    async def merge_variables(cls, from_case_id, to_case_id):
        """ 当用例引用的时候，自动将被引用用例的自定义变量合并到发起引用的用例上 """
        if from_case_id:
            from_variables = await cls.filter(id=from_case_id).first().values("variables")
            to_variables = await cls.filter(id=to_case_id).first().values("variables")
            from_case_variables = {variable["key"]: variable for variable in from_variables["variables"]}
            to_case_variables = {variable["key"]: variable for variable in to_variables["variables"]}

            for from_variable_key, from_variable_value in from_case_variables.items():
                to_case_variables.setdefault(from_variable_key, from_variable_value)
            await cls.filter(id=to_case_id).update(variables=[value for key, value in to_case_variables.items() if key])


    @classmethod
    async def merge_output(cls, case_id, source_list=[]):
        """ 把步骤的数据提取加到用例的output字段下 """
        output_dict = {}
        for source in source_list:
            if isinstance(source, int):  # 用例id
                source = dict(await cls.filter(id=source).first())
            elif isinstance(source, dict) is False:  # 对象（步骤或用例）
                source = dict(source)

            if source.get("quote_case") or source.get("suite_id"):  # 更新源是用例（引用用例和复制用例下的所有步骤）
                source_id = source["id"] if source.get("suite_id") else source["quote_case"]
                source_case = await cls.filter(id=source_id).first()
                source_case_output = parse_list_to_dict(source_case.output)
                output_dict.update(source_case_output)
            else:  # 更新源为步骤（添加步骤和复制其他用例的步骤）
                output_dict.update(parse_list_to_dict(source["extracts"]))

        to_case = await cls.filter(id=case_id).first()
        output_dict.update(parse_list_to_dict(to_case.output))
        await cls.filter(id=case_id).update(output=parse_dict_to_list(output_dict, False))


class ApiCase(BaseCase):
    """ 用例表 """

    headers = fields.JSONField(default=[{"key": "", "value": "", "remark": ""}], description="用例的头部信息")

    class Meta:
        table = "api_test_case"
        table_description = "接口测试用例表"

    async def delete_current_and_step(self):
        pass
        # step_list = await Step.filter(case_id=self.id).all()
        # for step in step_list:
        #     await step.model_delete()
        #     await step.subtract_api_quote_count()
        # await self.model_delete()


class AppCase(BaseCase):
    """ 用例表 """

    class Meta:
        table = "app_ui_test_case"
        table_description = "APP测试用例表"


class UiCase(BaseCase):
    """ 用例表 """

    class Meta:
        table = "web_ui_test_case"
        table_description = "web-ui测试用例表"


UiCasePydantic = pydantic_model_creator(UiCase, name="UiCase")
AppCasePydantic = pydantic_model_creator(AppCase, name="AppCase")
ApiCasePydantic = pydantic_model_creator(ApiCase, name="ApiCase")
