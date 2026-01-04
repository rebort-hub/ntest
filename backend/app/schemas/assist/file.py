from typing import Optional
from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm


class GetFileListForm(PaginationForm):
    """ 获取文件列表 """
    page_size: Optional[int] = Field(default=1)
    page_no: Optional[int] = Field(default=20)
    file_type: Optional[str] = Field(default="case", title='文件类型')


class CheckFileIsExistsForm(BaseForm):
    """ 校验文件是否存在 """
    file_name: str = Field(..., title='文件名')
    file_type: str = Field(..., title='文件类型')
