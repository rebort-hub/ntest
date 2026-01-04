import os

from faker import Faker
from fastapi import Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List

from utils.make_data import make_user_tools
from utils.util.file_util import FileUtil, TEMP_FILE_ADDRESS
from ...schemas.base_form import BaseForm

class MakeUserModel(BaseForm):
    language: str
    count: int
    options: list


async def make_user_list(request: Request, form: MakeUserModel ):
    all_data, fake = [], Faker(form.language)
    for option in form.options:
        temp_data = []
        if hasattr(fake, option) or option == "credit_code":
            i = 0
            while True:
                if i >= form.count:
                    break
                data = make_user_tools.get_credit_code() if option == "credit_code" else getattr(fake, option)()
                if data not in temp_data:
                    temp_data.append(data)
                    i += 1
        all_data.append(temp_data)
    return request.app.success("获取成功", data=[dict(zip(form.options, data)) for data in zip(*all_data)])


class ContactList(BaseModel):
    name: str
    phone_number: str


class MakeContactModel(BaseModel):
    language: str
    count: int
    data_list: List[ContactList]


async def make_contact_list(request: Request, form: MakeContactModel):
    # 数据解析为通讯录格式
    contact_text = ''
    for index, data in enumerate(form.data_list):
        dict_data = data.dict()
        if index >= form.count:
            break
        contact_text += f'BEGIN:VCARD\nVERSION:2.1\nFN:{dict_data.get("name", f"name_{index}")}\nTEL;CELL:{dict_data.get("phone_number", "")}\nEND:VCARD\n'

    # 写入到文件
    file_name = f'通讯录_{request.state.user.id}_{form.language}_{form.count}条.vcf'
    file_path = os.path.join(TEMP_FILE_ADDRESS, file_name)
    with open(file_path, "w", encoding='utf-8') as fp:
        fp.write(contact_text)

    return FileResponse(os.path.join(TEMP_FILE_ADDRESS, file_name))
