import datetime
import json
import re
import time

import paramiko
from fastapi import Request, Depends

from utils.logs.log import logger
from ...schemas.assist import shell_command as schema

from ...models.assist.model_factory import ShellCommandRecord
from ...models.config.model_factory import Config


async def get_shell_command_list(request: Request):
    """ 获取命令列表 """
    return request.app.get_success([
        {"label": "模拟下单", "command": "start"},
        {"label": "stop", "command": "stop"},
        {"label": "先抢单平仓再shutdown", "command": "update_tl_ctrl_task"}
        # {"label": "先抢单平仓再shutdown", "command": "update_pause_resume"}
    ])


async def get_shell_command_record_list(request: Request, form: schema.GetShellCommandRecordList = Depends()):
    """ 获取造数据log列表 """
    query_data = await form.make_pagination(ShellCommandRecord)
    return request.app.get_success(query_data)


async def get_shell_command_record(request: Request, form: schema.GetShellCommandRecord = Depends()):
    """ 获取造数据log """
    data = await ShellCommandRecord.validate_is_exist("数据不存在", id=form.id)
    return request.app.get_success(data)


async def send_shell_command(request: Request, form: schema.SendShellCommand):
    """ 发送造数据命令 """
    shell_command_info = await Config.get_shell_command_info()
    ssh_client = SSHConnection(**shell_command_info)
    file_tab = f"make_data_{int(time.time() * 1000)}"
    command_out_put = ssh_client.send_shell_command(file_tab, form.file_content, form.command)
    cmd_id = ssh_client.get_cmd_id(command_out_put)
    algo_instance_id = ssh_client.ssh_client_get_algo_instance_id(cmd_id)
    ssh_client.remove_command_file(file_tab)
    await ShellCommandRecord.model_create({
        "file_content": form.file_content,
        "command": form.command,
        "command_out_put": command_out_put,
        "cmd_id": cmd_id,
        "algo_instance_id": algo_instance_id
    })
    return request.app.success(
        f"发送成功, algo_instance_id: {algo_instance_id}",
       data={
           "cmd_id": cmd_id, "algo_instance_id": algo_instance_id, "command_out_put": command_out_put
       })


class SSHConnection:

    def __init__(self, ip, port, username, password, file_path, log_path):
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.file_path = file_path
        self.log_path = log_path.format(datetime.datetime.now().strftime("%Y%m%d"))
        self.shell_path = f'{self.file_path}/send_req_stress_test.sh'
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动接受新服务器的key
        self.client.connect(self.ip, port=self.port, username=self.username, password=self.password)

    def __del__(self):
        """ 关闭连接 """
        if self.client:
            self.client.close()

    def wait_for_log(self, command: str, max_wait_count: int = 5, interval: int = 2):
        count = 0
        while max_wait_count > count:
            logger.info(f"【{datetime.datetime.now().strftime('%H:%M:%S')}】开始执行第【{count + 1}】次查询")
            time.sleep(interval)

            # 执行查询命令
            stdin, stdout, stderr = self.client.exec_command(command)  # 执行命令并获取输出
            lines = stdout.readlines()  # 读取命令输出

            # 如果找到了日志数据，直接返回
            if lines:
                return ''.join(lines)

            # 否则等待2秒再重试
            count += 2

        # 如果超时仍未找到，返回 None
        logger.info(f"在 {max_wait_count * interval} 秒内没有找到相关日志数据")
        return None

    def exec_command(self, command: str):
        logger.info(f"{'*' * 20}开始执行命令: {command} {'*' * 20}")
        stdin, stdout, stderr = self.client.exec_command(command)
        success = stderr.channel.recv_exit_status() == 0
        command_out_put = stdout.read().decode('utf-8')
        logger.info(f"执行结果: \n{command_out_put}")
        if not success:
            raise RuntimeError("执行命令报错")
        logger.info(f"{'*' * 20}命令执行结束: {command}{'*' * 20}")
        return command_out_put

    def send_shell_command(self, file_tab, content, command='start'):
        """ 创建shell请求文件, start/update/stop """
        command, cats_file_path = command.lower(), None
        sftp = self.client.open_sftp()

        # json文件
        if command == 'start':
            cats_file_path, batch_file_path = f"{self.file_path}{file_tab}.csv", f"{self.file_path}{file_tab}_start.json"
            if content.endswith("\n") is False:
                content += "\n"
            batch_content = json.dumps([
                {
                    "type": "t0",
                    "filenames": [cats_file_path]
                }
            ], ensure_ascii=False, indent=4)
            cmd = '-s'

        elif command == 'stop':
            cats_file_path, batch_file_path = f"{self.file_path}{file_tab}.txt", f"{self.file_path}{file_tab}_stop.json"
            batch_content = json.dumps({
                "type": "all",
                "_type": "batch",
                "filenames": [cats_file_path]
            }, ensure_ascii=False, indent=4)
            cmd = '-S'

        elif command == 'update_tl_ctrl_task':  # update
            batch_file_path = f"{self.file_path}{file_tab}_update_TLCtrlTask.json"
            batch_content = json.dumps(json.loads(content), ensure_ascii=False, indent=4)
            cmd = '-u'

        else: # update_pause_resume
            batch_file_path = f"{self.file_path}{file_tab}_update_pauseResume.json"
            batch_content = json.dumps(json.loads(content), ensure_ascii=False, indent=4)
            cmd = '-U'

        if cats_file_path:
            with sftp.open(cats_file_path, 'w') as file:
                file.write(content) # T0文件

        with sftp.open(batch_file_path, 'w') as file:
            file.write(batch_content) # json文件

        return self.exec_command(f'{self.shell_path} {cmd} {batch_file_path}')

    def remove_command_file(self, file_tab):
        """ 删除shell请求文件 """
        self.client.exec_command(f'sudo rm -rf {self.file_path}{file_tab}*')

    def get_cmd_id(self, command_out_put: str):
        """ start命令的返回中获取cmdId """
        logger.info(f"{'*' * 20}开始start命令的返回中获取cmdId {'*' * 20}")
        logger.info(command_out_put)
        assert 'message=cmdId=' in command_out_put, f"获取 cmdId 失败，响应中没有获取到 cmdId= 相关字样"
        return re.search(r'message=cmdId=([^,]+). Processing', command_out_put).group(1)

    def ssh_client_get_algo_instance_id(self, cmd_id: str):
        """ 从日志中获取 algoInstanceId """
        logger.info(f"{'*' * 20}开始从日志中获取 algoInstanceId {'*' * 20}")
        last_minutes = (datetime.datetime.now() - datetime.timedelta(minutes=1)).strftime('%H:%M')  # 上一分钟
        now_minutes = datetime.datetime.now().strftime('%H:%M')  # 当前分钟
        next_minutes = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%H:%M')  # 下1分钟
        logger.info(f'last_minutes: {last_minutes}，now_minutes: {now_minutes}，next_minutes: {next_minutes}')
        last_minutes, now_minutes, next_minutes =  f"{last_minutes}:", f"{now_minutes}:", f"{next_minutes}:"

        command = f"grep 'cmdId={cmd_id}' {self.log_path} | grep 'algoInstanceId' | sort -r | head -n 1"
        wait_count, log_data = 0, None
        while wait_count < 10:
            logger.info(f"执行命令：{command}")
            wait_count += 1
            log_data = self.wait_for_log(command, 1, interval=0)
            logger.info(f"执行结果：{log_data}")
            # 确认数据是当前操作产生的
            if log_data and ((last_minutes in log_data) or (now_minutes in log_data) or (next_minutes in log_data)):
                break

        if log_data is None:
            return f"获取 algoInstanceId 失败，没有查到当前操作触发的 cmdId={cmd_id} 的 algoInstanceId= 相关字样的日志"
        return re.search(r'algoInstanceId=([^,]+)', log_data).group(1).replace("\n", "")