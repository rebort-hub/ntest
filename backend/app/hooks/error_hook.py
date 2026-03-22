import platform
import re
import traceback

from pydantic import ValidationError
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from tortoise import exceptions as tortoise_exceptions

from app.models.system.model_factory import SystemErrorRecord
from utils.logs.log import logger
from utils.message.send_report import send_system_error


def register_exception_handler(app):
    @app.exception_handler(tortoise_exceptions.IntegrityError)
    async def db_unique_error(request, exc):
        """ 统一拦截数据库唯一约束错误并解析 """
        # ((1062, "Duplicate entry '测试平台' for key 'api_test_project.uid_api_test_pr_name_293ace'"),)
        filed_value = re.findall("'(.+?)'", str(exc))[0]
        return request.app.fail(f'【{filed_value}】已存在')

    @app.exception_handler(tortoise_exceptions.ValidationError)
    async def db_validation_error(request, exc):
        """ 统一拦截数据库验证错误并解析 """
        # name: Length of '测试平台测试平台测试平台平台' 1404 > 255
        str_msg = str(exc)
        # filed_name = re.findall("^(.+?):", str_msg)[0]  # name
        filed_value = re.findall("'(.+?)'", str_msg)[0]  # 测试平台测试平台测试平台平台
        if 'Length' in str_msg:
            if '>' in str_msg:
                length = re.findall(">(.+?)$", str_msg)[0]
                return request.app.fail(f'【{filed_value}】长度超长，最长【{length}】位')

    # TODO 其他数据库字段约束错误，减少数据验证的查询次数

    @app.exception_handler(RequestValidationError)
    async def filed_type_error(request, exc):
        """ pydantic数据类型、必传字段 校验不通过
        [
            # 数据类型错误
            {'loc': ('report_id',), 'msg': 'value is not a valid integer', 'type': 'type_error.integer'},
            # 必传数据
            {'loc': ('from_id',), 'msg': 'field required', 'type': 'value_error.missing'},
            # 主动抛的ValueError
            {'loc': ('report_id',), 'msg': '数据不存在', 'type': 'value_error'}
            # 数据类型错误
            {'loc': ('body', 'permission_id'), 'msg': 'value is not a valid integer', 'type': 'type_error.integer'}
            # 长度错误
            {'ctx': {'limit_value': 4}, 'loc': ('body', 'permission_id'), 'msg': 'ensure this value has at most 4 characters', 'type': 'value_error.any_str.max_length'}
            {'ctx': {'limit_value': 2}, 'loc': ('body', 'permission_id'), 'msg': 'ensure this value has at least 2 characters', 'type': 'value_error.any_str.min_length'}
        ]
        """
        error = exc.errors()[0]
        app.logger.error(error)
        return request.app.fail(get_error_msg(error))

    @app.exception_handler(ValidationError)
    async def filed_validate_error(request, exc):
        """ pydantic数据类型、必传字段 校验不通过 """
        """
        [
            # 数据类型错误
            {'loc': ('report_id',), 'msg': 'value is not a valid integer', 'type': 'type_error.integer'}, 
            # 必传数据
            {'loc': ('from_id',), 'msg': 'field required', 'type': 'value_error.missing'},
            # 主动抛的ValueError
            {'loc': ('report_id',), 'msg': '数据不存在', 'type': 'value_error'}
            # 数据类型错误
            {'loc': ('body', 'permission_id'), 'msg': 'value is not a valid integer', 'type': 'type_error.integer'}
            # 长度错误
            {'ctx': {'limit_value': 4}, 'loc': ('body', 'permission_id'), 'msg': 'ensure this value has at most 4 characters', 'type': 'value_error.any_str.max_length'}
            {'ctx': {'limit_value': 2}, 'loc': ('body', 'permission_id'), 'msg': 'ensure this value has at least 2 characters', 'type': 'value_error.any_str.min_length'}
        ]
        """
        return request.app.fail(exc)

    @app.exception_handler(Exception)
    async def unexpected_exception(request: Request, exc: Exception):
        """ 未预期的所有异常捕获、pydantic数据值校验不通过 """
        if isinstance(exc, ValueError): return request.app.fail(str(exc))  # 数据值校验不通过

        error = traceback.format_exc()
        try:
            request.app.logger.error(f'系统报错了:  \n\n url: {request.url} \n\n 错误详情: \n\n {error}')

            # 写数据库
            error_record = await SystemErrorRecord.create(
                url=request.url,
                method=request.method,
                headers=dict(request.headers),
                params=dict(request.query_params) or {},
                data_form={},
                data_json=request.state.set_body if request.state.is_upload_file else {},
                detail=error
            )

            # 发送即时通讯通知
            if platform.platform().startswith('Linux'):
                await send_system_error(
                    title=f'{request.app.conf.token_secret_key}报错通知，数据id：{error_record.id}', content=error)
        except Exception as error:
            request.app.logger.error(traceback.format_exc())


def get_error_msg(error):
    # error_msg = exc.errors()
    filed_name = error["loc"][-1]
    error_type, msg = error["type"], error["msg"]

    if "type_error" in error_type:  # 数据类型错误
        return f'{filed_name} 数据类型错误'

    elif "max_length" in error_type:  # 数据长度超长
        return f'{filed_name} 长度超长，最多{error["ctx"]["limit_value"]}位'

    elif "min_length" in error_type:  # 数据长度超长
        return f'{filed_name} 长度不够，最少{error["ctx"]["limit_value"]}位'

    elif "required" in msg:  # 必传字段
        return f'{filed_name} 必传'

    return msg  # 数据值验证不通过
