from fastapi import Request
from tortoise import functions, expressions


from app.models.autotest.model_factory import ApiProject as Project, ApiModule as Module, ApiMsg as Api, \
    ApiCase as Case, ApiStep as Step, ApiTask as Task, ApiReport as Report
from utils.util.time_util import get_now, time_calculate, get_week_start_and_end
from app.schemas.enums import DataStatusEnum, CaseStatusEnum


async def get_data_by_time(model):
    """ 获取时间维度的统计 """
    last_start_time, last_end_time = get_week_start_and_end(1)
    current_start_time, current_end_time = get_week_start_and_end(0)
    return await model.annotate(
        last_day_add=functions.Count('id', _filter=expressions.Q(create_time__range=[time_calculate(-1), time_calculate(0)])),
        to_day_add=functions.Count('id', _filter=expressions.Q(create_time__range=[time_calculate(0), get_now()])),
        last_week_add=functions.Count('id', _filter=expressions.Q(create_time__range=[last_start_time, last_end_time])),
        current_week_add=functions.Count('id', _filter=expressions.Q(create_time__range=[current_start_time, current_end_time])),
        last_month_add=functions.Count('id', _filter=expressions.Q(create_time__range=[time_calculate(-30), get_now()]))
    ).first().values('last_day_add', 'to_day_add', 'last_week_add', 'current_week_add', 'last_month_add')


async def get_api_test_title(request: Request):
    return request.app.get_success([
        {"name": "report", "title": "测试报告数", "total": await Report.filter().all().count()},
        {"name": "api", "title": "接口数", "total": await Api.filter().all().count()},
        {"name": "case", "title": "用例数", "total": await Case.filter().all().count()},
        {"name": "step", "title": "测试步骤数", "total": await Step.filter().all().count()}
    ])


async def get_api_test_project(request: Request):
    time_data = await get_data_by_time(Project)
    return request.app.success(data={
        "title": "服务",
        "options": ["总数", "昨日新增", "今日新增", "本周新增", "上周新增", "30日内新增"],
        "data": [
            await Project.filter().all().count(),
            time_data["last_day_add"],
            time_data["to_day_add"],
            time_data["current_week_add"],
            time_data["last_week_add"],
            time_data["last_month_add"]
        ],
    })


async def get_api_test_module(request: Request):
    time_data = await get_data_by_time(Module)
    return request.app.success(data={
        "title": "模块",
        "options": ["总数", "昨日新增", "今日新增", "本周新增", "上周新增", "30日内新增"],
        "data": [
            await Module.filter().all().count(),
            time_data["last_day_add"],
            time_data["to_day_add"],
            time_data["current_week_add"],
            time_data["last_week_add"],
            time_data["last_month_add"]],
    })


async def get_api_test_api(request: Request):
    res = await Api.annotate(
        all=functions.Count('id'),
        get_method_count=functions.Count('id', _filter=expressions.Q(method="GET")),
        post_method_count=functions.Count('id', _filter=expressions.Q(method="POST")),
        put_method_count=functions.Count('id', _filter=expressions.Q(method="PUT")),
        delete_method_count=functions.Count('id', _filter=expressions.Q(method="DELETE")),
        other_method_count=functions.Count('id', _filter=expressions.Q(method__not_in=["GET", "POST", "PUT", "DELETE"])),
        is_used_count=functions.Count('id', _filter=expressions.Q(use_count__not=0)),
        not_used_count=functions.Count('id', _filter=expressions.Q(use_count=0))
    ).first().values(
        'all',
        'get_method_count',
        'post_method_count',
        'put_method_count',
        'delete_method_count',
        'other_method_count',
        'is_used_count',
        'not_used_count'
    )
    time_data = await get_data_by_time(Api)
    return request.app.success(data={
        "title": "接口",
        "options": [
            "总数",
            "GET请求", "POST请求", "PUT请求", "DELETE请求", "其他请求",
            "已使用数", "未使用数",
            "昨日新增", "今日新增", "本周新增", "上周新增", "30日内新增"
        ],
        "data": [
            *res.values(),
            time_data["last_day_add"],
            time_data["to_day_add"],
            time_data["current_week_add"],
            time_data["last_week_add"],
            time_data["last_month_add"]
        ]
    })


async def get_api_test_case(request: Request):
    res = await Case.annotate(
        all=functions.Count('id'),
        is_run_count=functions.Count('id', _filter=expressions.Q(status=CaseStatusEnum.DEBUG_PASS_AND_RUN.value)),
        not_run_count=functions.Count('id', _filter=expressions.Q(status__not=CaseStatusEnum.DEBUG_PASS_AND_RUN.value))
    ).first().values('all', 'is_run_count', 'not_run_count')
    time_data = await get_data_by_time(Case)
    return request.app.success("获取成功", data={
        "title": "用例",
        "options": [
            "总数", "要执行的用例", "不执行的用例",
            "昨日新增", "今日新增", "本周新增", "上周新增", "30日内新增"
        ],
        "data": [
            *res.values(),
            time_data["last_day_add"],
            time_data["to_day_add"],
            time_data["current_week_add"],
            time_data["last_week_add"],
            time_data["last_month_add"]
        ],
    })


async def get_api_test_step(request: Request):
    res = await Step.annotate(
        all=functions.Count('id'),
        is_run_count=functions.Count('id', _filter=expressions.Q(status=DataStatusEnum.ENABLE.value)),
        not_run_count=functions.Count('id', _filter=expressions.Q(status=DataStatusEnum.DISABLE.value))
    ).first().values('all', 'is_run_count', 'not_run_count')
    time_data = await get_data_by_time(Step)
    return request.app.success("获取成功", data={
        "title": "测试步骤",
        "options": [
            "总数", "要执行的步骤", "不执行的步骤",
            "昨日新增", "今日新增", "本周新增", "上周新增", "30日内新增"
        ],
        "data": [
            *res.values(),
            time_data["last_day_add"],
            time_data["to_day_add"],
            time_data["current_week_add"],
            time_data["last_week_add"],
            time_data["last_month_add"]
        ],
    })


async def get_api_test_task(request: Request):
    res = await Task.annotate(
        all=functions.Count('id'),
        enable_task_count=functions.Count('id', _filter=expressions.Q(status=DataStatusEnum.ENABLE.value)),
        disable_task_count=functions.Count('id', _filter=expressions.Q(status=DataStatusEnum.DISABLE.value))
    ).first().values('all', 'enable_task_count', 'disable_task_count')
    time_data = await get_data_by_time(Task)
    return request.app.success("获取成功", data={
        "title": "定时任务",
        "options": [
            "总数", "启用", "禁用",
            "昨日新增", "今日新增", "本周新增", "上周新增", "30日内新增"
        ],
        "data": [
            *res.values(),
            time_data["last_day_add"],
            time_data["to_day_add"],
            time_data["current_week_add"],
            time_data["last_week_add"],
            time_data["last_month_add"]
        ]
    })


async def get_api_test_report(request: Request):
    res = await Report.annotate(
        all=functions.Count('id'),
        is_passed_count=functions.Count('id', _filter=expressions.Q(is_passed=1)),
        not_passed_count=functions.Count('id', _filter=expressions.Q(is_passed__not=1)),
        api_report_count=functions.Count('id', _filter=expressions.Q(run_type="api")),
        case_report_count=functions.Count('id', _filter=expressions.Q(run_type="case")),
        suite_report_count=functions.Count('id', _filter=expressions.Q(run_type="set")),
        task_report_count=functions.Count('id', _filter=expressions.Q(run_type="task"))
    ).first().values(
        'all',
        'is_passed_count',
        'not_passed_count',
        'api_report_count',
        'case_report_count',
        'suite_report_count',
        'task_report_count'
    )
    time_data = await get_data_by_time(Report)
    return request.app.success("获取成功", data={
        "title": "测试报告",
        "options": [
            "总数", "通过数", "失败数",
            "接口生成", "用例生成", "用例集生成", "定时任务生成",
            "昨日新增", "今日新增", "本周新增", "上周新增", "30日内新增"
        ],
        "data": [
            *res.values(),
            time_data["last_day_add"],
            time_data["to_day_add"],
            time_data["current_week_add"],
            time_data["last_week_add"],
            time_data["last_month_add"]
        ]
    })
