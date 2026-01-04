from fastapi import Request, Depends, BackgroundTasks

from ...models.autotest.model_factory import ApiReport, ApiCase, ApiCaseSuite, ApiTask, AppReport, AppCase, \
    AppCaseSuite, AppTask, UiReport, UiCase, UiCaseSuite, UiTask, ApiStep, AppStep, UiStep, ApiProject, AppProject, \
    UiProject, AppRunServer, AppRunPhone
from ...models.config.config import Config
from ...models.config.run_env import RunEnv
from ...models.system.user import User
from ...schemas.autotest import task as schema
from utils.client.run_api_test import RunCase as RunApiCase
from utils.client.run_ui_test import RunCase as RunUiCase
from ...schemas.enums import DataStatusEnum


async def get_task_list(request: Request, form: schema.GetTaskListForm = Depends()):
    model = ApiTask if request.app.test_type == "api" else AppTask if request.app.test_type == "app" else UiTask
    get_filed = model.get_simple_filed_list()
    if form.detail:
        get_filed.extend([
            "cron", "skip_holiday", "status", "project_id", "merge_notify", "push_hit", "create_user", "receive_type",
            "is_send", "env_list"
        ])

    query_data = await form.make_pagination(model, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_task_sort(request: Request, form: schema.ChangeSortForm):
    model = ApiTask if request.app.test_type == "api" else AppTask if request.app.test_type == "app" else UiTask
    await model.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def copy_task(request: Request, form: schema.GetTaskForm):
    model = ApiTask if request.app.test_type == "api" else AppTask if request.app.test_type == "app" else UiTask
    task = await model.validate_is_exist("任务不存在", id=form.id)
    new_task = await task.copy(status=DataStatusEnum.DISABLE.value, user_id=request.state.user.id)
    return request.app.success("复制成功", data=new_task)


async def get_task_detail(request: Request, form: schema.GetTaskForm = Depends()):
    model = ApiTask if request.app.test_type == "api" else AppTask if request.app.test_type == "app" else UiTask
    task = await model.validate_is_exist("任务不存在", id=form.id)
    return request.app.get_success(data=task)


async def add_task(request: Request, form: schema.AddTaskForm):
    model = ApiTask if request.app.test_type == "api" else AppTask if request.app.test_type == "app" else UiTask
    await form.validate_request(request)
    await model.model_create(form.dict(), request.state.user)
    return request.app.post_success()


async def change_task(request: Request, form: schema.EditTaskForm):
    model = ApiTask if request.app.test_type == "api" else AppTask if request.app.test_type == "app" else UiTask
    update_result = await model.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    if update_result == 1:
        task = await model.filter(id=form.id).first()
        if task.is_enable():  # 如果任务是启动中，则把内存中的任务更新
            await task.disable_task(request.app.test_type, request.headers.get("access-token"))
            await task.enable_task(request.app.test_type, request.state.user.id, request.headers.get("access-token"))
    return request.app.put_success()


async def delete_task(request: Request, form: schema.GetTaskForm):
    model = ApiTask if request.app.test_type == "api" else AppTask if request.app.test_type == "app" else UiTask
    task = await model.validate_is_exist("任务不存在", id=form.id)
    if task.is_enable():  # 如果任务是启动中，则把内存中的任务删除
        await task.disable_task(request.app.test_type, request.headers.get("access-token"))
    await task.model_delete()
    return request.app.delete_success()


async def enable_task(request: Request, form: schema.GetTaskForm):
    model = ApiTask if request.app.test_type == "api" else AppTask if request.app.test_type == "app" else UiTask
    task = await model.validate_is_exist("任务不存在", id=form.id)
    await task.enable_task(request.app.test_type, request.state.user.id, request.headers.get("access-token"))
    return request.app.success("任务启用成功")


async def disable_task(request: Request, form: schema.GetTaskForm):
    model = ApiTask if request.app.test_type == "api" else AppTask if request.app.test_type == "app" else UiTask
    task = await model.validate_is_exist("任务不存在", id=form.id)
    await task.disable_task(request.app.test_type, request.headers.get("access-token"))
    return request.app.success("任务禁用成功")


async def run_task(request: Request, form: schema.RunTaskForm, background_tasks: BackgroundTasks):
    task_model, case_runner, project_model, suite_model, case_model, step_model, report_model = ApiTask, RunApiCase, ApiProject, ApiCaseSuite, ApiCase, ApiStep, ApiReport
    if request.app.test_type == "app":
        task_model, case_runner, project_model, suite_model, case_model, step_model, report_model = AppTask, RunUiCase, AppProject, AppCaseSuite, AppCase, AppStep, AppReport
    elif request.app.test_type == "ui":
        task_model, case_runner, project_model, suite_model, case_model, step_model, report_model = UiTask, RunUiCase, UiProject, UiCaseSuite, UiCase, UiStep, UiReport

    task = await task_model.validate_is_exist("任务不存在", id=form.id_list[0])
    case_id_list = await suite_model.get_case_id(case_model, task.project_id, task.suite_ids, task.case_ids)
    user_id = await User.get_run_user_id(request)
    batch_id = report_model.get_batch_id(user_id)
    env_list = form.env_list or task.env_list

    # 如果是app自动化测试，需要获取设备数据
    appium_config = {}
    if request.app.test_type == "app":
        server_id = form.server_id or task.conf["server_id"]
        phone_id = form.phone_id or task.conf["phone_id"]
        no_reset = form.no_reset or task.conf["no_reset"]
        server = await AppRunServer.validate_is_exist("服务器不存在", id=server_id)  # 校验服务id存在
        await form.validate_appium_server_is_running(server.ip, server.port)  # 校验appium是否能访问
        phone = await AppRunPhone.validate_is_exist("运行设备不存在", id=phone_id)  # 校验手机id存在
        project = await project_model.filter(id=task.project_id).first().values("app_package", "app_activity")
        appium_command_timeout = await Config.get_appium_new_command_timeout() or 120
        appium_config = await server.get_appium_config(
            project["app_package"], project["app_activity"], phone, no_reset, appium_command_timeout)

    for env_code in env_list:
        env = await RunEnv.filter(code=env_code).first().values("name")

        # 运行用例
        summary = report_model.get_summary_template()
        summary["env"]["code"], summary["env"]["name"] = env_code, env["name"]
        report = await report_model.get_new_report(
            project_id=task.project_id, batch_id=batch_id, trigger_id=[task.id], name=task.name,
            run_type="task", env=env_code, trigger_type=form.trigger_type.value, temp_variables=form.temp_variables,
            summary=summary, create_user=user_id, update_user=user_id
        )

        # 后台任务运行测试
        background_tasks.add_task(case_runner(
            report_id=report.id, case_id_list=case_id_list, is_async=form.is_async, env_code=env_code, env_name=env["name"],
            browser=form.browser or task.conf["browser"], task_dict=dict(task), temp_variables=form.temp_variables, run_type=request.app.test_type,
            extend={}, appium_config=appium_config
        ).parse_and_run)

    return request.app.trigger_success({
        "batch_id": batch_id,
        "report_id": report.id if len(env_list) == 1 else None
    })
