from ..base_model import fields, pydantic_model_creator, NumFiled


class BugTrack(NumFiled):
    business_id = fields.IntField(index=True, description="业务线id")
    name = fields.CharField(255, default='', description="bug名")
    detail = fields.TextField(default='', null=True, description="bug详情")
    iteration = fields.CharField(128, default='', null=True, description="迭代")
    bug_from = fields.CharField(128, default='', description="缺陷来源")
    trigger_time = fields.CharField(128, default='', null=True, description="发现时间")
    manager = fields.IntField(null=True, description="跟进负责人")
    reason = fields.CharField(128, default='', null=True, description="原因")
    solution = fields.CharField(128, default='', null=True, description="解决方案")
    status = fields.CharField(64, default='todo', description="bug状态，todo：待解决、doing：解决中、done：已解决")
    replay = fields.IntField(default=0, description="是否复盘，0：未复盘，1：已复盘")
    conclusion = fields.TextField(default='', null=True, description="复盘结论")

    class Meta:
        table = "test_work_bug_track"
        table_description = "生产Bug跟踪表"


BugTrackPydantic = pydantic_model_creator(BugTrack, name="BugTrack")
