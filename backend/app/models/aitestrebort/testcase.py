"""
aitestrebort 测试用例管理模型
基于 Tortoise ORM
"""
from tortoise import fields
from ..base_model import BaseModel


class aitestrebortTestCaseModule(BaseModel):
    """测试用例模块模型，支持5级子模块"""
    
    project = fields.ForeignKeyField(
        "test_platform.aitestrebortProject",
        related_name="testcase_modules",
        description="所属项目"
    )
    name = fields.CharField(max_length=100, description="模块名称")
    description = fields.TextField(null=True, description="模块描述")
    parent = fields.ForeignKeyField(
        "test_platform.aitestrebortTestCaseModule",
        related_name="children",
        null=True,
        description="父模块"
    )
    level = fields.SmallIntField(default=1, description="模块级别")
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "aitestrebort_testcase_module"
        table_description = "aitestrebort 测试用例模块表"
        unique_together = (("project", "parent", "name"),)

    def __str__(self):
        return self.name

    async def get_all_descendant_ids(self):
        """获取当前模块及其所有子模块的ID列表（递归）"""
        ids = [self.id]
        children = await aitestrebortTestCaseModule.filter(parent=self).all()
        for child in children:
            child_ids = await child.get_all_descendant_ids()
            ids.extend(child_ids)
        return ids


class aitestrebortTestCase(BaseModel):
    """测试用例模型"""
    
    LEVEL_CHOICES = [
        ("P0", "P0"),
        ("P1", "P1"), 
        ("P2", "P2"),
        ("P3", "P3"),
    ]
    
    project = fields.ForeignKeyField(
        "test_platform.aitestrebortProject",
        related_name="testcases",
        description="所属项目"
    )
    module = fields.ForeignKeyField(
        "test_platform.aitestrebortTestCaseModule",
        related_name="testcases",
        description="所属模块"
    )
    name = fields.CharField(max_length=255, description="用例名称")
    description = fields.TextField(null=True, description="用例描述")
    precondition = fields.TextField(null=True, description="前置条件")
    level = fields.CharField(
        max_length=2,
        default="P2",
        description="用例等级"
    )
    creator_id = fields.IntField(description="创建人ID")
    notes = fields.TextField(null=True, description="备注")
    
    class Meta:
        table = "aitestrebort_testcase"
        table_description = "aitestrebort 测试用例表"

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class aitestrebortTestCaseStep(BaseModel):
    """用例步骤模型"""
    
    test_case = fields.ForeignKeyField(
        "test_platform.aitestrebortTestCase",
        related_name="steps",
        description="所属用例"
    )
    step_number = fields.IntField(description="步骤编号")
    description = fields.TextField(description="步骤描述")
    expected_result = fields.TextField(description="预期结果")
    creator_id = fields.IntField(description="创建人ID")
    
    class Meta:
        table = "aitestrebort_testcase_step"
        table_description = "aitestrebort 测试用例步骤表"
        unique_together = (("test_case", "step_number"),)

    def __str__(self):
        return f"{self.test_case.name} - Step {self.step_number}"


class aitestrebortTestCaseScreenshot(BaseModel):
    """测试用例截图模型"""
    
    test_case = fields.ForeignKeyField(
        "test_platform.aitestrebortTestCase",
        related_name="screenshots",
        description="测试用例"
    )
    screenshot_path = fields.CharField(max_length=500, description="截图路径")
    title = fields.CharField(max_length=255, null=True, description="图片标题")
    description = fields.TextField(null=True, description="图片描述")
    step_number = fields.IntField(null=True, description="对应步骤")
    
    # MCP执行相关信息
    mcp_session_id = fields.CharField(max_length=255, null=True, description="MCP会话ID")
    page_url = fields.CharField(max_length=2000, null=True, description="页面URL")
    uploader_id = fields.IntField(description="上传人ID")
    
    class Meta:
        table = "aitestrebort_testcase_screenshot"
        table_description = "aitestrebort 测试用例截图表"

    def __str__(self):
        if self.title:
            return f"{self.test_case.name} - {self.title}"
        return f"{self.test_case.name} - Screenshot"


class aitestrebortTestSuite(BaseModel):
    """测试套件模型"""
    
    name = fields.CharField(max_length=255, description="套件名称")
    description = fields.TextField(null=True, description="套件描述")
    project = fields.ForeignKeyField(
        "test_platform.aitestrebortProject",
        related_name="test_suites",
        description="所属项目"
    )
    creator_id = fields.IntField(description="创建人ID")
    max_concurrent_tasks = fields.SmallIntField(
        default=1,
        description="最大并发数"
    )
    
    class Meta:
        table = "aitestrebort_testsuite"
        table_description = "aitestrebort 测试套件表"
        unique_together = (("project", "name"),)

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class aitestrebortTestSuiteCase(BaseModel):
    """测试套件用例关联表"""
    
    suite = fields.ForeignKeyField(
        "test_platform.aitestrebortTestSuite",
        related_name="suite_cases",
        description="测试套件"
    )
    testcase = fields.ForeignKeyField(
        "test_platform.aitestrebortTestCase",
        related_name="case_suites",
        description="测试用例"
    )
    
    class Meta:
        table = "aitestrebort_testsuite_case"
        table_description = "aitestrebort 测试套件用例关联表"
        unique_together = (("suite", "testcase"),)


class aitestrebortTestExecution(BaseModel):
    """测试执行记录模型"""
    
    suite = fields.ForeignKeyField(
        "test_platform.aitestrebortTestSuite",
        related_name="executions",
        description="测试套件"
    )
    status = fields.CharField(
        max_length=20,
        default="pending",
        description="执行状态"
    )
    executor_id = fields.IntField(description="执行人ID")
    started_at = fields.DatetimeField(null=True, description="开始时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")
    
    # 统计信息
    total_count = fields.IntField(default=0, description="总用例数")
    passed_count = fields.IntField(default=0, description="通过数")
    failed_count = fields.IntField(default=0, description="失败数")
    skipped_count = fields.IntField(default=0, description="跳过数")
    error_count = fields.IntField(default=0, description="错误数")
    
    # 任务ID
    celery_task_id = fields.CharField(max_length=255, null=True, description="任务ID")
    
    class Meta:
        table = "aitestrebort_test_execution"
        table_description = "aitestrebort 测试执行记录表"

    def __str__(self):
        return f"{self.suite.name} - {self.status}"

    @property
    def pass_rate(self):
        """计算通过率"""
        if self.total_count > 0:
            return round((self.passed_count / self.total_count) * 100, 2)
        return 0.0


class aitestrebortTestCaseResult(BaseModel):
    """测试用例执行结果模型"""
    
    execution = fields.ForeignKeyField(
        "test_platform.aitestrebortTestExecution",
        related_name="results",
        description="测试执行"
    )
    testcase = fields.ForeignKeyField(
        "test_platform.aitestrebortTestCase",
        related_name="execution_results",
        description="测试用例"
    )
    status = fields.CharField(
        max_length=20,
        default="pending",
        description="执行状态"
    )
    error_message = fields.TextField(null=True, description="错误信息")
    stack_trace = fields.TextField(null=True, description="堆栈跟踪")
    
    # 执行时间统计
    started_at = fields.DatetimeField(null=True, description="开始时间")
    completed_at = fields.DatetimeField(null=True, description="完成时间")
    execution_time = fields.FloatField(null=True, description="执行耗时(秒)")
    
    # MCP相关信息
    mcp_session_id = fields.CharField(max_length=255, null=True, description="MCP会话ID")
    
    # 截图信息(JSON格式存储截图路径列表)
    screenshots = fields.JSONField(default=list, description="截图列表")
    
    # 执行日志
    execution_log = fields.TextField(null=True, description="执行日志")
    
    class Meta:
        table = "aitestrebort_testcase_result"
        table_description = "aitestrebort 测试用例执行结果表"
        unique_together = (("execution", "testcase"),)

    def __str__(self):
        return f"{self.testcase.name} - {self.status}"