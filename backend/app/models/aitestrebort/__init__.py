"""
aitestrebort 集成模块 - 数据模型
基于现有 FastAPI + Tortoise ORM 架构
"""
from .project import (
    aitestrebortProject, aitestrebortProjectCredential, aitestrebortProjectMember,
    aitestrebortLLMConfig, aitestrebortMCPConfig, aitestrebortAPIKey,
    aitestrebortConversation, aitestrebortMessage, aitestrebortPrompt
)
from .testcase import (
    aitestrebortTestCase, aitestrebortTestCaseStep, aitestrebortTestCaseModule, 
    aitestrebortTestCaseScreenshot, aitestrebortTestSuite, aitestrebortTestSuiteCase,
    aitestrebortTestExecution, aitestrebortTestCaseResult
)
from .automation import aitestrebortAutomationScript, aitestrebortScriptExecution
from .knowledge import (
    aitestrebortKnowledgeBase, aitestrebortDocument, aitestrebortDocumentChunk,
    aitestrebortKnowledgeQuery, aitestrebortKnowledgeConfig
)
from .requirements import (
    RequirementDocument, RequirementModule, Requirement,
    ReviewReport, ReviewIssue, ModuleReviewResult
)
from .orchestrator import (
    OrchestratorTask, AgentTask, AgentStep, AgentBlackboard
)

__all__ = [
    # 项目管理
    'aitestrebortProject', 'aitestrebortProjectCredential', 'aitestrebortProjectMember',
    # LLM 和配置管理
    'aitestrebortLLMConfig', 'aitestrebortMCPConfig', 'aitestrebortAPIKey',
    # 对话管理
    'aitestrebortConversation', 'aitestrebortMessage', 'aitestrebortPrompt',
    # 测试用例管理
    'aitestrebortTestCase', 'aitestrebortTestCaseStep', 'aitestrebortTestCaseModule',
    'aitestrebortTestCaseScreenshot', 'aitestrebortTestSuite', 'aitestrebortTestSuiteCase',
    'aitestrebortTestExecution', 'aitestrebortTestCaseResult', 
    # 自动化脚本
    'aitestrebortAutomationScript', 'aitestrebortScriptExecution',
    # 知识库管理
    'aitestrebortKnowledgeBase', 'aitestrebortDocument', 'aitestrebortDocumentChunk',
    'aitestrebortKnowledgeQuery', 'aitestrebortKnowledgeConfig',
    # 需求管理和评审
    'RequirementDocument', 'RequirementModule', 'Requirement',
    'ReviewReport', 'ReviewIssue', 'ModuleReviewResult',
    # 智能编排
    'OrchestratorTask', 'AgentTask', 'AgentStep', 'AgentBlackboard'
]
