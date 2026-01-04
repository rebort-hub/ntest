from fastapi import Request, Depends

from ...models.autotest.model_factory import ApiReport as Report, ApiProject as Project
from app.models.config.model_factory import BusinessLine
from utils.util.time_util import time_calculate, get_now
from ...schemas.autotest import stat as schema


async def get_use_stat(time_slot, project_list: list = [], get_card=False):
    """ 获取时间段的统计 """
    page_trigger_count, page_trigger_pass_count, page_trigger_pass_rate = 0, 0, 0  # 页面触发使用次数维度
    patrol_count, patrol_pass_count, patrol_pass_rate = 0, 0, 0  # 巡检维度

    start_time, end_time = time_calculate(time_slot), get_now()
    time_filter = {"create_time__range": [start_time, end_time]}

    if get_card:
        # 人工使用（页面触发）统计
        page_trigger_count = await Report.filter(**time_filter, trigger_type='page').count()
        if page_trigger_count > 0:
            page_trigger_pass_count = await Report.filter(**time_filter, trigger_type='page', is_passed=1).count()
            page_trigger_pass_rate = round(page_trigger_pass_count / page_trigger_count, 4)

        # cron巡检统计
        patrol_count = await Report.filter(**time_filter, trigger_type='cron').count()
        if patrol_count > 0:
            patrol_pass_count = await Report.filter(**time_filter, trigger_type='cron', is_passed=1).count()
            patrol_pass_rate = round(patrol_pass_count / patrol_count, 4)
    else:
        if project_list:
            # 人工使用（页面触发）统计
            page_trigger_count = await Report.filter(**time_filter, project_id__in=project_list, trigger_type='page').count()
            if page_trigger_count > 0:
                page_trigger_pass_count = await Report.filter(**time_filter, project_id__in=project_list, trigger_type='page', is_passed=1).count()
                page_trigger_pass_rate = round(page_trigger_pass_count / page_trigger_count, 4)

            # cron巡检统计
            patrol_count = await Report.filter(**time_filter, project_id__in=project_list, trigger_type='page').count()
            if patrol_count > 0:
                patrol_pass_count = await Report.filter(**time_filter, project_id__in=project_list, trigger_type='cron', is_passed=1).count()
                patrol_pass_rate = round(patrol_pass_count / patrol_count, 4)
    return {
        "page_trigger_count": page_trigger_count,
        "page_trigger_pass_count": page_trigger_pass_count,
        "page_trigger_pass_rate": page_trigger_pass_rate,
        "patrol_count": patrol_count,
        "patrol_pass_count": patrol_pass_count,
        "patrol_pass_rate": patrol_pass_rate
    }



async def get_use_card(request: Request, form: schema.UseCountForm = Depends()):
    use_stat = await get_use_stat(form.time_slot, get_card=True)
    return request.app.get_success(data=use_stat)


async def get_use_chart(request: Request, form: schema.UseCountForm = Depends()):
    options_list = []
    page_trigger_count_list, page_trigger_pass_count_list, page_trigger_pass_rate_list = [], [], []  # 页面使用维度
    patrol_count_list, patrol_pass_count_list, patrol_pass_rate_list = [], [], []  # 巡检维度

    business_list = await BusinessLine.filter().values("id", "name")  # [{"id", 1, "name": "公共业务线"}]
    for business_line in business_list:
        options_list.append(business_line["name"])
        project_id_list = await Project.filter(business_id=business_line["id"]).values("id")  # [{"id", 1}]
        business_stat = await get_use_stat(form.time_slot, [data["id"] for data in project_id_list])

        page_trigger_count_list.append(business_stat.get("page_trigger_count", 0))
        page_trigger_pass_count_list.append(business_stat.get("page_trigger_pass_count", 0))
        page_trigger_pass_rate_list.append(business_stat.get("page_trigger_pass_rate", 0))
        patrol_count_list.append(business_stat.get("patrol_count", 0))
        patrol_pass_count_list.append(business_stat.get("patrol_pass_count", 0))
        patrol_pass_rate_list.append(business_stat.get("patrol_pass_rate", 0))

    return request.app.get_success({
        "options_list": options_list,
        "items": [
            {"name": "人工触发次数", "type": "bar", "data": page_trigger_count_list},
            {"name": "人工通过次数", "type": "bar", "data": page_trigger_pass_count_list},
            {"name": "巡检次数", "type": "bar", "data": patrol_count_list},
            {"name": "巡检通过次数", "type": "bar", "data": patrol_pass_count_list}
        ]
    })


async def get_report_chart(request: Request, form: schema.AnalyseForm = Depends()):
    project_list = await Project.filter(business_id=form.business_id).values("id")  # [{"id": 1}]
    filter_dict = {"project_id__in": [data["id"] for data in project_list]}
    if form.trigger_type:
        filter_dict["trigger_type"] = form.trigger_type.value
    if form.start_time:
        filter_dict["create_time__range"] = [form.start_time, form.end_time]

    # 执行次数维度统计
    all_count = await Report.filter(**filter_dict).count()
    pass_count = await Report.filter(**filter_dict, is_passed=1).count()
    fail_count = all_count - pass_count

    # 创建人执行次数统计
    user_count_sql = f"""
        SELECT user.name AS name, count(user.id) AS value
        FROM system_user user,
             api_test_report report,
             api_test_project project
        WHERE report.project_id = project.id
          AND project.business_id = {form.business_id}
          AND user.id = report.create_user
    """
    if form.trigger_type:
        user_count_sql += f"""AND report.trigger_type = '{form.trigger_type.value}' \n"""
    if form.start_time:
        user_count_sql += f"""AND report.create_time between '{form.start_time}' and '{form.end_time}' \n"""
    user_count_sql += """GROUP BY report.create_user"""
    request.app.logger.info(f'api.report.stat.analyse.user_count_sql: {user_count_sql}')
    user_count_list = await Report.execute_sql(user_count_sql)

    return request.app.get_success({
        "use_count": {
            "stat": {
                "title": "执行次数统计",
                "stat_list": [
                    {"name": "通过数量", "value": pass_count},
                    {"name": "不通过数量", "value": fail_count},
                ]
            },
            "detail": {"all_count": all_count, "pass_count": pass_count, "fail_count": fail_count}
        },
        "create": {
            "stat": {
                "title": "执行人员统计",
                "stat_list": user_count_list
            }
        }
    })
