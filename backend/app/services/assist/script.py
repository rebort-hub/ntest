import importlib
import sys
import types
import traceback

from fastapi import Request, Depends

from ...models.config.config import Config
from ...models.assist.model_factory import Script
from ...models.autotest.model_factory import ApiProject, AppProject, UiProject
from utils.util.file_util import FileUtil
from utils.logs.redirect_print_log import RedirectPrintLogToMemory
from utils.client.test_runner.parser import parse_function, extract_functions
from ...schemas.assist import script as schema


async def get_script_list(request: Request, form: schema.FindScriptForm = Depends()):
    get_filed = Script.get_simple_filed_list()
    if form.detail:
        get_filed.extend(["script_type", "desc",  "create_user",  "update_user"])
    query_data = await form.make_pagination(Script, get_filed=get_filed)
    return request.app.get_success(data=query_data)


async def change_script_sort(request: Request, form: schema.ChangeSortForm):
    await Script.change_sort(**form.dict(exclude_unset=True))
    return request.app.put_success()


async def copy_script(request: Request, form: schema.GetScriptForm):
    script = await Script.validate_is_exist("数据不存在", id=form.id)
    script = await script.copy()
    return request.app.success("复制成功", data=script)


async def debug_script(request: Request, form: schema.DebugScriptForm):
    script = await Script.validate_is_exist("数据不存在", id=form.id)
    name, expression = f'{form.env}_{script.name}', form.expression
    await Script.create_script_file(form.env)  # 把自定义函数脚本内容写入到python脚本中

    # 动态导入脚本
    try:
        import_path = f'script_list.{name}'
        func_list = importlib.reload(importlib.import_module(import_path))
        module_functions_dict = {
            name: item for name, item in vars(func_list).items() if isinstance(item, types.FunctionType)
        }
        ext_func = extract_functions(expression)
        func_info = parse_function(ext_func[0])
        func_name, args, kwargs = func_info["func_name"], func_info["args"], func_info["kwargs"]

        # 重定向print内容到内存
        redirect = RedirectPrintLogToMemory()
        result = await Script.run_func(module_functions_dict[func_name], args, kwargs)
        script_print = redirect.get_text_and_redirect_to_default()

        return request.app.success(msg="执行成功，请查看执行结果", result={
            "env": form.env,
            "expression": form.expression,
            "result": result,
            "script_print": script_print,
            "script": FileUtil.get_func_data_by_script_name(f'{form.env}_{script.name}')
        })
    except Exception as e:
        sys.stdout = sys.__stdout__  # 恢复输出到console
        error_data = "\n".join("{}".format(traceback.format_exc()).split("↵"))
        request.app.logger.error(error_data)
        return request.app.fail(msg="语法错误，请检查", result={
            "env": form.env,
            "expression": form.expression,
            "result": error_data,
            "script": FileUtil.get_func_data_by_script_name(f'{form.env}_{script.name}')
        })


async def get_script(request: Request, form: schema.GetScriptForm = Depends()):
    script = await Script.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data=script)


async def add_script(request: Request, form: schema.CreatScriptForm):
    save_func_permissions = await Config.get_save_func_permissions()
    await form.validate_request(request.state.user, save_func_permissions)
    script = await Script.model_create(form.dict(), request.state.user)
    return request.app.post_success({"id": script.id})


async def change_script(request: Request, form: schema.EditScriptForm):
    save_func_permissions = await Config.get_save_func_permissions()
    await form.validate_request(request.state.user, save_func_permissions)
    await Script.filter(id=form.id).update(**form.get_update_data(request.state.user.id))
    return request.app.put_success()


async def delete_script(request: Request, form: schema.DeleteScriptForm):
    """
    1.校验自定义脚本文件需存在
    2.校验是否有引用
    3.校验当前用户是否为管理员或者创建者
    """
    script = await Script.validate_is_exist("数据不存在", id=form.id)

    # 用户是管理员或者创建者
    form.validate_is_true(
        "脚本文件仅【管理员】或【创建者】可删除",
        form.is_admin(request.state.user.api_permissions) or script.is_create_user(request.state.user.id))

    # 校验是否被引用
    for model in [ApiProject, AppProject, UiProject]:
        project = await model.filter(script_list__contains=form.id).first().values("name")
        if project and project["name"]:
            class_name = model.__name__
            name = '服务' if 'Api' in class_name else '项目' if 'Ui' in class_name else 'APP'
            raise ValueError(f'{name}【{project["name"]}】已引用此脚本文件，请先解除依赖再删除')

    await script.model_delete()
    return request.app.delete_success()
