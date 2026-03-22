from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, ChangeSortForm
from app.schemas.enums import TriggerTypeEnum


class UseCountForm(BaseForm):
    time_slot: int = Field(..., title="时间切片")


class AnalyseForm(BaseForm):
    business_id: int = Field(..., title="业务线id")
    trigger_type: Optional[TriggerTypeEnum] = Field(default=None, title="触发类型")
    start_time: Optional[str] = Field(default=None, title="开始时间")
    end_time: Optional[str] = Field(default=None, title="结束时间")
