from fastapi import Request, Depends
from selenium.webdriver.common.keys import Keys

from ...models.autotest.model_factory import ApiCase, ApiStep, AppCase, AppStep, UiCase, UiStep
from ...schemas.autotest import step as schema
from config import ui_action_mapping_list, ui_assert_mapping_list, ui_extract_mapping_list

async def get_step_list(request: Request, form: schema.GetStepListForm = Depends()):
    case_model, step_model = ApiCase, ApiStep
    if request.app.test_type == "app":
        case_model, step_model = AppCase, AppStep
    elif request.app.test_type == "ui":
        case_model, step_model = UiCase, UiStep

    step_obj_list = await step_model.filter(case_id=form.case_id).order_by("num").all()
    step_list = await step_model.set_has_step_for_step(step_obj_list, case_model)
    return request.app.get_success(data={"total": len(step_list), "data": step_list})


def get_step_execute_mapping(request: Request):
    return request.app.get_success(ui_action_mapping_list)

def get_step_extract_mapping(request: Request):
    return request.app.get_success(ui_extract_mapping_list)

def get_step_assert_mapping(request: Request):
    return request.app.get_success(ui_assert_mapping_list)

def get_step_key_board_code(request: Request):
    return request.app.get_success({key: f'按键【{key}】' for key in dir(Keys) if key.startswith('_') is False})


async def change_step_sort(request: Request, form: schema.ChangeSortForm):
    step_model = ApiStep if request.app.test_type == "api" else AppStep if request.app.test_type == "app" else UiStep
    await step_model.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def change_step_status(request: Request, form: schema.ChangeStepStatusForm):
    step_model = ApiStep if request.app.test_type == "api" else AppStep if request.app.test_type == "app" else UiStep
    await step_model.filter(id__in=form.id_list).update(status=form.status)
    return request.app.put_success()


async def change_step_element(request: Request, form: schema.ChangeStepElement):
    step_model = ApiStep if request.app.test_type == "api" else AppStep if request.app.test_type == "app" else UiStep
    data = {"api_id": form.element_id} if request.app.test_type == "api" else {"element_id": form.element_id}
    await step_model.filter(id=form.id).update(**data)
    return request.app.put_success()


async def copy_step(request: Request, form: schema.CopyStepForm):
    case_model, step_model = ApiCase, ApiStep
    if request.app.test_type == "app":
        case_model, step_model = AppCase, AppStep
    elif request.app.test_type == "ui":
        case_model, step_model = UiCase, UiStep

    step = await step_model.filter(id=form.id).first()
    # step.name = f'{step.name}_copy'
    if form.case_id:
        step.case_id = form.case_id
        step.num = await step_model.get_insert_num()
    new_step = await step_model.model_create(dict(step), request.state.user)
    await case_model.merge_output(new_step.case_id, [new_step])  # 合并出参

    return request.app.success("复制成功")


async def get_step_detail(request: Request, form: schema.GetStepForm = Depends()):
    step_model = ApiStep if request.app.test_type == "api" else AppStep if request.app.test_type == "app" else UiStep
    step = await step_model.validate_is_exist("步骤不存在", id=form.id)
    return request.app.get_success(data=step)


async def add_step(request: Request, form: schema.AddStepForm):
    case_model, step_model = ApiCase, ApiStep
    if request.app.test_type == "app":
        case_model, step_model = AppCase, AppStep
    elif request.app.test_type == "ui":
        case_model, step_model = UiCase, UiStep

    await form.validate_request()

    add_step_data = form.dict()
    add_step_data["num"] = await step_model.get_insert_num()
    step = await step_model.model_create(add_step_data, request.state.user)
    await case_model.merge_variables(step.quote_case, step.case_id)
    await case_model.merge_output(step.case_id, [int(step.quote_case) if step.quote_case else step])  # 合并出参

    return request.app.post_success()


async def change_step(request: Request, form: schema.EditStepForm):
    model = ApiStep if request.app.test_type == "api" else AppStep if request.app.test_type == "app" else UiStep
    await form.validate_request()

    update_data = form.get_update_data(request.state.user.id)
    if request.app.test_type == "api":
        pop_filed = ["element_id", "send_keys", "execute_type", "wait_time_out"]
    else:
        pop_filed = [
            "api_id", "headers", "params", "body_type", "data_form", "data_json", "data_urlencoded", "data_text",
            "replace_host", "pop_header_filed", "time_out", "allow_redirect"
        ]
    for filed in pop_filed:
        update_data.pop(filed)
    await model.filter(id=form.id).update(**update_data)
    return request.app.put_success()


async def delete_step(request: Request, form: schema.DeleteStepForm):
    step_model = ApiStep if request.app.test_type == "api" else AppStep if request.app.test_type == "app" else UiStep
    await step_model.filter(id__in=form.id_list).delete()
    return request.app.delete_success()
