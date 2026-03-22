from ..base_model import fields, pydantic_model_creator, BaseModel
from app.models.config.business import BusinessLine


class RunEnv(BaseModel):
    """ 运行环境表 """

    name = fields.CharField(255, null=True, unique=True, description="环境名字")
    num = fields.IntField(null=True, description="环境序号")
    code = fields.CharField(255, null=True, index=True, unique=True, description="环境code")
    desc = fields.CharField(255, null=True, description="备注")
    group = fields.CharField(255, null=True, description="环境分组")

    class Meta:
        table = "config_run_env"
        table_description = "运行环境配置表"

    @classmethod
    async def env_to_business(cls, env_id_list, business_id_list, command):
        """ 管理环境与业务线的 绑定/解绑  command: add、delete """
        business_list = await BusinessLine.filter(id__in=business_id_list).all()
        for business in business_list:
            if command == "add":  # 绑定
                env_list = list({*env_id_list, *business.env_list})
            else:  # 取消绑定
                env_list = list(set(business.env_list).difference(set(env_id_list)))
            await business.model_update({"env_list": env_list})

    @classmethod
    async def get_data_byid_or_code(cls, env_id=None, env_code=None):
        """ 根据id或者code获取数据 """
        if env_id:
            return await cls.filter(id=env_id).first()
        return await cls.filter(code=env_code).first()


RunEnvPydantic = pydantic_model_creator(RunEnv, name="RunEnv")
