from fastapi import Request, Depends, BackgroundTasks

from utils.client.run_api_test import RunCase as RunApiCase
from utils.client.run_ui_test import RunCase as RunUiCase
from app.schemas.enums import CaseStatusEnum
from ...models.autotest.model_factory import ApiCaseSuite, ApiCase, ApiStep, AppCaseSuite, AppCase, AppStep, \
    UiCaseSuite, UiCase, UiStep, ApiProject, AppProject, UiProject, ApiProjectEnv, AppProjectEnv, UiProjectEnv, \
    ApiReport, AppReport, UiReport, AppRunServer, AppRunPhone
from ...models.config.config import Config
from ...models.config.run_env import RunEnv
from ...models.system.user import User
from ...schemas.autotest import case as schema


async def get_case_list(request: Request, form: schema.FindCaseForm = Depends()):
    case_model, step_model = ApiCase, ApiStep
    if request.app.test_type == "app":
        case_model, step_model = AppCase, AppStep
    elif request.app.test_type == "ui":
        case_model, step_model = UiCase, UiStep

    get_filed = case_model.get_simple_filed_list()
    if form.detail:
        get_filed.extend([
            "desc", "status", "skip_if", "variables", "output", "suite_id", "run_times", "create_user", "update_user"
        ])
        if request.app.test_type == "api":
            get_filed.extend(["headers"])
    query_data = await form.make_pagination(case_model, get_filed=get_filed)
    if form.has_step:
        total, data_list = query_data["total"], await step_model.set_has_step_for_case(query_data["data"])
        return request.app.get_success(data={"total": total, "data": data_list})
    return request.app.get_success(data=query_data)


async def change_case_sort(request: Request, form: schema.ChangeSortForm):
    model = ApiCase if request.app.test_type == "api" else AppCase if request.app.test_type == "app" else UiCase
    await model.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_make_data_case_list(request: Request, form: schema.GetAssistCaseForm = Depends()):
    case_model, suite_model = ApiCase, ApiCaseSuite
    if request.app.test_type == "app":
        case_model, suite_model = AppCase, AppCaseSuite
    elif request.app.test_type == "ui":
        case_model, suite_model = UiCase, UiCaseSuite
    case_list = await suite_model.get_make_data_case(form.project_id, case_model)
    return request.app.get_success(data={"total": len(case_list), "data": case_list})


async def get_case_name(request: Request, form: schema.GetCaseNameForm = Depends()):
    model = ApiCase if request.app.test_type == "api" else AppCase if request.app.test_type == "app" else UiCase
    case_list = await model.filter(id__in=form.case_list).all().values("id", "name")
    data = [{"id": case["id"], "name": case["name"]} for case in case_list]
    return request.app.get_success(data=data)


async def get_case_project(request: Request, form: schema.GetCaseForm = Depends()):
    case_model, suite_model, project_model = ApiCase, ApiCaseSuite, ApiProject
    if request.app.test_type == "app":
        case_model, suite_model, project_model = AppCase, AppCaseSuite, AppProject
    elif request.app.test_type == "ui":
        case_model, suite_model, project_model = UiCase, UiCaseSuite, UiProject
    case = await case_model.validate_is_exist("用例不存在", id=form.id)
    suite = await suite_model.filter(id=case.suite_id).first()
    project = await project_model.filter(id=suite.project_id).first()
    return request.app.get_success(data={"case": case, "suite": suite, "project": project})


async def change_case_status(request: Request, form: schema.ChangeCaseStatusForm):
    model = ApiCase if request.app.test_type == "api" else AppCase if request.app.test_type == "app" else UiCase
    await model.filter(id__in=form.id_list).update(status=form.status.value)
    return request.app.put_success()


async def change_case_parent(request: Request, form: schema.ChangeCaseParentForm):
    model = ApiCase if request.app.test_type == "api" else AppCase if request.app.test_type == "app" else UiCase
    await model.filter(id__in=form.id_list).update(suite_id=form.suite_id)
    return request.app.put_success()


async def copy_case(request: Request, form: schema.DeleteCaseForm):
    case_model, step_model = ApiCase, ApiStep
    if request.app.test_type == "app":
        case_model, step_model = AppCase, AppStep
    elif request.app.test_type == "ui":
        case_model, step_model = UiCase, UiStep

    for case_id in form.id_list:
        case = await case_model.filter(id=case_id).first()
        if not case:
            continue

        # 复制用例
        old_case = dict(case)
        # old_case["name"], old_case["status"] = old_case["name"] + "_copy", CaseStatusEnum.NOT_DEBUG_AND_NOT_RUN.value
        old_case["status"] = CaseStatusEnum.NOT_DEBUG_AND_NOT_RUN.value
        new_case = await case_model.model_create(old_case, request.state.user)

        # 复制步骤
        old_step_list = await step_model.filter(case_id=case.id).order_by("num").all()
        for index, old_step in enumerate(old_step_list):
            step = dict(old_step)
            step["case_id"] = new_case.id
            await step_model.model_create(step, request.state.user)
    return request.app.success("复制成功", data=new_case if len(form.id_list) == 1 else None)


async def case_from(request: Request, form: schema.GetCaseForm = Depends()):
    case_model, suite_model, project_model = ApiCase, ApiCaseSuite, ApiProject
    if request.app.test_type == "app":
        case_model, suite_model, project_model = AppCase, AppCaseSuite, AppProject
    elif request.app.test_type == "ui":
        case_model, suite_model, project_model = UiCase, UiCaseSuite, UiProject

    case = await case_model.validate_is_exist("用例不存在", id=form.id)
    from_path = await case.get_quote_case_from(project_model, suite_model)
    return request.app.get_success(data=from_path)


async def case_copy_step(request: Request, form: schema.CopyCaseStepForm):
    case_model, step_model = ApiCase, ApiStep
    if request.app.test_type == "app":
        case_model, step_model = AppCase, AppStep
    elif request.app.test_type == "ui":
        case_model, step_model = UiCase, UiStep

    # 复制指定用例的步骤到当前用例下
    step_list, insert_num = [], await step_model.get_insert_num()
    from_step_list = await step_model.filter(case_id=form.from_case).order_by("num").all()

    for index, step in enumerate(from_step_list):
        step_dict = dict(step)
        step_dict["case_id"], step_dict["num"] = form.to_case, insert_num + index
        new_step = await step_model.model_create(step_dict, request.state.user)
        step_list.append(dict(new_step))
    await case_model.merge_output(form.to_case, step_list)  # 合并出参
    await case_model.merge_variables(form.from_case, form.to_case)
    return request.app.success("步骤复制成功，自定义变量已合并至当前用例", data=step_list)


async def get_case_detail(request: Request, form: schema.GetCaseForm = Depends()):
    model = ApiCase if request.app.test_type == "api" else AppCase if request.app.test_type == "app" else UiCase
    case = await model.filter(id=form.id).first()
    return request.app.get_success(data=case)


async def add_case(request: Request, form: schema.AddCaseForm):
    model = ApiCase if request.app.test_type == "api" else AppCase if request.app.test_type == "app" else UiCase
    max_num = await model.get_max_num()
    data_list = [{
        "suite_id": form.suite_id,
        "num": max_num + index + 1,
        **case.dict()
    } for index, case in enumerate(form.case_list)]

    if len(data_list) == 1:
        return request.app.post_success(await model.model_create(data_list[0], request.state.user))
    await model.batch_insert(data_list, request.state.user)
    return request.app.post_success()


async def change_case(request: Request, form: schema.EditCaseForm):
    project_model, project_env_model, suite_model, case_model = ApiProject, ApiProjectEnv, ApiCaseSuite, ApiCase
    if request.app.test_type == "app":
        project_model, project_env_model, suite_model, case_model = AppProject, AppProjectEnv, AppCaseSuite, AppCase
    elif request.app.test_type == "ui":
        project_model, project_env_model, suite_model, case_model = UiProject, UiProjectEnv, UiCaseSuite, UiCase

    suite = await suite_model.filter(id=form.suite_id).first().values("project_id")
    project = await project_model.filter(id=suite["project_id"]).first().values("id", "script_list")
    project_env = await project_env_model.filter(project_id=project["id"]).first().values("variables")

    await form.validate_request(
        project_script_list=project["script_list"], project_env_variables=project_env["variables"])
    update_data = form.get_update_data(request.state.user.id)
    if request.app.test_type != "api":
        update_data.pop("headers")
    await case_model.filter(id=form.id).update(**update_data)
    return request.app.put_success()


async def delete_case(request: Request, form: schema.DeleteCaseForm):
    case_model, step_model = ApiCase, ApiStep
    if request.app.test_type == "app":
        case_model, step_model = AppCase, AppStep
    elif request.app.test_type == "ui":
        case_model, step_model = UiCase, UiStep

    step = await step_model.filter(quote_case__in=form.id_list).first().values("case_id")
    if step and step["case_id"]:
        step_case = await case_model.filter(id=step["case_id"]).first().values("name")
        raise ValueError(f'用例【{step_case["name"]}】已引用此用例，请先解除引用')

    await step_model.filter(case_id__in=form.id_list).delete()
    await case_model.filter(id__in=form.id_list).delete()
    return request.app.delete_success()


async def run_case(request: Request, form: schema.RunCaseForm, background_tasks: BackgroundTasks):
    case_runner, project_model, project_env_model, suite_model, case_model, step_model, report_model = RunApiCase, ApiProject, ApiProjectEnv, ApiCaseSuite, ApiCase, ApiStep, ApiReport
    if request.app.test_type == "app":
        case_runner, project_model, project_env_model, suite_model, case_model, step_model, report_model = RunUiCase, AppProject, AppProjectEnv, AppCaseSuite, AppCase, AppStep, AppReport
    elif request.app.test_type == "ui":
        case_runner, project_model, project_env_model, suite_model, case_model, step_model, report_model = RunUiCase, UiProject, UiProjectEnv, UiCaseSuite, UiCase, UiStep, UiReport

    case_id_list = [data["id"] for data in await case_model.filter(id__in=form.id_list).all().values("id")]
    if not case_id_list or len(case_id_list) == 0:
        raise ValueError(f'用例不存在')

    await form.validate_request(project_model, project_env_model, suite_model, case_model)
    first_case = await case_model.filter(id=case_id_list[0]).first().values("suite_id", "name")
    suite = await suite_model.filter(id=first_case["suite_id"]).first().values("project_id")
    user_id = await User.get_run_user_id(request)
    batch_id = report_model.get_batch_id(user_id)

    # 如果是app自动化测试，需要获取设备数据
    appium_config = {}
    if request.app.test_type == "app":
        server = await AppRunServer.validate_is_exist("服务器不存在", id=form.server_id)  # 校验服务id存在
        await form.validate_appium_server_is_running(server.ip, server.port)  # 校验appium是否能访问
        phone = await AppRunPhone.validate_is_exist("运行设备不存在", id=form.phone_id)  # 校验手机id存在
        project = await project_model.filter(id=suite["project_id"]).first().values("app_package", "app_activity")
        appium_command_timeout = await Config.get_appium_new_command_timeout() or 120
        appium_config = await server.get_appium_config(
            project["app_package"], project["app_activity"], phone, form.no_reset, appium_command_timeout)

    for env_code in form.env_list:
        env = await RunEnv.filter(code=env_code).first().values("name")
        # 运行用例
        summary = report_model.get_summary_template()
        summary["env"]["code"], summary["env"]["name"] = env_code, env["name"]
        report = await report_model.get_new_report(
            project_id=suite["project_id"], batch_id=batch_id, trigger_id=case_id_list, name=first_case["name"],
            run_type="case", env=env_code, trigger_type="page", temp_variables=form.temp_variables,
            summary=summary, create_user=user_id, update_user=user_id
        )
        # 后台任务运行测试
        background_tasks.add_task(case_runner(
            report_id=report.id, case_id_list=case_id_list, is_async=form.is_async, env_code=env_code, env_name=env["name"],
            browser=form.browser, temp_variables=form.temp_variables, run_type=request.app.test_type,
            appium_config=appium_config, insert_to=form.insert_to
        ).parse_and_run)

    return request.app.trigger_success({
        "batch_id": batch_id,
        "report_id": report.id if len(form.env_list) == 1 else None
    })
