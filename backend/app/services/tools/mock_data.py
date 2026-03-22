import time
import importlib
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse

from ...models.assist.model_factory import Script
from utils.util.file_util import FileUtil


async def run_script(script_name, request):
    if script := await Script.filter(name=script_name).first() is None:
        return request.app.fail('mock脚本文件不存在')

    try:
        script_file_name = f"mock_{script.name}"
        import_path = f'script_list.{script_file_name}'
        FileUtil.save_mock_script_data(
            script_file_name,
            script.script_data,
            path=request.url.path,
            headers=dict(request.headers),
            query=request.query_params,
            body=request.json or request.form
        )
        script_obj = importlib.reload(importlib.import_module(import_path))
        return script_obj.result
    except Exception as e:
        error_data = "\n".join("{}".format(traceback.format_exc()).split("↵"))
        return request.app.fail(msg="脚本执行错误，请检查", result=error_data)


async def mock_data_by_script_get(script_name, request: Request):
    return await run_script(script_name, request)


async def mock_data_by_script_post(script_name, request: Request):
    return await run_script(script_name, request)


async def mock_data_by_script_put(script_name, request: Request):
    return await run_script(script_name, request)


async def mock_data_by_script_delete(script_name, request: Request):
    return await run_script(script_name, request)


def mock_api(data):
    """ mock_api， 收到什么就返回什么 """
    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),
        "status": 200,
        "message": "请求成功",
        "data": data
    }


async def mock_data_by_request_get(request: Request):
    return JSONResponse(mock_api(dict(request.query_params)))


async def mock_data_by_request_post(request: Request):
    return JSONResponse(mock_api(await request.json()))


async def mock_data_by_request_put(request: Request):
    return JSONResponse(mock_api(await request.json()))


async def mock_data_by_request_delete(request: Request):
    return JSONResponse(mock_api(await request.json()))
