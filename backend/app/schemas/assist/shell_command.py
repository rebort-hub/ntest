from pydantic import Field

from ..base_form import BaseForm, PaginationForm, ChangeSortForm

class GetShellCommandRecordList(PaginationForm):
    """ 获取shell命令发送记录列表 """
    command: str = Field(..., title='shell命令')

    def get_query_filter(self, *args, **kwargs):
        """ 查询条件 """
        return {"command": self.command}


class GetShellCommandRecord(BaseForm):
    """ 获取shell命令发送记录 """
    id: int = Field(..., title='数据id')


class SendShellCommand(BaseForm):
    """ 发送shell命令 """
    file_content: str = Field(..., title='文件数据')
    command: str = Field(..., title='shell命令')
