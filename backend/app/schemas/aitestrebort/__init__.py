"""
aitestrebort 集成模块 - 数据模式
基于 Pydantic 模型
"""
from .project import (
    aitestrebortProjectSchema, aitestrebortProjectCreateSchema, aitestrebortProjectUpdateSchema,
    aitestrebortProjectCredentialSchema, aitestrebortProjectMemberSchema
)
from .testcase import (
    aitestrebortTestCaseSchema, aitestrebortTestCaseCreateSchema, aitestrebortTestCaseUpdateSchema,
    aitestrebortTestCaseStepSchema, aitestrebortTestCaseModuleSchema, aitestrebortTestCaseScreenshotSchema,
    aitestrebortTestSuiteSchema, aitestrebortTestExecutionSchema, aitestrebortTestCaseResultSchema
)
from .automation import (
    aitestrebortAutomationScriptSchema, aitestrebortScriptExecutionSchema
)

__all__ = [
    'aitestrebortProjectSchema', 'aitestrebortProjectCreateSchema', 'aitestrebortProjectUpdateSchema',
    'aitestrebortProjectCredentialSchema', 'aitestrebortProjectMemberSchema',
    'aitestrebortTestCaseSchema', 'aitestrebortTestCaseCreateSchema', 'aitestrebortTestCaseUpdateSchema',
    'aitestrebortTestCaseStepSchema', 'aitestrebortTestCaseModuleSchema', 'aitestrebortTestCaseScreenshotSchema',
    'aitestrebortTestSuiteSchema', 'aitestrebortTestExecutionSchema', 'aitestrebortTestCaseResultSchema',
    'aitestrebortAutomationScriptSchema', 'aitestrebortScriptExecutionSchema'
]