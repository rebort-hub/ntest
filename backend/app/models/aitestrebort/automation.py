"""
aitestrebort 自动化脚本管理模型
基于 Tortoise ORM
"""
from tortoise import fields
from ..base_model import BaseModel


class aitestrebortAutomationScript(BaseModel):
    """自动化脚本模型"""
    
    SCRIPT_TYPE_CHOICES = [
        ("playwright_python", "Playwright Python"),
        ("playwright_javascript", "Playwright JavaScript"),
    ]
    
    SOURCE_CHOICES = [
        ("ai_generated", "AI 自动生成"),
        ("manual", "手动编写"),
        ("recorded", "录制生成"),
    ]
    
    STATUS_CHOICES = [
        ("draft", "草稿"),
        ("active", "启用"),
        ("deprecated", "已废弃"),
    ]
    
    # 关联功能用例（可选）
    test_case = fields.ForeignKeyField(
        "test_platform.aitestrebortTestCase",
        related_name="automation_scripts",
        null=True,
        description="关联功能用例"
    )
    
    # 来源任务（可选，AI 生成时关联）
    source_task_id = fields.IntField(null=True, description="来源任务ID")
    
    # 脚本基本信息
    name = fields.CharField(max_length=255, description="脚本名称")
    description = fields.TextField(null=True, description="脚本描述")
    script_type = fields.CharField(
        max_length=30,
        default="playwright_python",
        description="脚本类型"
    )
    source = fields.CharField(
        max_length=20,
        default="ai_generated",
        description="来源"
    )
    status = fields.CharField(
        max_length=20,
        default="active",
        description="状态"
    )
    
    # 脚本内容
    script_content = fields.TextField(description="脚本代码")
    
    # 原始记录的操作步骤（JSON 格式，用于重新生成或分析）
    recorded_steps = fields.JSONField(
        default=list,
        description="记录的操作步骤"
    )
    
    # 配置
    target_url = fields.CharField(max_length=2000, null=True, description="目标URL")
    timeout_seconds = fields.IntField(default=30, description="超时时间(秒)")
    headless = fields.BooleanField(default=True, description="无头模式")
    
    # 版本管理
    version = fields.IntField(default=1, description="版本号")
    
    # 兼容旧字段
    project = fields.ForeignKeyField(
        "test_platform.aitestrebortProject",
        related_name="automation_scripts_legacy",
        null=True,
        description="所属项目(兼容字段)"
    )
    project_id = fields.IntField(description="所属项目ID")
    framework = fields.CharField(
        max_length=20,
        null=True,
        description="测试框架(兼容字段)"
    )
    language = fields.CharField(
        max_length=20,
        default="python",
        description="编程语言(兼容字段)"
    )
    
    # 元信息
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "aitestrebort_automation_script"
        table_description = "aitestrebort 自动化脚本表"

    def __str__(self):
        return f"{self.test_case.name} - {self.name} (v{self.version})"

    @property
    async def project(self):
        """获取所属项目"""
        if self.test_case:
            test_case = await self.test_case
            return await test_case.project
        return await self.project


class aitestrebortScriptExecution(BaseModel):
    """脚本执行记录模型"""
    
    STATUS_CHOICES = [
        ("pending", "等待中"),
        ("running", "执行中"),
        ("pass", "通过"),
        ("fail", "失败"),
        ("error", "错误"),
        ("cancelled", "已取消"),
    ]
    
    script = fields.ForeignKeyField(
        "test_platform.aitestrebortAutomationScript",
        related_name="executions",
        description="执行的脚本"
    )
    
    # 关联到测试套件执行记录（可选，因为脚本也可以单独执行）
    test_execution = fields.ForeignKeyField(
        "test_platform.aitestrebortTestExecution",
        related_name="script_results",
        null=True,
        description="测试执行"
    )
    
    status = fields.CharField(
        max_length=20,
        default="pending",
        description="执行状态"
    )
    
    # 执行时间
    started_at = fields.DatetimeField(null=True, description="开始时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")
    execution_time = fields.FloatField(null=True, description="执行耗时(秒)")
    
    # 执行结果
    output = fields.TextField(null=True, description="执行输出")
    error_message = fields.TextField(null=True, description="错误信息")
    stack_trace = fields.TextField(null=True, description="堆栈跟踪")
    
    # 截图（JSON 格式存储路径列表）
    screenshots = fields.JSONField(default=list, description="截图列表")
    
    # 录屏（JSON 格式存储路径列表）
    videos = fields.JSONField(default=list, description="录屏列表")
    
    # 执行环境信息
    browser_type = fields.CharField(max_length=50, default="chromium", description="浏览器类型")
    viewport = fields.JSONField(default=dict, description="视口大小")
    
    # 兼容旧字段
    executor_id = fields.IntField(description="执行人ID")
    environment = fields.CharField(max_length=100, null=True, description="执行环境")
    parameters = fields.JSONField(default=dict, description="执行参数")
    result_data = fields.JSONField(default=dict, description="执行结果数据")
    execution_log = fields.TextField(null=True, description="执行日志")
    celery_task_id = fields.CharField(max_length=255, null=True, description="任务ID")
    
    class Meta:
        table = "aitestrebort_script_execution"
        table_description = "aitestrebort 脚本执行记录表"

    def __str__(self):
        return f"{self.script.name} - {self.status}"

    @property
    def duration(self):
        """计算执行时长(秒)"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return self.execution_time