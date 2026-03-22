"""
Playwright Test Agents 数据模型
"""
from tortoise import fields
from .base_model import BaseModel


class PlaywrightTestPlan(BaseModel):
    """测试计划模型"""
    
    url = fields.CharField(max_length=500, description="应用URL")
    max_depth = fields.IntField(default=2, description="探索深度")
    timeout = fields.IntField(default=60, description="超时时间(秒)")
    status = fields.CharField(
        max_length=20, 
        default="pending",
        description="状态: pending, exploring, completed, failed"
    )
    test_scenarios = fields.JSONField(null=True, description="测试场景列表")
    exploration_result = fields.JSONField(null=True, description="探索结果")
    llm_config_id = fields.IntField(null=True, description="使用的LLM配置ID")
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "playwright_test_plan"
        table_description = "Playwright测试计划表"

    def __str__(self):
        return f"TestPlan #{self.id} - {self.url}"


class PlaywrightGeneratedCode(BaseModel):
    """生成的测试代码模型"""
    
    plan = fields.ForeignKeyField(
        "test_platform.PlaywrightTestPlan",
        related_name="generated_codes",
        description="关联的测试计划"
    )
    framework = fields.CharField(max_length=50, default="playwright", description="测试框架")
    language = fields.CharField(max_length=20, default="typescript", description="编程语言")
    code = fields.TextField(description="生成的测试代码")
    config_file = fields.TextField(null=True, description="配置文件内容")
    status = fields.CharField(
        max_length=20,
        default="pending",
        description="状态: pending, generating, completed, failed"
    )
    llm_config_id = fields.IntField(null=True, description="使用的LLM配置ID")
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "playwright_generated_code"
        table_description = "Playwright生成代码表"

    def __str__(self):
        return f"Code #{self.id} - Plan #{self.plan_id}"


class PlaywrightExecution(BaseModel):
    """测试执行记录模型"""
    
    code = fields.ForeignKeyField(
        "test_platform.PlaywrightGeneratedCode",
        related_name="executions",
        description="关联的测试代码"
    )
    browser = fields.CharField(max_length=20, default="chromium", description="浏览器")
    headless = fields.BooleanField(default=True, description="是否无头模式")
    status = fields.CharField(
        max_length=20,
        default="pending",
        description="状态: pending, running, success, failed"
    )
    start_time = fields.DatetimeField(null=True, description="开始时间")
    end_time = fields.DatetimeField(null=True, description="结束时间")
    duration = fields.FloatField(null=True, description="执行时长(秒)")
    stdout = fields.TextField(null=True, description="标准输出")
    stderr = fields.TextField(null=True, description="错误输出")
    exit_code = fields.IntField(null=True, description="退出码")
    error_message = fields.TextField(null=True, description="错误信息")
    screenshots = fields.JSONField(null=True, description="截图列表")
    videos = fields.JSONField(null=True, description="视频列表")
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "playwright_execution"
        table_description = "Playwright执行记录表"

    def __str__(self):
        return f"Execution #{self.id} - Code #{self.code_id}"


class PlaywrightHealRecord(BaseModel):
    """自愈修复记录模型"""
    
    execution = fields.ForeignKeyField(
        "test_platform.PlaywrightExecution",
        related_name="heal_records",
        description="关联的执行记录"
    )
    original_code = fields.ForeignKeyField(
        "test_platform.PlaywrightGeneratedCode",
        related_name="heal_records_as_original",
        description="原始代码"
    )
    fixed_code = fields.ForeignKeyField(
        "test_platform.PlaywrightGeneratedCode",
        related_name="heal_records_as_fixed",
        null=True,
        description="修复后的代码"
    )
    status = fields.CharField(
        max_length=20,
        default="pending",
        description="状态: pending, healing, success, failed"
    )
    error_analysis = fields.TextField(null=True, description="错误分析")
    fix_description = fields.TextField(null=True, description="修复说明")
    changes = fields.JSONField(null=True, description="代码变更列表")
    llm_config_id = fields.IntField(null=True, description="使用的LLM配置ID")
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "playwright_heal_record"
        table_description = "Playwright自愈修复记录表"

    def __str__(self):
        return f"Heal #{self.id} - Execution #{self.execution_id}"


class PlaywrightExplorationStep(BaseModel):
    """探索过程步骤记录模型"""
    
    plan = fields.ForeignKeyField(
        "test_platform.PlaywrightTestPlan",
        related_name="exploration_steps",
        description="关联的测试计划"
    )
    step_number = fields.IntField(description="步骤序号")
    action = fields.CharField(max_length=100, description="操作类型: navigate, click, type, snapshot等")
    description = fields.TextField(description="步骤描述")
    url = fields.CharField(max_length=500, null=True, description="当前页面URL")
    screenshot = fields.TextField(null=True, description="截图的base64数据或文件路径")
    page_title = fields.CharField(max_length=200, null=True, description="页面标题")
    elements_found = fields.JSONField(null=True, description="发现的元素信息")
    timestamp = fields.DatetimeField(auto_now_add=True, description="步骤时间")
    duration = fields.FloatField(null=True, description="步骤耗时(秒)")
    status = fields.CharField(
        max_length=20,
        default="success",
        description="状态: success, failed, warning"
    )
    error_message = fields.TextField(null=True, description="错误信息")
    
    class Meta:
        table = "playwright_exploration_step"
        table_description = "Playwright探索步骤记录表"
        ordering = ["step_number"]

    def __str__(self):
        return f"Step #{self.step_number} - {self.action} - Plan #{self.plan_id}"
