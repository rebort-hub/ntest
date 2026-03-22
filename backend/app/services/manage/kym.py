import os

from fastapi import Request, Depends
from fastapi.responses import FileResponse

from ...models.manage.model_factory import KYMModule
from ...models.config.model_factory import Config
from utils.util.file_util import TEMP_FILE_ADDRESS, FileUtil
from utils.make_data.make_xmind import make_xmind
from ...schemas.manage import kym as schema


async def get_kym_project_list(request: Request):
    data_list = await KYMModule.filter().distinct().values("project")
    return request.app.get_success(data=[{"key": data["project"], "value": data["project"]} for data in data_list])


async def download_kym_as_xmind(request: Request, form: schema.KymProjectForm = Depends()):
    project = await KYMModule.filter(project=form.project).first()
    file_path = os.path.join(TEMP_FILE_ADDRESS, f"{project.project}.xmind")
    FileUtil.delete_file(file_path)
    make_xmind(file_path, project.kym)
    return FileResponse(file_path)


async def add_kym_project(request: Request, form: schema.KymProjectForm):
    kym_data = {"nodeData": {"topic": form.project, "root": True, "children": []}}
    kym_data["nodeData"]["children"] = await Config.get_kym()
    data = await KYMModule.model_create({"project": form.project, "kym": kym_data}, request.state.user)
    return request.app.post_success(data)


async def get_kym_detail(request: Request, form: schema.KymProjectForm = Depends()):
    kym = await KYMModule.filter(project=form.project).first()
    return request.app.get_success(data=kym)


async def change_kym(request: Request, form: schema.ChangeKymForm):
    await KYMModule.filter(project=form.project).update(kym=form.kym, update_user=request.state.user.id)
    return request.app.put_success()
