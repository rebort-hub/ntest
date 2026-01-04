# -*- coding: utf-8 -*-
import asyncio
import copy
import os.path

from fastapi import Request, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse

from ...models.autotest.model_factory import ApiModule as Module, ApiProject as Project, ApiReport as Report, \
    ApiMsg as Api, ApiCase as Case, ApiCaseSuite as CaseSuite, ApiStep as Step
from ...schemas.autotest import api as schema
from utils.util.file_util import STATIC_ADDRESS
from utils.parse.parse_excel import parse_file_content
from utils.client.run_api_test import RunApi


async def get_api_list(request: Request, form: schema.ApiListForm = Depends()):
    get_filed = Api.get_simple_filed_list()
    if form.detail:
        get_filed.extend([
            "project_id", "module_id", "addr", "method", "use_count", "level", "status", "create_user"
        ])
    query_data = await form.make_pagination(Api, user=request.state.user, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_api_level(request: Request, form: schema.ChangeLevel):
    await Api.filter(id=form.id).update(level=form.level)
    return request.app.put_success()


async def change_api_status(request: Request, form: schema.ChangeStatus):
    await Api.filter(id=form.id).update(status=form.status)
    return request.app.put_success()


async def get_api_from(request: Request, form: schema.GetApiFromForm = Depends()):
    filter_dict = {"id": form.id} if form.id else {"addr__icontains": form.api_addr}
    api_list = await Api.filter(**filter_dict).all()

    api_from_list = []
    for api in api_list:  # 多个接口存在同一个接口地址的情况
        project = await Project.filter(id=api.project_id).first()
        module_name = await Module.get_from_path(api.module_id)
        api_dict = dict(api)
        api_dict["from"] = f'【{project.name}_{module_name}_{api.name}】'
        api_from_list.append(api_dict)
    return request.app.get_success(data=api_from_list)


async def get_api_use(request: Request, form: schema.GetApiFromForm = Depends()):
    await form.validate_request()
    filter_dict = {"id": form.id} if form.id else {"addr__icontains": form.api_addr}
    api_list = await Api.filter(**filter_dict).all()

    case_list, case_dict, project_dict = [], {}, {}  # 可能存在重复获取数据的请，获取到就存下来，一条数据只查一次库
    for api in api_list:  # 多个接口存在同一个接口地址的情况
        for step in await Step.filter(api_id=api.id).all():  # 存在一个接口在多个步骤调用的情况
            # 获取步骤所在的用例
            if step.case_id not in case_dict:
                case_dict[step.case_id] = await Case.filter(id=step.case_id).first()
            case = case_dict[step.case_id]

            # 获取用例所在的用例集
            suite = await CaseSuite.filter(id=case.suite_id).first()
            suite_from_path = await CaseSuite.get_from_path(suite.id)

            # 获取用例集所在的接口
            if suite.project_id not in project_dict:
                project_dict[suite.project_id] = await Project.filter(id=suite.project_id).first()
            project = project_dict[suite.project_id]

            case_dict = dict(case)
            case_dict["from"] = f'【{project.name if project else None}_{suite_from_path}_{case.name}_{step.name}】'
            case_list.append(copy.deepcopy(case_dict))
    return request.app.get_success(data=case_list)


async def get_api_template(request: Request):
    return FileResponse(os.path.join(STATIC_ADDRESS, "api_upload_template.xls"))


async def upload_api(request: Request, file: UploadFile = File(), module_id: str = Form()):
    module = await Module.filter(id=module_id).first()
    if not module:
        return request.app.fail("模块不存在")
    if file and file.filename.endswith("xls"):
        # [{"请求类型": "get", "接口名称": "xx接口", "addr": "/api/v1/xxx"}]
        excel_data = parse_file_content(await file.read())
        api_list = []
        for api_data in excel_data:
            new_api = Api()
            for key, value in api_data.items():
                if hasattr(new_api, key):
                    setattr(new_api, key, value)
            new_api.method = api_data.get("method", "post").upper()
            new_api.project_id = module.project_id
            new_api.module_id = module.id
            new_api.create_user = request.state.user.id
            api_list.append(new_api)
        await Api.bulk_create(api_list)
        return request.app.success("接口导入成功")
    return request.app.fail("请上传后缀为xls的Excel文件")


async def change_api_sort(request: Request, form: schema.ChangeSortForm):
    await Api.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_api_detail(request: Request, form: schema.GetApiForm = Depends()):
    api = await Api.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(api)


async def add_api(request: Request, form: schema.AddApiForm):
    max_num = await Api.get_max_num()
    data_list = [{
        "project_id": form.project_id,
        "module_id": form.module_id,
        "num": max_num + index + 1,
        **api.dict()
    } for index, api in enumerate(form.api_list)]
    await Api.batch_insert(data_list, request.state.user)
    return request.app.post_success()


async def change_api(request: Request, form: schema.EditApiForm):
    await Api.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_api(request: Request, form: schema.DeleteApiForm):
    step = await Step.filter(api_id=form.id).first().values("case_id")
    if step and step.get("case_id"):
        case_name = await Case.filter(id=step.get("case_id")).first().values("name")
        raise ValueError(f"用例【{case_name['name']}】已引用此接口，请先解除引用")

    await Api.filter(id=form.id).delete()
    return request.app.delete_success()


async def run_api(request: Request, form: schema.RunApiMsgForm):
    run_api_list = [api["id"] for api in await Api.filter(id__in=form.id_list).all().values("id")]
    if len(run_api_list) == 0:
        ValueError(f"接口不存在")
    first_api = await Api.filter(id=run_api_list[0]).first().values("name", "project_id")

    batch_id = Report.get_batch_id(request.state.user.id)
    summary = Report.get_summary_template()
    for env_code in form.env_list:
        summary["env"]["code"], summary["env"]["name"] = env_code, env_code
        report = await Report.get_new_report(
            batch_id=batch_id,
            trigger_id=form.id_list,
            name=first_api["name"],
            run_type="api",
            env=env_code,
            create_user=request.state.user.id,
            project_id=first_api["project_id"],
            summary=summary
        )

        asyncio.create_task(RunApi(
            api_id_list=run_api_list, report_id=report.id, env_code=env_code, env_name=env_code
        ).parse_and_run())

    return request.app.trigger_success({"batch_id": batch_id})
