from pydantic import Field

from ..base_form import BaseForm


class GetSsoTokenForm(BaseForm):
    code: str = Field(..., title="登录code")
