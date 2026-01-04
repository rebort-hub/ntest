from tortoise import Tortoise, fields, models
from tortoise.contrib.pydantic import pydantic_model_creator  # 统一归口，都从此处引用 pydantic_model_creator

from app.schemas.enums import DataStatusEnum
from utils.util.json_util import JsonUtil


class BaseModel(models.Model, JsonUtil):
    id = fields.IntField(pk=True)
    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now=True, description="最后修改时间")
    create_user = fields.IntField(null=True, default=1, description="创建人")
    update_user = fields.IntField(null=True, default=1, description="最后修改人")

    class Meta:
        abstract = True  # 不生成表

    @classmethod
    async def model_create(cls, data_dict: dict, user=None, *args, **kwargs):
        """ 创建数据
         1、如果有id字段，自动去除
         2、如果模型里面有num字段，自动获取最大num数值
         3、自动加上user_id
         """
        if "id" in data_dict: data_dict.pop("id")
        # if "num" in cls._meta.fields: data_dict["num"] = await cls.get_insert_num()
        if user: data_dict["create_user"] = data_dict["update_user"] = user.id
        return await cls.create(**data_dict)

    async def model_update(self, data: dict, user=None, *args, **kwargs):
        """ 根据id更新数据 """
        if "num" in data: data.pop("num")
        if user: data["update_user"] = user.id
        if "id" in data: data.pop("id")
        return await self.__class__.filter(id=self.id).update(**data)

    async def model_delete(self):
        """ 删除数据 """
        await self.__class__.filter(id=self.id).delete()

    # @classmethod
    # async def batch_delete(cls, **kwargs):
    #     await cls.filter(**kwargs).delete()

    @classmethod
    async def batch_insert(cls, data_list, user, **kwargs):
        """ 批量插入 """
        await cls.bulk_create([cls(create_user=user.id, update_user=user.id, **data) for data in data_list])

    async def enable(self):
        """ 启用数据 """
        await self.__class__.filter(id=self.id).update(status=DataStatusEnum.ENABLE)

    async def disable(self):
        """ 禁用数据 """
        await self.__class__.filter(id=self.id).update(status=DataStatusEnum.DISABLE)

    async def copy(self, **kwargs):
        """ 复制对象数据并插入到数据库 """
        data = dict(self)
        if kwargs:
            data.update(kwargs)
        
        if "user_id" in kwargs:
            user_id = kwargs.pop("user_id")
            data["create_user"] = data["update_user"] = user_id
        
        # data["name"] = data.get("name", "") + "_copy"
        if "id" in data: data.pop("id")
        return await self.__class__.model_create(data)

    def to_format_dict(self):
        """ 转字典 """
        data = dict(self)
        data.pop("create_time")
        data.pop("update_time")
        return data

    @classmethod
    async def execute_sql(cls, sql):
        """ 执行原生SQL """
        db = Tortoise.get_connection("default")
        result = await db.execute_query_dict(sql)  # [{'methods': 'POST', 'totle': 3}]
        return result

    @classmethod
    def get_simple_filed_list(cls):
        return ["id", "name"]

    def is_enable(self):
        """ 判断数据是否为启用状态 """
        return self.status == DataStatusEnum.ENABLE

    @classmethod
    def filter_not_get_filed(cls, not_get_filed: list = []):
        """ 根据设置的不查的字段，获取剩下要获取的字段，用于查列表时只查关键字段，提升性能 """
        return cls._meta.fields - set(not_get_filed)

    @classmethod
    def is_admin(cls, api_permissions: list):
        """ 管理员权限 """
        return 'admin' in api_permissions

    @classmethod
    def is_not_admin(cls, api_permissions: list):
        """ 非管理员权限 """
        return cls.is_admin(api_permissions) is False

    @classmethod
    async def get_from_path(cls, data_id):
        """ 获取模块/用例集的归属 """
        from_name = []

        async def get_from(m_id):
            parent = await cls.filter(id=m_id).first()
            from_name.insert(0, parent.name)

            if parent.parent:
                await get_from(parent.parent)

        await get_from(data_id)
        return '/'.join(from_name)

    def is_create_user(self, user_id: int):
        """ 判断当前传进来的id为数据创建者 """
        return self.create_user == user_id

    @classmethod
    async def change_sort(cls, id_list, page_no, page_size):
        """ 批量修改排序 """
        for index, data_id in enumerate(id_list):
            query = cls.filter(id=data_id)
            if await query.first():
                await query.update(num=(page_no - 1) * page_size + index)

    @classmethod
    async def get_max_num(cls, **kwargs):
        """ 返回 model 表中**kwargs筛选条件下的已存在编号num的最大值 """
        max_num_data = await cls.filter(**kwargs).order_by('-num').first()
        return max_num_data.num if max_num_data and max_num_data.num else 0

    @classmethod
    async def get_insert_num(cls, **kwargs):
        """ 返回 model 表中**kwargs筛选条件下的已存在编号num的最大值 + 1 """
        return await cls.get_max_num(**kwargs) + 1

    ###############################  数据校验相关的方法  ###############################
    @classmethod
    async def validate_is_exist(cls, msg: str = None, **kwargs):
        data = await cls.filter(**kwargs).first()
        if data is None:
            raise ValueError(msg or f"数据不存在")
        return data

    @classmethod
    async def validate_is_not_exist(cls, msg: str = None, **kwargs):
        data = await cls.filter(**kwargs).first()
        if data:
            raise ValueError(msg or f"数据存在")

    # @classmethod
    # async def run(
    #         cls, is_async, task_type, project_id, batch_id, report_model, report_name, case_id_list, runner, env_code, env_name,
    #         run_type=None, temp_variables={}, trigger_id=None, browser=None, trigger_type="page", task_dict={},
    #         appium_config={}, extend_data={}, create_user=None, background_tasks=None
    # ):
    #     """ 运行用例/任务 """
    #     summary = report_model.get_summary_template()
    #     summary["env"]["code"], summary["env"]["name"] = env_code, env_name
    #     report = await report_model.get_new_report(
    #         project_id=project_id, batch_id=batch_id, trigger_id=trigger_id or case_id_list, name=report_name,
    #         run_type=task_type, env=env_code, trigger_type=trigger_type, temp_variables=temp_variables, summary=summary,
    #         create_user=create_user, update_user=create_user
    #     )
    #
    #     background_tasks.add_task(runner(
    #         report_id=report.id, case_id_list=case_id_list, is_async=is_async, env_code=env_code, env_name=env_name,
    #         browser=browser, task_dict=task_dict, temp_variables=temp_variables, run_type=run_type,
    #         extend=extend_data, appium_config=appium_config
    #     ).parse_and_run)
    #     # asyncio.create_task(runner(
    #     #     report_id=report.id, case_id_list=case_id_list, is_async=is_async, env_code=env_code, env_name=env_name,
    #     #     browser=browser, task_dict=task_dict, temp_variables=temp_variables, run_type=run_type,
    #     #     extend=extend_data, appium_config=appium_config
    #     # ).parse_and_run())

class NumFiled(BaseModel):
    class Meta:
        abstract = True  # 不生成表

    num = fields.IntField(default=0, null=True, comment="数据序号")


class SaveRequestLog(BaseModel):
    """ 记录请求表 """

    ip = fields.CharField(128, null=True, description="访问来源ip")
    url = fields.CharField(128, null=True, description="请求地址")
    method = fields.CharField(10, null=True, description="请求方法")
    headers = fields.JSONField(default={}, description="头部参数")
    params = fields.JSONField(default={}, description="查询字符串参数")
    data_form = fields.JSONField(default={}, description="form_data参数")
    data_json = fields.JSONField(default={}, description="json参数")

    class Meta:
        abstract = True  # 不生成表
