"""
提示词管理器
管理系统中的各种AI提示词模板
"""
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class PromptType(str, Enum):
    """提示词类型"""
    REQUIREMENT_ANALYSIS = "requirement_analysis"
    TEST_CASE_GENERATION = "test_case_generation"
    SCRIPT_GENERATION = "script_generation"
    CODE_REVIEW = "code_review"
    BUG_ANALYSIS = "bug_analysis"
    COMPLETENESS_ANALYSIS = "completeness_analysis"
    CONSISTENCY_ANALYSIS = "consistency_analysis"
    TESTABILITY_ANALYSIS = "testability_analysis"
    FEASIBILITY_ANALYSIS = "feasibility_analysis"
    CLARITY_ANALYSIS = "clarity_analysis"


class PromptTemplate:
    """提示词模板类"""
    
    def __init__(
        self,
        name: str,
        template: str,
        description: str = "",
        variables: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ):
        self.name = name
        self.template = template
        self.description = description
        self.variables = variables or []
        self.examples = examples or []
        self.created_at = datetime.now()
    
    def format(self, **kwargs) -> str:
        """格式化提示词模板"""
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing variable in prompt template: {e}")
            raise ValueError(f"Missing required variable: {e}")
    
    def validate_variables(self, **kwargs) -> bool:
        """验证变量是否完整"""
        missing_vars = []
        for var in self.variables:
            if var not in kwargs:
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"Missing variables: {missing_vars}")
            return False
        return True


class PromptManager:
    """提示词管理器"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._initialize_default_templates()
    
    def _initialize_default_templates(self):
        """初始化默认提示词模板"""
        
        # 需求分析模板
        self.register_template(
            PromptType.REQUIREMENT_ANALYSIS,
            PromptTemplate(
                name="需求分析",
                template="""
你是一位专业的需求分析师。请分析以下需求文档，从完整性、清晰度、一致性、可测性、可行性五个维度进行评估。

需求文档：
{requirement_text}

请按照以下JSON格式返回分析结果：
{{
    "completeness_score": 85,
    "clarity_score": 90,
    "consistency_score": 88,
    "testability_score": 75,
    "feasibility_score": 92,
    "overall_rating": "good",
    "summary": "需求文档整体质量良好，但在可测性方面需要改进",
    "issues": [
        {{
            "type": "testability",
            "priority": "medium",
            "title": "缺少验收标准",
            "description": "部分功能缺少明确的验收标准",
            "suggestion": "为每个功能点定义明确的验收标准",
            "location": "第3章功能需求"
        }}
    ],
    "strengths": ["需求描述详细", "功能模块划分清晰"],
    "recommendations": ["补充验收标准", "增加边界条件描述"]
}}

评分标准：
- 90-100分：优秀
- 80-89分：良好  
- 70-79分：一般
- 60-69分：需改进
- 60分以下：较差
""",
                description="分析需求文档的质量",
                variables=["requirement_text"]
            )
        )
        
        # 测试用例生成模板
        self.register_template(
            PromptType.TEST_CASE_GENERATION,
            PromptTemplate(
                name="测试用例生成",
                template="""
你是一位专业的测试工程师。基于以下需求，生成详细的测试用例。

需求描述：
{requirement_text}

请生成{test_case_count}个测试用例，每个测试用例包含：
1. 测试用例名称
2. 测试目标/描述
3. 前置条件
4. 测试步骤（详细的操作步骤）
5. 预期结果
6. 优先级（P0/P1/P2/P3）

请按照以下JSON格式返回：
{{
    "test_cases": [
        {{
            "name": "用户登录功能正常流程测试",
            "description": "验证用户使用正确的用户名和密码能够成功登录系统",
            "priority": "P0",
            "precondition": "用户已注册且账号状态正常，系统运行正常",
            "steps": [
                "打开登录页面",
                "输入正确的用户名",
                "输入正确的密码", 
                "点击登录按钮"
            ],
            "expected_result": "用户成功登录，跳转到主页面，显示用户信息"
        }}
    ]
}}

请确保测试用例覆盖正常流程、异常流程和边界条件。
""",
                description="基于需求生成测试用例",
                variables=["requirement_text", "test_case_count"]
            )
        )
        
        # Playwright脚本生成模板
        self.register_template(
            PromptType.SCRIPT_GENERATION,
            PromptTemplate(
                name="Playwright脚本生成",
                template="""
你是一位专业的自动化测试工程师。基于以下测试用例，生成Playwright Python自动化脚本。

测试用例信息：
名称：{test_case_name}
描述：{test_case_description}
前置条件：{precondition}
测试步骤：
{test_steps}
预期结果：{expected_result}

目标URL：{target_url}

请生成完整的Playwright Python脚本，要求：
1. 使用async/await语法
2. 包含必要的导入语句
3. 实现页面对象模式（如果适用）
4. 包含元素定位和操作
5. 添加适当的等待和断言
6. 包含异常处理
7. 添加详细的注释

脚本模板：
```python
import asyncio
from playwright.async_api import async_playwright, Page, Browser
import pytest

class {test_class_name}:
    def __init__(self, page: Page):
        self.page = page
        # 定义页面元素
        
    async def {test_method_name}(self):
        \"\"\"
        {test_case_description}
        \"\"\"
        try:
            # 实现测试步骤
            
            # 添加断言验证
            
        except Exception as e:
            print(f"测试失败: {{e}}")
            raise

async def test_{test_method_name}():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        test_instance = {test_class_name}(page)
        await test_instance.{test_method_name}()
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_{test_method_name}())
```

请生成可直接运行的完整脚本。
""",
                description="基于测试用例生成Playwright自动化脚本",
                variables=[
                    "test_case_name", "test_case_description", "precondition",
                    "test_steps", "expected_result", "target_url",
                    "test_class_name", "test_method_name"
                ]
            )
        )
        
        # 完整性分析模板
        self.register_template(
            PromptType.COMPLETENESS_ANALYSIS,
            PromptTemplate(
                name="完整性分析",
                template="""
你是一位专业的需求分析师。请专门从完整性角度分析以下需求文档。

需求文档：
{requirement_text}

完整性分析要点：
1. 功能需求是否完整覆盖
2. 非功能需求是否齐全
3. 业务流程是否完整
4. 异常处理是否考虑周全
5. 边界条件是否明确
6. 接口定义是否完整
7. 数据结构是否完整

请按照以下JSON格式返回分析结果：
{{
    "score": 85,
    "issues": [
        {{
            "type": "completeness",
            "priority": "high",
            "title": "缺少异常处理流程",
            "description": "文档中未描述系统异常情况下的处理流程",
            "suggestion": "补充系统异常、网络异常、数据异常等情况的处理方案",
            "location": "第4章系统设计"
        }}
    ],
    "strengths": [
        "功能需求描述详细",
        "业务流程清晰完整",
        "接口定义规范"
    ],
    "recommendations": [
        "补充异常处理流程",
        "增加边界条件说明",
        "完善非功能需求描述"
    ]
}}
""",
                description="专门分析需求文档的完整性",
                variables=["requirement_text"]
            )
        )
        
        # 一致性分析模板
        self.register_template(
            PromptType.CONSISTENCY_ANALYSIS,
            PromptTemplate(
                name="一致性分析",
                template="""
你是一位专业的需求分析师。请专门从一致性角度分析以下需求文档。

需求文档：
{requirement_text}

一致性分析要点：
1. 术语使用是否一致
2. 数据定义是否一致
3. 业务规则是否一致
4. 接口规范是否一致
5. 格式风格是否统一
6. 逻辑是否自洽

请按照以下JSON格式返回分析结果：
{{
    "score": 90,
    "issues": [
        {{
            "type": "consistency",
            "priority": "medium",
            "title": "术语使用不一致",
            "description": "文档中'用户'和'客户'两个术语混用",
            "suggestion": "统一使用'用户'术语，或明确区分两者的含义",
            "location": "第2章和第5章"
        }}
    ],
    "strengths": [
        "数据定义一致",
        "接口规范统一",
        "格式风格一致"
    ],
    "recommendations": [
        "建立术语词汇表",
        "统一业务规则表述",
        "保持文档格式一致性"
    ]
}}
""",
                description="专门分析需求文档的一致性",
                variables=["requirement_text"]
            )
        )
        
        # 可测性分析模板
        self.register_template(
            PromptType.TESTABILITY_ANALYSIS,
            PromptTemplate(
                name="可测性分析",
                template="""
你是一位专业的测试工程师。请专门从可测性角度分析以下需求文档。

需求文档：
{requirement_text}

可测性分析要点：
1. 需求是否可验证
2. 验收标准是否明确
3. 测试数据是否可准备
4. 测试环境是否可搭建
5. 功能是否可观测
6. 结果是否可量化

请按照以下JSON格式返回分析结果：
{{
    "score": 75,
    "issues": [
        {{
            "type": "testability",
            "priority": "high",
            "title": "缺少明确的验收标准",
            "description": "多个功能点缺少具体的验收标准和成功指标",
            "suggestion": "为每个功能点定义明确的验收标准，包括性能指标、准确率等",
            "location": "第3章功能需求"
        }}
    ],
    "strengths": [
        "功能描述清晰",
        "业务流程可跟踪",
        "接口定义明确"
    ],
    "recommendations": [
        "补充验收标准",
        "定义测试数据要求",
        "明确性能指标",
        "增加可观测性设计"
    ]
}}
""",
                description="专门分析需求文档的可测性",
                variables=["requirement_text"]
            )
        )
    
    def register_template(self, prompt_type: PromptType, template: PromptTemplate):
        """注册提示词模板"""
        self.templates[prompt_type] = template
        logger.info(f"Registered prompt template: {prompt_type}")
    
    def get_template(self, prompt_type: PromptType) -> Optional[PromptTemplate]:
        """获取提示词模板"""
        return self.templates.get(prompt_type)
    
    def format_prompt(self, prompt_type: PromptType, **kwargs) -> str:
        """格式化提示词"""
        template = self.get_template(prompt_type)
        if not template:
            raise ValueError(f"Template not found: {prompt_type}")
        
        return template.format(**kwargs)
    
    def list_templates(self) -> List[str]:
        """列出所有模板"""
        return list(self.templates.keys())
    
    def validate_template_variables(self, prompt_type: PromptType, **kwargs) -> bool:
        """验证模板变量"""
        template = self.get_template(prompt_type)
        if not template:
            return False
        
        return template.validate_variables(**kwargs)
    
    def get_template_info(self, prompt_type: PromptType) -> Optional[Dict[str, Any]]:
        """获取模板信息"""
        template = self.get_template(prompt_type)
        if not template:
            return None
        
        return {
            "name": template.name,
            "description": template.description,
            "variables": template.variables,
            "examples": template.examples,
            "created_at": template.created_at.isoformat()
        }


# 全局提示词管理器实例
_prompt_manager = None


def get_prompt_manager() -> PromptManager:
    """获取提示词管理器实例"""
    global _prompt_manager
    if _prompt_manager is None:
        _prompt_manager = PromptManager()
    return _prompt_manager


# 便捷函数
def format_prompt(prompt_type: PromptType, **kwargs) -> str:
    """格式化提示词的便捷函数"""
    manager = get_prompt_manager()
    return manager.format_prompt(prompt_type, **kwargs)


def get_template_info(prompt_type: PromptType) -> Optional[Dict[str, Any]]:
    """获取模板信息的便捷函数"""
    manager = get_prompt_manager()
    return manager.get_template_info(prompt_type)