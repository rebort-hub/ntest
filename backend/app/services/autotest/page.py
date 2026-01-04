from fastapi import Request, Depends

from ...models.autotest.model_factory import AppPage, AppElement, UiPage, UiElement
from ...schemas.autotest import page as schema


async def get_page_list(request: Request, form: schema.PageListForm = Depends()):
    model = AppPage if request.app.test_type == "app" else UiPage
    get_filed = model.get_simple_filed_list()
    if form.detail:
        get_filed.extend(["module_id", "project_id"])
    query_data = await form.make_pagination(model, user=request.state.user)
    return request.app.get_success(data=query_data)


async def change_page_sort(request: Request, form: schema.ChangeSortForm):
    model = AppPage if request.app.test_type == "app" else UiPage
    await model.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def copy_page(request: Request, form: schema.GetPageForm):
    page_model, element_model = UiPage, UiElement
    if request.app.test_type == "app":
        page_model, element_model = AppPage, AppElement
    old_page = await page_model.filter(id=form.id).first()
    new_page = await page_model.model_create(dict(old_page), user=request.state.user)  # 创建页面
    await element_model.copy_element(old_page.id, new_page.id, request.state.user)  # 复制元素
    return request.app.success("复制成功", data=new_page)


async def get_page_detail(request: Request, form: schema.GetPageForm = Depends()):
    model = AppPage if request.app.test_type == "app" else UiPage
    data = await model.filter(id=form.id).first()
    return request.app.get_success(data)


async def add_page(request: Request, form: schema.AddPageForm):
    model = AppPage if request.app.test_type == "app" else UiPage
    max_num = await model.get_max_num()
    page_list = [{
        "project_id": form.project_id,
        "module_id": form.module_id,
        "num": max_num + index + 1,
        **page.dict()} for index, page in enumerate(form.page_list)]

    if len(page_list) == 1:
        return request.app.post_success(data=dict(await model.create(**page_list[0])))
    await model.batch_insert(page_list, request.state.user)
    return request.app.post_success()


async def change_page(request: Request, form: schema.EditPageForm):
    model = AppPage if request.app.test_type == "app" else UiPage
    await model.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_page(request: Request, form: schema.GetPageForm):
    page_model, element_model = UiPage, UiElement
    if request.app.test_type == "app":
        page_model, element_model = AppPage, AppElement
    await element_model.validate_is_not_exist(msg="当前页面下有元素，请先删除元素，再删除页面", page_id=form.id)
    await page_model.filter(id=form.id).delete()
    return request.app.delete_success()
