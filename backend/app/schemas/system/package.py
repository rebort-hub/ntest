from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, ChangeSortForm

class PackageInstallForm(BaseForm):
    name: str = Field(..., title="包名")
    version: Optional[str] = Field(default=None, title="包版本")
