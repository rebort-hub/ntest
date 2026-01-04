from fastapi import Request, Depends

from ...schemas.autotest import project as schema
from ...models.assist.model_factory import Script
from ...models.autotest.model_factory import ApiProject, ApiProjectEnv, ApiModule, ApiCaseSuite, ApiTask
from ...models.autotest.model_factory import AppProject, AppProjectEnv, AppModule, AppCaseSuite, AppTask
from ...models.autotest.model_factory import UiProject, UiProjectEnv, UiModule, UiCaseSuite, UiTask
from ...models.system.user import User
from ...models.config.model_factory import RunEnv


async def get_project_list(request: Request, form: schema.FindProjectListForm = Depends()):
    project_model = ApiProject if request.app.test_type == "api" else AppProject if request.app.test_type == "app" else UiProject
    get_filed = ["id", "name", "business_id"]
    if form.detail:
        get_filed.extend(["manager", "update_user"])
        if request.app.test_type == "api":
            get_filed.extend(["swagger", "last_pull_status"])
        elif request.app.test_type == "app":
            get_filed.extend(["app_package"])

    query_data = await form.make_pagination(project_model, user=request.state.user, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def project_sort(request: Request, form: schema.ChangeSortForm):
    project_model = ApiProject if request.app.test_type == "api" else AppProject if request.app.test_type == "app" else UiProject
    await project_model.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def get_project_detail(request: Request, form: schema.GetProjectForm = Depends()):
    project_model = ApiProject if request.app.test_type == "api" else AppProject if request.app.test_type == "app" else UiProject
    project = await project_model.filter(id=form.id).first()
    return request.app.get_success(project)


async def add_project(request: Request, form: schema.AddProjectForm):
    await form.validate_request()
    project_model, project_env_model, case_suite_model = ApiProject, ApiProjectEnv, ApiCaseSuite
    match request.app.test_type:
        case "app":
            project_model, project_env_model, case_suite_model = AppProject, AppProjectEnv, AppCaseSuite
        case "ui":
            project_model, project_env_model, case_suite_model = UiProject, UiProjectEnv, UiCaseSuite

    project = await project_model.model_create(form.dict(), request.state.user)
    # 新增服务的时候，一并把运行环境、用例集设置齐全
    await project_env_model.create_env(RunEnv, project_model, project.id)
    await case_suite_model.create_suite_by_project(project.id)

    return request.app.post_success(data=project)


async def change_project(request: Request, form: schema.EditProjectForm):
    project_model = ApiProject if request.app.test_type == "api" else AppProject if request.app.test_type == "app" else UiProject
    data = form.get_update_data(request.state.user.id)
    if request.app.test_type != "app":
        data.pop("app_package")
        data.pop("app_activity")
        data.pop("template_device")
    if request.app.test_type != "api":
            data.pop("swagger")
    await project_model.filter(id=form.id).update(**data)
    return request.app.put_success()


async def delete_project(request: Request, form: schema.GetProjectForm):
    """ 删除服务 / app / 项目 """
    project_model, module_model, case_suite_model, task_model = ApiProject, ApiModule, ApiCaseSuite, ApiTask
    match request.app.test_type:
        case "app":
            project_model, module_model, case_suite_model, task_model = AppProject, AppModule, AppCaseSuite, AppTask
        case "ui":
            project_model, module_model, case_suite_model, task_model = UiProject, UiModule, UiCaseSuite, UiTask
    project = await project_model.filter(id=form.id).first()

    # 删除权限判断，管理员、数据创建者、服务负责人
    if User.is_not_admin(request.state.user.api_permissions):
        if request.state.user.id not in [project.create_user, project.manager]:
            raise ValueError("当前用户无权限删除此服务")

    await task_model.filter(project_id=project.id).delete()  # 删除任务
    await case_suite_model.filter(project_id=project.id).delete()  # 删除用例集
    await module_model.filter(project_id=project.id).delete()  # 删除模块
    await project.model_delete()  # 删除服务
    return request.app.delete_success()


async def synchronization_project_env(request: Request, form: schema.SynchronizationEnvForm):
    env_model = ApiProjectEnv if request.app.test_type == "api" else AppProjectEnv if request.app.test_type == "app" else UiProjectEnv
    from_env = await env_model.validate_is_exist("环境不存在", project_id=form.project_id, env_id=form.env_from)
    filed_list = ["variables", "headers"] if request.app.test_type == "api" else ["variables"]
    await env_model.synchronization(dict(from_env), form.env_to, filed_list)
    return request.app.success("同步完成")


async def get_project_env(request: Request, form: schema.GetEnvForm = Depends()):
    env_model = ApiProjectEnv if request.app.test_type == "api" else AppProjectEnv if request.app.test_type == "app" else UiProjectEnv
    env_data = await env_model.filter(env_id=form.env_id, project_id=form.project_id).first()
    if not env_data:  # 如果没有就插入一条记录， 并且自动同步当前服务已有的环境数据
        env_data = await env_model.insert_env(form.project_id, form.env_id, request.state.user.id)
    return request.app.get_success(env_data)


async def change_project_env(request: Request, form: schema.EditEnvForm):
    env_model = ApiProjectEnv if request.app.test_type == "api" else AppProjectEnv if request.app.test_type == "app" else UiProjectEnv
    project_env = await env_model.validate_is_exist("环境不存在", id=form.id)

    project_model = ApiProject if request.app.test_type == "api" else AppProject if request.app.test_type == "app" else UiProject
    project = await project_model.filter(id=project_env.project_id).first().values("script_list")
    all_func_name = await Script.get_func_by_script_id(project["script_list"])
    await form.validate_request(all_func_name=all_func_name)

    update_data = form.dict()
    if request.app.test_type != "api":
        update_data.pop("headers")
    await project_env.model_update(update_data,  request.state.user)

    # 把环境的头部信息、变量的key一并同步到其他环境
    project_env_list = await env_model.filter(
        project_id=project_env.project_id, id__not=project_env.env_id).values("env_id")
    await env_model.synchronization(
        form.dict(),
        [env["env_id"] for env in project_env_list],
        ["variables", "headers"] if request.app.test_type == "api" else ["variables"])

    return request.app.put_success()
