# -*- coding: utf-8 -*-

from datetime import datetime


def inspection_ding_ding(content_list, task_kwargs):
    """ 巡检-钉钉报告模板，官方文档 https://open.dingtalk.com/document/orgapp/custom-robot-access """
    notify_template = {
        "msgtype": "markdown",
        "markdown": {
            "title": "巡检通知",
            "text": f'### 巡检通知 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} \n> '
                    f'### 任务名: {task_kwargs["name"]} \n\n\n'
        }
    }
    for content_data in content_list:
        report_id, content = content_data["report_id"], content_data["report_summary"]
        case_stat, step_stat = content["stat"]["test_case"], content["stat"]["test_step"]
        pass_rate = round(case_stat["success"] / case_stat["total"] * 100, 3) if case_stat["total"] else 100
        notify_template["markdown"]["text"] += (
            f'#### 运行环境:<font color=#409EFF> {content["env"]["name"]} </font>\n> '
            f'#### 开始时间:<font color=#409EFF> {content["time"]["start_at"]} </font>\n> '
            f'#### 结束时间:<font color=#409EFF> {content["time"]["end_at"]} </font>\n> '
            f'#### 执行:<font color=#409EFF> {case_stat["total"]} </font>条用例 \n> '
            f'#### 通过:<font color=#00FF00> {case_stat["success"]} </font>条用例 \n> '
            f'#### 失败:<font color=#FF0000> {case_stat["fail"] + case_stat["error"]} </font>条用例 \n> '
            f'#### 通过率:<font color=#409EFF> {pass_rate}% </font> \n> '
            f'#### 此次共运行<font color=#19D4AE> {step_stat["total"]} </font>个步骤，'
            f'涉及<font color=#19D4AE> {content["stat"]["count"]["api"]} </font>个接口 \n> '
            )
        if content_data["report_summary"]["stat"]["response_time"]["slow"] or content_data["report_summary"]["stat"]["response_time"]["very_slow"]:
            notify_template["markdown"]["text"] += "#### 其中: "
            if content_data["report_summary"]["stat"]["response_time"]["slow"]:
                notify_template["markdown"]["text"] += (
                    f'<font color="#FF0000"> 有{len(content_data["report_summary"]["stat"]["response_time"]["slow"])}个接口响应时间超过{content_data["report_summary"]["stat"]["response_time"]["response_time_level"]["slow"]}毫秒 </font>, '
                )
            if content_data["report_summary"]["stat"]["response_time"]["very_slow"]:
                notify_template["markdown"]["text"] += (
                    f'<font color="#FF0000"> 有{len(content_data["report_summary"]["stat"]["response_time"]["very_slow"])}个接口响应时间超过{content_data["report_summary"]["stat"]["response_time"]["response_time_level"]["very_slow"]}毫秒 </font>, '
                )
            notify_template["markdown"]["text"] += """<font color="#FF0000">请确认是否需要优化</font>\n"""
        notify_template["markdown"]["text"] += f'#### 详情请【[点击此处]({task_kwargs["report_addr"] + str(report_id)})】查看\n\n\n'
    return notify_template


def inspection_we_chat(content_list, task_kwargs):
    """ 巡检-企业微信报告模板, 官方文档 https://developer.work.weixin.qq.com/document/path/91770 """
    notify_template = {
        "msgtype": "markdown",
        "markdown": {
            "content": f'>**巡检通知** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
                       f'>**任务名**: {task_kwargs["name"]} \n\n'
        }
    }
    for content_data in content_list:
        report_id, content = content_data["report_id"], content_data["report_summary"]
        case_stat, step_stat = content["stat"]["test_case"], content["stat"]["test_step"]
        pass_rate = round(case_stat["success"] / case_stat["total"] * 100, 3) if case_stat["total"] else 100
        notify_template["markdown"]["content"] += (
            f'>**运行环境**: {content["env"]["name"]} \n'
            f'>**开始时间**: {content["time"]["start_at"]} \n'
            f'>**结束时间**: {content["time"]["end_at"]} \n'
            f'>**执行**:<font color="comment"> {case_stat["total"]} </font>条用例\n'
            f'>**通过**:<font color="info"> {case_stat["success"]} </font>条用例\n'
            f'>**失败**:<font color="warning"> {case_stat["fail"] + case_stat["error"]} </font>条用例\n'
            f'>**通过率**:<font color="info"> {pass_rate}% </font>\n'
            f'>此次共运行<font color="info"> {step_stat["total"]} </font>个步骤，'
            f'涉及<font color="info"> {content["stat"]["count"]["api"]} </font>个接口 \n> '
        )
        if content_data["report_summary"]["stat"]["response_time"]["slow"] or content_data["report_summary"]["stat"]["response_time"]["very_slow"]:
            notify_template["markdown"]["content"] += "其中: "
            if content_data["report_summary"]["stat"]["response_time"]["slow"]:
                notify_template["markdown"]["content"] += (
                    f'<font color="warning"> 有{len(content_data["report_summary"]["stat"]["response_time"]["slow"])}个接口响应时间超过{content_data["report_summary"]["stat"]["response_time"]["response_time_level"]["slow"]}毫秒 </font>, '
                )
            if content_data["report_summary"]["stat"]["response_time"]["very_slow"]:
                notify_template["markdown"]["content"] += (
                    f'<font color="warning"> 有{len(content_data["report_summary"]["stat"]["response_time"]["very_slow"])}个接口响应时间超过{content_data["report_summary"]["stat"]["response_time"]["response_time_level"]["very_slow"]}毫秒 </font>, '
                )
            notify_template["markdown"]["content"] += """<font color="warning">请确认是否需要优化</font>\n"""
        notify_template["markdown"]["content"] += f'**详情请【[点击此处]({task_kwargs["report_addr"] + str(report_id)})】查看** \n\n\n'
    return notify_template


def render_html_report(content_list, task_kwargs):
    """ 巡检-邮件模板 """
    notify_template = f"""
    <div>
        <h2>巡检通知：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</h2>
        <h3>
            <span>
                任务名: 
                <span style="color: #60C0DDFF">
                    {task_kwargs["name"]}
                </span>
            </span>
        </h3>
        <br/>
    """
    all_res = []
    for content_data in content_list:
        report_id, content = content_data["report_id"], content_data["report_summary"]
        all_res.append(content["result"])
        case_stat, step_stat = content["stat"]["test_case"], content["stat"]["test_step"]
        pass_rate = round(case_stat["success"] / case_stat["total"] * 100, 3) if case_stat["total"] else 100
        notify_template += (
            f"""
            <div><span>运行环境: <span style="color: #60C0DDFF">{content["env"]["name"]}</span></span></div>
            <div><span>开始时间: <span style="color: #60C0DDFF">{content["time"]["start_at"]}</span></span></div>
            <div><span>结束时间: <span style="color: #60C0DDFF">{content["time"]["end_at"]}</span></span></div>
            <div><span>执行: <span style="color: #60C0DDFF">{case_stat["total"]}</span> 条用例</span></div>
            <div><span>通过: <span style="color: #9BCA63FF">{case_stat["success"]}</span> 条用例</span></div>
            <div><span>失败: <span style="color: #FA6E86FF">{case_stat["fail"] + case_stat["error"]}</span> 条用例</span></div>
            <div><span>通过率: <span style="color: #60C0DDFF">{pass_rate}</span>%</span></div>
            <div>
                <span>
                    此次共运行: 
                    <span style="color: #60C0DDFF"> 
                        {step_stat["total"]} 
                    </span>
                    个步骤, 涉及 
                    <span style="color: #60C0DDFF"> 
                        {content["stat"]["count"]["api"]} 
                    </span> 
                    个接口 
                </span>
            </div>
            """
        )
        if content_data["report_summary"]["stat"]["response_time"]["slow"] or content_data["report_summary"]["stat"]["response_time"]["very_slow"]:
            notify_template += "其中: "
            if content_data["report_summary"]["stat"]["response_time"]["slow"]:
                notify_template += (
                    f"""
                    <span style="color: #E4080A">
                        有{len(content_data["report_summary"]["stat"]["response_time"]["slow"])}个接口响应时间超过{content_data["report_summary"]["stat"]["response_time"]["response_time_level"]["slow"]}毫秒
                    </span>, 
                    """
                )
            if content_data["report_summary"]["stat"]["response_time"]["very_slow"]:
                notify_template += (
                    f"""
                    <span style="color: #E4080A">
                        有{len(content_data["report_summary"]["stat"]["response_time"]["very_slow"])}个接口响应时间超过{content_data["report_summary"]["stat"]["response_time"]["response_time_level"]["very_slow"]}毫秒
                    </span>, 
                    """
                )
            notify_template += """<span style="color: #E4080A">请确认是否需要优化</span>"""
        notify_template += (
            f"""
            <div>
                <span>
                    详情请【<a style="color: #fe5b4c" href="{task_kwargs["report_addr"] + str(report_id)}">点击此处</a>】查看
                </span>
            </div>        
            <br/>
            """
        )
    notify_template += "</div>"
    return {"status": "fail" if "fail" in all_res else "success", "msg": notify_template}


def diff_api_msg(content, host, diff_api_addr, report_id):
    """ 接口对比报告模板 -- 钉钉 """
    return {
        "msgtype": "markdown",
        "markdown": {
            "title": "接口监控",
            "text": f'## 接口监控 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} \n> '
                    f'### 任务名：{content["title"]} \n> '
                    f'#### 对比服务:<font color=#27AE60> {content["project"]["totle"]} </font>个 \n> '
                    f'##### 新增服务:<font color=#27AE60> {content["project"]["add"]} </font>个 \n> '
                    f'##### 修改服务:<font color=#3498DB> {content["project"]["modify"]} </font>个 \n> '
                    f'##### 删除服务:<font color=#E74C3C> {content["project"]["remove"]} </font>个 \n> '
                    f'##### 乱码:<font color=#E74C3C> {content["project"]["errorCode"]} </font>个 \n> '
                    f'##### \n> '
                    f'#### 对比模块:<font color=#27AE60> {content["module"]["totle"]} </font>个 \n> '
                    f'##### 新增模块:<font color=#27AE60> {content["module"]["add"]} </font>个 \n> '
                    f'##### 修改模块:<font color=#3498DB> {content["module"]["modify"]} </font>个 \n> '
                    f'##### 删除模块:<font color=#E74C3C> {content["module"]["remove"]} </font>个 \n> '
                    f'##### 乱码:<font color=#E74C3C> {content["module"]["errorCode"]} </font>个 \n> '
                    f'##### \n> '
                    f'#### 对比接口:<font color=#27AE60> {content["api"]["totle"]} </font>个 \n> '
                    f'##### 新增接口:<font color=#27AE60> {content["api"]["add"]} </font>个 \n> '
                    f'##### 修改接口:<font color=#3498DB> {content["api"]["modify"]} </font>个 \n> '
                    f'##### 删除接口:<font color=#E74C3C> {content["api"]["remove"]} </font>个 \n> '
                    f'##### 乱码:<font color=#E74C3C> {content["api"]["errorCode"]} </font>个 \n> '
                    f'##### \n> '
                    f'#### 请【[点击此处]({host}{diff_api_addr}{str(report_id)})】查看详情，并确认是否更新\n'
        }
    }


def run_time_error_msg(content, host, func_error_addr):
    """ 执行自定义函数时发生了异常的报告 -- 钉钉 """
    return {
        "msgtype": "markdown",
        "markdown": {
            "title": content.get("title"),
            "text": content.get("detail") + f"#### 详情请【[点击此处]({host}{func_error_addr})】查看\n"
        }
    }


def call_back_webhook_msg(data):
    """ 发送回调数据消息到即时通讯 -- 钉钉 """
    return {
        "msgtype": "markdown",
        "markdown": {
            "title": "测试平台回调",
            "text": data
        }
    }


def business_stage_count_ding_ding(content):
    """ 组装阶段统计报告
    content：{
              "countTime": "month",
              "total": 189,
              "pass": 163,
              "fail": 26,
              "passRate": 0.862,
              "hitRecord": {
                "代码问题": 5,
                "环境问题": 2
              },
              "webhookList": [
                "https://"
              ],
              "receiveType": "ding_ding",
              "record": [
                {
                  "total": 189,
                  "pass": 163,
                  "fail": 26,
                  "passRate": 0.862,
                  "record": [],
                  "hitRecord": {
                    "代码问题": 5,
                    "环境问题": 2
                  },
                  "name": "服务XXX"
                }
              ]
            }
    """
    msg_template = {
        "msgtype": "markdown",
        "markdown": {"title": "阶段统计", "text": ""}
    }

    def get_detail_msg(time_type, title, data):
        detail_template = f'\n' \
                          f'#### 【{title}】<font color=#409EFF>本{time_type}</font> ' \
                          f'共执行自动化测试: <font color=#409EFF>{data["total"]}</font> 次\n> ' \
                          f'#### 通过: <font color=#409EFF> {data["pass"]} </font>次\n> ' \
                          f'#### 失败: <font color=#409EFF> {data["fail"]} </font>次\n> ' \
                          f'#### 通过率为: <font color=#409EFF> {round(data["passRate"] * 100, 2)}% </font>\n> '

        # 汇总问题记录
        total_hit_count = 0
        # if data["hitRecord"]:  # 有问题记录才统计
        hit_record_total = '#### 其中\n> '
        for hit_title, hit_count in data["hitRecord"].items():
            total_hit_count += hit_count
            hit_record_total += f'#### {hit_title}: <font color=#FF0000>{hit_count}</font> 个\n>'
        hit_record_total = f'#### 共记录问题: <font color=#FF0000>{total_hit_count}</font> 个\n>' + hit_record_total
        detail_template += hit_record_total
        return detail_template

    count_type = "月" if content["countTime"] == "month" else "周"
    msg_template["markdown"]["title"] = f'{count_type}统计报告'

    # 业务线汇总
    builtins_msg = f'### <font color=#409EFF>自动化测试{count_type}统计报告</font>\n>' \
                   f'#### 统计时间 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n>'
    builtins_msg += get_detail_msg(count_type, "本业务线", content)

    # 遍历每个服务
    for project in content["record"]:
        if project["total"]:  # 有执行的才统计
            builtins_msg += get_detail_msg(count_type, project["name"], project)

    msg_template["markdown"]["text"] = builtins_msg
    return msg_template


def business_stage_count_we_chat(content):
    pass


def get_business_stage_count_msg(content):
    if content["receiveType"] == "ding_ding":
        return business_stage_count_ding_ding(content)
    return business_stage_count_we_chat(content)


def server_status_msg_ding_ding(action_type, server_name, app_title):
    """ 服务状态通知 """
    return {
            "msgtype": "markdown",
            "markdown": {
                "title": f"服务<font color=#FF0000>【{action_type}】</font>通知",
                "text": f'### 服务<font color=#FF0000>【{action_type}】</font>通知 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} \n> '
                        f'#### 服务<font color=#FF0000>【{server_name}】【{app_title}】</font>{action_type}完成 \n> '
            }
        }

def server_status_msg_we_chat(action_type, server_name, app_title):
    """ 服务状态通知 """
    return {
        "msgtype": "markdown",
        "markdown": {
            "content": f'服务<font color=#FF0000>【{action_type}】</font>通知 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} \n\n'
                       f'### 服务<font color=#FF0000>【{server_name}】【{app_title}】</font>{action_type}完成 \n\n'
        }
    }


def debug_msg_ding_ding():
    """ 钉钉消息测试 """
    return {
        "msgtype": "markdown",
        "markdown": {
            "title": "测试通知",
            "text": "这是一条测试消息通知"
        }
    }


def debug_msg_we_chat():
    """ 企业微信消息测试 """
    return {
        "msgtype": "text",
        "text": {
            "content": "这是一条测试消息通知"
        }
    }
