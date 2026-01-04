import os

from fastapi.responses import FileResponse
from fastapi import Request, UploadFile, File, Form, Depends

from ...models.autotest.model_factory import ApiModule, ApiCaseSuite, ApiCase, ApiStep, AppCaseSuite, AppCase, AppStep, \
    UiCaseSuite, UiCase, UiStep
from ...models.autotest.page import ApiMsg
from ...schemas.autotest import suite as schema
from utils.make_data.make_xmind import get_xmind_first_sheet_data
from utils.util.file_util import STATIC_ADDRESS, TEMP_FILE_ADDRESS
from ...schemas.enums import CaseStatusEnum, DataStatusEnum


async def get_suite_list(request: Request, form: schema.FindCaseSuite = Depends()):
    model = ApiCaseSuite if request.app.test_type == "api" else AppCaseSuite if request.app.test_type == "app" else UiCaseSuite
    get_filed = ["id", "name", "parent", "project_id", "suite_type"]
    query_data = await form.make_pagination(model, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def get_suite_template(request: Request):
    return FileResponse(os.path.join(STATIC_ADDRESS, "case_suite_upload_template.xmind"))


async def upload_suite(request: Request, file: UploadFile = File(), project_id: str = Form()):
    suite_model, case_model = ApiCaseSuite, ApiCase
    if request.app.test_type == "app":
        suite_model, case_model = AppCaseSuite, AppCase
    elif request.app.test_type == "ui":
        suite_model, case_model = UiCaseSuite, UiCase

    if project_id is None:
        return request.app.fail("服务必传")

    if file and file.filename.endswith("xmind"):
        # 保存文件
        file_path = os.path.join(TEMP_FILE_ADDRESS, file.filename)
        file_content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(file_content)

        # 读取文件内容，并创建数据
        xmind_data = get_xmind_first_sheet_data(file_path)
        upload_res = await suite_model.upload(project_id, xmind_data, case_model)
        return request.app.success("导入完成", upload_res)
    return request.app.fail("文件格式错误")


async def change_suite_sort(request: Request, form: schema.ChangeSortForm):
    model = ApiCaseSuite if request.app.test_type == "api" else AppCaseSuite if request.app.test_type == "app" else UiCaseSuite
    await model.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_suite_detail(request: Request, form: schema.GetCaseSuiteForm = Depends()):
    model = ApiCaseSuite if request.app.test_type == "api" else AppCaseSuite if request.app.test_type == "app" else UiCaseSuite
    suite = await model.filter(id=form.id).first()
    return request.app.get_success(data=suite)


async def copy_suite(request: Request, form: schema.CopyCaseSuiteForm):
    suite_model, case_model, step_model = ApiCaseSuite, ApiCase, ApiStep
    if request.app.test_type == "app":
        suite_model, case_model, step_model = AppCaseSuite, AppCase, AppStep
    elif request.app.test_type == "ui":
        suite_model, case_model, step_model = UiCaseSuite, UiCase, UiStep
    from_suite, parent_suite = await suite_model.filter(id=form.id).first(), await suite_model.filter(
        id=form.parent).first()

    async def deep_copy_suite(
            from_suite, parent_suite, suite_model, case_model, step_model, request_user, is_deep=False):
        # 复制用例集，如果已经有同名的用例集，则把已存在，将下属的用例集和用例复制到该用例集下面
        new_suite = await suite_model.filter(parent=parent_suite.id, name=from_suite.name).order_by("num").first()
        if new_suite is None:
            from_suite.project_id, from_suite.parent = parent_suite.project_id, parent_suite.id
            from_suite.suite_type, from_suite.num = parent_suite.suite_type, parent_suite.num + 1
            new_suite = await suite_model.model_create(dict(from_suite), request_user)

        # 复制用例
        case_id_list = await case_model.filter(suite_id=from_suite.id).order_by("num").all().values("id")
        for case_id in case_id_list:
            old_case = await case_model.filter(id=case_id["id"]).first()
            old_case.suite_id = new_suite.id
            new_case = await case_model.model_create(dict(old_case), request_user)

            # 复制步骤
            step_id_list = await step_model.filter(case_id=old_case.id).order_by("num").all().values("id")
            for step_id in step_id_list:
                old_step = await step_model.filter(id=step_id["id"]).first()
                old_step.case_id = new_case.id
                await step_model.model_create(dict(old_step), request_user)

        # 如果用例集下还有用例集，则递归复制用例集下的用例集和用例
        if is_deep:
            if child_suite_list := await suite_model.filter(parent=from_suite.id).all():
                for child_suite in child_suite_list:
                    await deep_copy_suite(
                        child_suite, new_suite, suite_model, case_model, step_model, request_user, is_deep)

    await deep_copy_suite(from_suite, parent_suite, suite_model, case_model, step_model, request.state.user, form.deep)
    return request.app.success("复制成功")


async def api_module_to_suite(request: Request, form: schema.ModuleToCaseSuiteForm):
    module_model, suite_model, case_model, step_model = ApiModule, ApiCaseSuite, ApiCase, ApiStep
    module = await module_model.filter(id=form.module).first()
    api_list = await ApiMsg.filter(module_id=module.id).order_by("num").all()

    module_suite = await suite_model.filter(parent=form.parent, name=module.name).order_by("num").first()
    if module_suite is None:
        parent = await suite_model.filter(id=form.parent).first()
        module_data = {
            "project_id": parent.project_id, "parent": parent.id,
            "name": module.name, "suite_type": parent.suite_type
        }
        module_suite = await suite_model.model_create(module_data, request.state.user)

    for index, api in enumerate(api_list):
        # 创建用例集
        suite_name = f'{api.method.value} - {api.addr.split("?")[0]}'
        suite = await suite_model.filter(parent=module_suite.id, name=suite_name).first()
        if suite is None:
            suite_data = {
                "project_id": module_suite.project_id, "parent": module_suite.id, "name": suite_name,
                "suite_type": module_suite.suite_type, "num": index + 1,
            }
            suite = await suite_model.model_create(suite_data, request.state.user)

        # 创建用例
        case = await case_model.filter(suite_id=suite.id, name=api.name).first()
        if case is None:
            case_data = {
                "suite_id": suite.id, "status": CaseStatusEnum.NOT_DEBUG_AND_NOT_RUN.value,
                "name": api.name, "desc": api.name,
            }
            case = await case_model.model_create(case_data, request.state.user)

            # 创建步骤
            step_data = {
                "case_id": case.id, "api_id": api.id, "name": api.name, "time_out": api.time_out,
                "headers": api.headers, "status": DataStatusEnum.ENABLE, "params": api.params,
                "data_form": api.data_form, "data_urlencoded": api.data_urlencoded, "data_json": api.data_json,
                "data_text": api.data_text, "body_type": api.body_type, "extracts": api.extracts, "validates": api.validates
            }
            await step_model.model_create(step_data, request.state.user)
    return request.app.success("创建成功")


async def add_suite(request: Request, form: schema.AddCaseSuiteForm):
    model = ApiCaseSuite if request.app.test_type == "api" else AppCaseSuite if request.app.test_type == "app" else UiCaseSuite
    max_num = await model.get_max_num()
    suite_list = [{
        "project_id": form.project_id,
        "suite_type": form.suite_type,
        "parent": form.parent,
        "name": suite_name,
        "num": max_num + index + 1
    } for index, suite_name in enumerate(form.data_list)]
    await model.batch_insert(suite_list, request.state.user)
    return request.app.post_success()


async def change_suite(request: Request, form: schema.EditCaseSuiteForm):
    model = ApiCaseSuite if request.app.test_type == "api" else AppCaseSuite if request.app.test_type == "app" else UiCaseSuite
    suite = await model.validate_is_exist("用例集不存在", id=form.id)
    await model.filter(id=form.id).update(**form.get_update_data(request.state.user.id))

    # 如果是否修改了用例集类型，则把子用例集的类型一并修改
    if form.parent is None and form.suite_type != suite.suite_type:
        suite.suite_type = form.suite_type
        await suite.update_children_suite_type()
    return request.app.put_success(form.dict())


async def delete_suite(request: Request, form: schema.GetCaseSuiteForm):
    suite_model, case_model, step_model = ApiCaseSuite, ApiCase, ApiStep
    if request.app.test_type == "app":
        suite_model, case_model, step_model = AppCaseSuite, AppCase, AppStep
    elif request.app.test_type == "ui":
        suite_model, case_model, step_model = UiCaseSuite, UiCase, UiStep

    waite_delete_suite_list, waite_delete_case_list, waite_delete_step_list = [], [], []
    async def get_waite_delete_data(suite_id):
        waite_delete_suite_list.append(suite_id)

        # 当前用例集下的用例列表
        case_list = [case["id"] for case in await case_model.filter(suite_id=suite_id).all().values("id")]
        if case_list:
            waite_delete_case_list.extend(case_list)

            # 如果有被引用的用例，直接返回
            step = await step_model.filter(quote_case__in=case_list).first().values("case_id")
            if step and step["case_id"]:
                step_case = await case_model.filter(id=step["case_id"]).first().values("name", "suite_id")
                suite = await suite_model.filter(id=step_case["suite_id"]).first().values("name")
                raise ValueError(f'用例集【{suite["name"]}】下的用例【{step_case["name"]}】已引用此次要删除的用例，请先解除引用')

            # 步骤列表
            step_list = [step["id"] for step in await step_model.filter(case_id__in=case_list).all().values("id")]
            waite_delete_step_list.extend(step_list)

        # 当前用例集下的用例集列表
        suite_list = [suite["id"] for suite in await suite_model.filter(parent=suite_id).all().values("id")]
        for suite_id in suite_list:
            await get_waite_delete_data(suite_id)

    await get_waite_delete_data(form.id)
    await step_model.filter(id__in=waite_delete_step_list).delete()
    await case_model.filter(id__in=waite_delete_case_list).delete()
    await suite_model.filter(id__in=waite_delete_suite_list).delete()
    return request.app.delete_success()
