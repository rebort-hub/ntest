from datetime import datetime

from ..base_model import fields, pydantic_model_creator, BaseModel


class WeeklyConfigModel(BaseModel):
    name = fields.TextField(description="名字")
    parent = fields.IntField(null=True, description="上一级的id，有上一级则为项目，否则为产品")
    desc = fields.TextField(description="备注")

    class Meta:
        table = "test_work_weekly_config"
        table_description = "周报配置表"

    @classmethod
    async def get_data_dict(cls):
        """ 获取产品、项目数据
        {
            "id": {
                "total": 0,  # 产品下的项目数
                "name": "产品名",
                "project": {
                    "id": {
                        "total": 0,  # 项目下的版本数
                        "name": "项目名",
                        "version": {
                            "version1": {
                                "total": 0,  # 版本下的日报条数
                                "item": [],  # 版本下的日报数据
                            },
                            "version2": {
                                "total": 0,
                                "item": []
                            }
                        }
                    }
                }
            }
        }
        """
        container = {}
        product_list = [dict(data) for data in await WeeklyConfigModel.all()]

        # 获取所有产品
        for index, data in enumerate(product_list):
            if not data["parent"]:
                cls.build_project_product(container, data)
                cls.build_project_container(container[data["id"]], data)

        # 根据产品id获取所有项目
        for product_id, product_data in container.items():
            for index, data in enumerate(product_list):
                if data["parent"] == product_id:
                    cls.build_project_container(product_data, data)

        return container

    @classmethod
    def build_project_product(cls, container, data):
        """ 插入项目 """
        container[data["id"]] = {
            "total": 0,
            "name": data["name"],
            "project": {}
        }

    @classmethod
    def build_project_container(cls, container, data):
        """ 插入项目 """
        container["project"][data["id"]] = {
            "name": data["name"],
            "total": 0,
            "version": {}
        }
        container["total"] += 1


class WeeklyModel(BaseModel):
    product_id = fields.IntField(description="产品id")
    project_id = fields.IntField(description="项目id")
    version = fields.CharField(255, description="版本号")
    task_item = fields.TextField(description="任务明细和进度")
    start_time = fields.DatetimeField(default=datetime.now, description="开始时间")
    end_time = fields.DatetimeField(default=datetime.now, onupdate=datetime.now, description="结束时间")
    desc = fields.TextField(description="备注")

    class Meta:
        table = "test_work_weekly"
        table_description = "周报明细表"


WeeklyConfigModelPydantic = pydantic_model_creator(WeeklyConfigModel, name="WeeklyConfigModel")
WeeklyModelPydantic = pydantic_model_creator(WeeklyModel, name="WeeklyModel")
