from ..base_model import fields, BaseModel, NumFiled
from app.schemas.enums import TodoListEnum


class Todo(NumFiled):
    status = fields.CharEnumField(TodoListEnum, default=TodoListEnum.TODO, description="状态")
    title = fields.CharField(512, null=True, default='', description="任务title")
    done_user = fields.IntField(null=True, description="完成人")
    done_time = fields.DatetimeField(null=True, description="完成时间")
    detail = fields.CharField(2048, null=True, default='', description="任务详情")

    class Meta:
        table = "test_work_todo"
        table_description = "待处理任务"
