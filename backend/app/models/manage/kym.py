from ..base_model import fields, pydantic_model_creator, BaseModel


class KYMModule(BaseModel):
    project = fields.CharField(255, unique=True, description="服务名")
    kym = fields.JSONField(default={}, description="kym分析")

    class Meta:
        table = "test_work_kym"
        table_description = "KYM分析表"


KYMModulePydantic = pydantic_model_creator(KYMModule, name="KYMModule")
