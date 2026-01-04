# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields, pydantic_model_creator
from app.schemas.enums import ApiCaseSuiteTypeEnum, CaseStatusEnum
from config import api_suite_list, ui_suite_list


class BaseCaseSuite(BaseModel):
    """ 用例集基类表 """
    name = fields.CharField(255, default="", description="用例集名称")
    num = fields.IntField(null=True, description="用例集在对应服务下的序号")
    suite_type = fields.CharEnumField(
        ApiCaseSuiteTypeEnum, default=ApiCaseSuiteTypeEnum.BASE,
        description="用例集类型，base: 基础用例集，api: 单接口用例集，process: 流程用例集，assist: 造数据用例集")
    parent = fields.IntField(null=True, description="父级用例集id")
    project_id = fields.IntField(index=True, description="所属的服务id")

    class Meta:
        abstract = True  # 不生成表

    @classmethod
    async def upload(cls, project_id, data_tree, case_model):
        """ 上传用例集 """
        suite_pass, suite_fail, case_pass, case_fail = [], [], [], []
        topic_list = data_tree.get("topic", {}).get("topics", [])

        async def insert_data(topic_data, parent=None):
            title = topic_data.get("title", "")

            if title.startswith('tc'):  # 用例
                case_name = title.split(':')[1] if ':' in title else title.split('：')[1]  # 支持中英文的冒号
                if await case_model.filter(name=case_name, suite_id=parent).first() is None:  # 有才导入
                    desc = topic_data.get("topics", [{}])[0].get("title", case_name)
                    try:
                        await case_model.create(name=case_name, desc=desc, suite_id=parent)
                        case_pass.append(case_name)
                    except:
                        case_fail.append(case_name)
            else:  # 用例集
                suite = await cls.filter(parent=parent, name=title, project_id=project_id).first()
                if suite is None:  # 有就插入下级
                    try:
                        suite = await cls.create(name=title, project_id=project_id, parent=parent, suite_type="process")
                        suite_pass.append(title)
                    except:
                        suite_fail.append(title)
                        return
                for child in topic_data.get("topics", []):
                    await insert_data(child, suite.id)

        for topic_data in topic_list:
            await insert_data(topic_data)

        return {
            "suite": {
                "pass": {
                    "total": len(suite_pass),
                    "data": suite_pass
                },
                "fail": {
                    "total": len(suite_fail),
                    "data": suite_fail
                },
            },
            "case": {
                "pass": {
                    "total": len(case_pass),
                    "data": case_pass
                },
                "fail": {
                    "total": len(case_fail),
                    "data": case_fail
                },
            }
        }

    async def update_children_suite_type(self):
        """ 递归更新子用例集的类型 """
        cls = self.__class__

        async def change_child_suite_type(parent_id):
            child_list = await cls.filter(parent=parent_id).all()
            for child in child_list:
                await cls.filter(id=child.id).update(suite_type=self.suite_type)
                await change_child_suite_type(child.id)

        await change_child_suite_type(self.id)

    @classmethod
    async def create_suite_by_project(cls, project_id):
        """ 根据项目id，创建用例集 """
        project_type, suite_type_list = "ui", ui_suite_list
        if "api" in cls.__name__.lower():
            project_type, suite_type_list = "api", api_suite_list

        model_list = [
            cls(num=index, project_id=project_id, name=suite_type["value"], suite_type=suite_type["key"])
            for index, suite_type in enumerate(suite_type_list)
        ]
        await cls.bulk_create(model_list)

    async def get_run_case_id(self, case_model, business_id=None):
        """ 获取用例集下，状态为要运行的用例id """
        filter_dict = {"suite_id": self.id, "status": CaseStatusEnum.DEBUG_PASS_AND_RUN.value}
        if business_id:
            filter_dict["business_id"] = business_id
        case_list = await case_model.filter(**filter_dict).order_by("num").all().values('id')
        return [case["id"] for case in case_list]

    @classmethod
    async def get_case_id(cls, case_model, project_id: int, suite_id: list, case_id: list):
        """
        获取要执行的用例的id
            1、即没选择用例，也没选择用例集
            2、只选择了用例
            3、只选了用例集
            4、选定了用例和用例集
        """
        # 1、只选择了用例，则直接返回用例
        if len(case_id) != 0 and len(suite_id) == 0:
            return case_id

        # 2、没有选择用例集和用例，则视为选择了所有用例集
        elif len(suite_id) == 0 and len(case_id) == 0:
            suite_list = await cls.filter(
                project_id=project_id, suite_type__in=['api', 'process']).all().values("id")
            suite_id = [suite["id"] for suite in suite_list]

        # 解析已选中的用例集，并继承已选中的用例列表，再根据用例id去重
        case_id_list = await case_model.filter(suite_id__in=suite_id,
                                               status=CaseStatusEnum.DEBUG_PASS_AND_RUN).order_by("num").all().values(
            "id")
        case_id.extend([case_id["id"] for case_id in case_id_list])
        return list(set(case_id))

    @classmethod
    async def get_make_data_case(cls, project_id, case_model):
        """ 获取造数据用例集下的用例 """
        filed_list = ["id", "name", "desc", "status", "skip_if", "headers", "variables", "output", "suite_id"]
        suite_list = await cls.filter(
            project_id=project_id, suite_type=ApiCaseSuiteTypeEnum.MAKE_DATA).all().values("id")
        suite_id_list = [suite["id"] for suite in suite_list]
        return await case_model.filter(
            suite_id__in=suite_id_list, status=CaseStatusEnum.DEBUG_PASS_AND_RUN).order_by("num").all().values(*filed_list)


class ApiCaseSuite(BaseCaseSuite):
    """ 用例集表 """

    class Meta:
        table = "api_test_case_suite"
        table_description = "接口测试用例集表"


class AppCaseSuite(BaseCaseSuite):
    """ 用例集表 """

    class Meta:
        table = "app_ui_test_case_suite"
        table_description = "APP测试用例集表"


class UiCaseSuite(BaseCaseSuite):
    """ 用例集表 """

    class Meta:
        table = "web_ui_test_case_suite"
        table_description = "web-ui测试用例集表"


ApiCaseSuitePydantic = pydantic_model_creator(ApiCaseSuite, name="ApiCaseSuite")
AppCaseSuitePydantic = pydantic_model_creator(AppCaseSuite, name="AppCaseSuite")
UiCaseSuitePydantic = pydantic_model_creator(UiCaseSuite, name="UiCaseSuite")
