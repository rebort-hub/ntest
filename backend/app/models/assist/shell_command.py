from ..base_model import BaseModel, fields


class ShellCommandRecord(BaseModel):
    
    class Meta:
        table = "auto_test_shell_command_record"
        table_description = "shell造数据"

    file_content = fields.TextField(default="", description="文件数据")
    command = fields.CharField(32, default="", description="shell命令")
    command_out_put = fields.TextField(default="", description="shell执行结果")
    cmd_id = fields.CharField(32, default="", description="日志里面的cmdId")
    algo_instance_id = fields.CharField(128, default="", description="日志里面的algoInstanceId")

