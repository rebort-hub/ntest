import os
from fastapi import Request, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse

from ...schemas.autotest import element as schema
from ...models.autotest.model_factory import AppProject, AppModule, AppPage, AppElement, AppCase, AppStep, UiProject, \
    UiModule, UiPage, UiElement, UiCase, UiStep, AppCaseSuite, UiCaseSuite
from ...models.config.config import Config
from utils.parse.parse_excel import parse_file_content
from utils.util.file_util import STATIC_ADDRESS


async def get_element_list(request: Request, form: schema.ElementListForm = Depends()):
    model = AppElement if request.app.test_type == "app" else UiElement

    get_filed = model.get_simple_filed_list()
    if form.detail:
        get_filed.extend(["by", "element", "wait_time_out", "page_id"])
    query_data = await form.make_pagination(model, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_element_sort(request: Request, form: schema.ChangeSortForm):
    model = AppElement if request.app.test_type == "app" else UiElement
    await model.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def change_element_by_id(request: Request, form: schema.ChangeElementByIdForm):
    model = AppElement if request.app.test_type == "app" else UiElement
    await model.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def get_element_template(request: Request):
    return FileResponse(os.path.join(STATIC_ADDRESS, "element_upload_template.xls"))


async def element_upload(request: Request, file: UploadFile = File(), page_id: str = Form()):
    page_model, element_model = AppPage, AppElement
    if request.app.test_type != "app":
        page_model, element_model = UiPage, UiElement

    page = await page_model.filter(id=page_id).first()
    if page is None:
        return request.app.fail("页面不存在")

    if not file or file.filename.endswith("xls") is False:
        return request.app.fail("请上传后缀为xls的Excel文件")
    # [{"元素名称": "账号输入框", "定位方式": "根据id属性定位", "元素表达式": "account", "等待元素出现的超时时间": 10.0}]
    excel_data = parse_file_content(await file.read())
    option_dict = {option["label"]: option["value"] for option in await Config.get_find_element_by_app()}
    element_list = []
    for element_data in excel_data:
        name, by = element_data.get("元素名称"), element_data.get("定位方式")
        element, wait_time_out = element_data.get("元素表达式"), element_data.get("等待元素出现的超时时间")
        if all((name, by, element, wait_time_out)):
            element_list.append(element_model(
                name=name,
                by=option_dict[by] if by in option_dict else "id",
                element=element,
                wait_time_out=wait_time_out,
                project_id=page.project_id,
                module_id=page.module_id,
                page_id=page.id,
                create_user=request.state.user.id,
                update_user=request.state.user.id
            ))
    if len(element_list) > 0:
        await element_model.bulk_create(element_list)
    return request.app.success("元素导入成功")


async def get_element_from(request: Request, form: schema.GetElementForm = Depends()):
    project_model, module_model, page_model, element_model = AppProject, AppModule, AppPage, AppElement
    if request.app.test_type != "app":
        project_model, module_model, page_model, element_model = UiProject, UiModule, UiPage, UiElement

    element = await element_model.validate_is_exist("元素不存在", id=form.id)
    project = await project_model.filter(id=element.project_id).first().values("name")
    module_name = await module_model.get_from_path(element.module_id)
    page = await page_model.filter(id=element.page_id).first().values("name")
    return request.app.get_success(f'此元素归属：【{project["name"]}_{module_name}_{page["name"]}_{element.name}】')


async def get_element_detail(request: Request, form: schema.GetElementForm = Depends()):
    model = AppElement if request.app.test_type == "app" else UiElement
    data = await model.filter(id=form.id).first()
    return request.app.get_success(data)


async def add_element(request: Request, form: schema.AddElementForm):
    model = AppElement if request.app.test_type == "app" else UiElement
    max_num = await model.get_max_num()
    data_list = [{
        "project_id": form.project_id,
        "module_id": form.module_id,
        "page_id": form.page_id,
        "num": max_num + index + 1,
        **element.dict()} for index, element in enumerate(form.element_list)]
    await model.batch_insert(data_list, request.state.user)
    return request.app.post_success()


async def change_element(request: Request, form: schema.EditElementForm):
    model = AppElement if request.app.test_type == "app" else UiElement
    data = form.get_update_data(request.state.user.id)
    if request.app.test_type == "ui":
        data.pop("template_device")
    await model.filter(id=form.id).update(**data)
    return request.app.put_success()


async def delete_element(request: Request, form: schema.GetElementForm):
    project_model, suite_model, element_model, case_model, step_model = AppProject, AppCaseSuite, AppElement, AppCase, AppStep
    if request.app.test_type != "app":
        project_model, suite_model, element_model, case_model, step_model = UiProject, UiCaseSuite, UiElement, UiCase, UiStep

    element = await element_model.validate_is_exist("元素不存在", id=form.id)
    step = await step_model.filter(element_id=element.id).first().values("case_id", "name")
    if step:
        case = await case_model.filter(id=step["case_id"]).first()
        case_from = await case.get_quote_case_from(project_model, suite_model)
        raise ValueError(f'步骤【{case_from}/{step["name"]}】已引用此元素，请先解除引用')

    await element.model_delete()
    return request.app.delete_success()
