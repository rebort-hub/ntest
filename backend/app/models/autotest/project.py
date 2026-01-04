# -*- coding: utf-8 -*-
from ..base_model import BaseModel, fields, pydantic_model_creator
from config import main_server_host
from utils.parse.parse import parse_list_to_dict, update_dict_to_list, parse_dict_to_list


class BaseProject(BaseModel):
    """ 服务基类表 """

    name = fields.CharField(255, null=False, unique=True, description="服务名称")
    manager = fields.IntField(description="服务的管理员id")
    script_list = fields.JSONField(default=[], description="引用的脚本文件")
    num = fields.IntField(null=True, description="当前服务的序号")
    business_id = fields.IntField(index=True, description="所属业务线")

    class Meta:
        abstract = True  # 不生成表

    def is_manager_id(self, user_id: int):
        """ 判断当前用户为当前数据的负责人 """
        return self.manager == user_id

    def is_can_delete(self, user_id: int, user_permissions: list):
        """
        判断是否有权限删除，
        可删除条件（或）：
        1.当前用户为系统管理员
        2.当前用户为当前数据的创建者
        3.当前用户为当前要删除服务的负责人
        """
        return self.is_manager_id(user_id) or self.is_admin(user_permissions) or self.is_create_user(user_id)

    @classmethod
    async def get_business_id(cls, project_id):
        data = await cls.filter(id=project_id).first().values("business_id")
        return data["business_id"]

    @classmethod
    async def clear_env(cls, project_env_model):
        project_id_list = [data["id"] for data in await cls.all().values("id")]
        await project_env_model.query.filter(project_id__not_in=project_id_list).delete()


class ApiProject(BaseProject):
    """ 服务表 """

    swagger = fields.CharField(255, null=True, description="服务对应的swagger地址")
    last_pull_status = fields.IntField(
        null=True, default=1, description="最近一次swagger拉取状态，0拉取失败，1未拉取，2拉取成功")

    class Meta:
        table = "api_test_project"
        table_description = "接口测试服务表"

    async def last_pull_is_fail(self):
        """ 最近一次从swagger拉取失败 """
        await self.model_update({"last_pull_status": 0})

    async def last_pull_is_success(self):
        """ 最近一次从swagger拉取成功 """
        await self.model_update({"last_pull_status": 2})


class AppProject(BaseProject):
    """ APP表 """

    app_package = fields.CharField(255, description="被测app包名")
    app_activity = fields.CharField(255, description="被测app要启动的AndroidActivity")
    template_device = fields.IntField(description="元素定位时参照的设备")

    class Meta:
        table = "app_ui_test_project"
        table_description = "APP测试项目表"


class UiProject(BaseProject):
    """ 服务表 """

    class Meta:
        table = "web_ui_test_project"
        table_description = "web-ui测试项目表"


ApiProjectPydantic = pydantic_model_creator(ApiProject, name="ApiProject")
AppProjectPydantic = pydantic_model_creator(AppProject, name="AppProject")
UiProjectPydantic = pydantic_model_creator(UiProject, name="UiProject")


class BaseProjectEnv(BaseModel):
    """ 服务环境基类表 """

    host = fields.CharField(255, default=main_server_host, description="服务地址")
    variables = fields.JSONField(
        default=[{"key": None, "value": None, "remark": None, "data_type": None}], description="服务的公共变量")

    env_id = fields.IntField(index=True, description="对应环境id")
    project_id = fields.IntField(index=True, description="所属的服务id")

    class Meta:
        abstract = True  # 不生成表

    @classmethod
    async def insert_env(cls, project_id, env_id, user_id):
        """ 获取环境的时候，没有环境，就插入一条环境记录 """
        project_env_first = await cls.filter(project_id=project_id).first()
        if project_env_first:
            insert_env_data = project_env_first.__dict__
            insert_env_data["env_id"] = env_id
        else:
            insert_env_data = {"env_id": env_id, "project_id": project_id}
        insert_env_data["create_user"] = insert_env_data["update_user"] = user_id
        return await cls.model_create(insert_env_data)

    @classmethod
    async def create_env(cls, env_model, project_model, project_id=None, env_list=None):
        """
        当环境配置更新时，自动给项目/环境增加环境信息
        如果指定了项目id，则只更新该项目的id，否则更新所有项目的id
        如果已有当前项目的信息，则用该信息创建到指定的环境
        """
        if not project_id and not env_list:
            return

        env_id_list = env_list or [env["id"] for env in await env_model.all().values("id")]

        if project_id:
            current_project_env = await cls.filter(project_id=project_id).first()
            data = current_project_env.__dict__ if current_project_env else {"project_id": project_id}
            await cls.bulk_create([cls(**data, env_id=env_id) for env_id in env_id_list])

        else:
            all_project_id = [env["id"] for env in await project_model.all().values("id")]
            for project_id in all_project_id:
                await cls.create_env(env_model, project_model, project_id, env_id_list)

    @classmethod
    async def synchronization(cls, from_env: dict, to_env_id_list: list, filed_list: list):
        """ 把当前环境同步到其他环境
        from_env: 从哪个环境
        to_env_list: 同步到哪些环境
        filed_list: 指定要同步的字段列表
        """

        # 同步数据来源解析
        from_env_dict = {filed: parse_list_to_dict(from_env[filed]) for filed in filed_list}
        to_env_list = await cls.filter(project_id=from_env["project_id"], env_id__in=to_env_id_list).all()

        # 同步至指定环境
        for to_env in to_env_list:
            new_env_data = {}
            for filed in filed_list:
                from_data, to_data = from_env_dict[filed], getattr(to_env, filed)
                new_env_data[filed] = update_dict_to_list(from_data, to_data)

            await cls.filter(id=to_env.id).update(**new_env_data)  # 同步环境

    @classmethod
    async def add_env(cls, env_id, project_model):
        """ 新增运行环境时，批量给服务/项目/APP加上 """
        for project in await project_model.all().values("id"):
            if not await cls.filter(project_id=project["id"], env_id=env_id).first().values("id"):
                await cls().create(env_id=env_id, project_id=project["id"])


class ApiProjectEnv(BaseProjectEnv):
    """ 服务环境表 """

    headers = fields.JSONField(default=[{"key": None, "value": None, "remark": None}], description="服务的公共头部信息")

    class Meta:
        table = "api_test_project_env"
        table_description = "接口测试服务环境表"


class AppProjectEnv(BaseProjectEnv):
    """ APP环境表 """

    class Meta:
        table = "app_ui_test_project_env"
        table_description = "APP测试项目环境表"


class UiProjectEnv(BaseProjectEnv):
    """ 服务环境表 """

    class Meta:
        table = "web_ui_test_project_env"
        table_description = "web-ui测试项目环境表"


ApiProjectEnvPydantic = pydantic_model_creator(ApiProjectEnv, name="ApiProjectEnv")
AppProjectEnvPydantic = pydantic_model_creator(AppProjectEnv, name="AppProjectEnv")
UiProjectEnvPydantic = pydantic_model_creator(UiProjectEnv, name="UiProjectEnv")
