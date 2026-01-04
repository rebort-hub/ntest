"""
高级功能API路由
包含LangGraph智能编排、脚本生成、需求检索、质量评估、图表生成等功能
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from fastapi import HTTPException
from pydantic import BaseModel, Field

from app.routers.base_view import APIRouter
from app.services.aitestrebort.script_generator import (
    PlaywrightScriptGenerator,
    TestCaseTemplateGenerator
)
from app.models.aitestrebort.knowledge import aitestrebortKnowledgeBase, aitestrebortDocument
from utils.logs.log import logger

router = APIRouter(prefix="/aitestrebort/advanced", tags=["aitestrebort - 高级功能"])


# ==================== 请求/响应模型 ====================

class RAGQueryRequest(BaseModel):
    """RAG查询请求"""
    question: str = Field(..., description="查询问题")
    knowledge_base_id: str = Field(..., description="知识库ID")
    use_knowledge_base: bool = Field(True, description="是否使用知识库")
    similarity_threshold: float = Field(0.7, description="相似度阈值")
    top_k: int = Field(5, description="返回结果数量")
    thread_id: Optional[str] = Field(None, description="对话线程ID")


class AgentExecutionRequest(BaseModel):
    """Agent执行请求"""
    goal: str = Field(..., description="执行目标")
    session_id: str = Field(..., description="会话ID")
    max_steps: int = Field(50, description="最大步骤数")
    tools: List[str] = Field(default=[], description="可用工具列表")
    initial_context: Dict[str, Any] = Field(default={}, description="初始上下文")


class ScriptGenerationRequest(BaseModel):
    """脚本生成请求"""
    recorded_steps: List[Dict[str, Any]] = Field(..., description="记录的操作步骤")
    test_case_name: str = Field(..., description="测试用例名称")
    target_url: str = Field("", description="目标URL")
    timeout_seconds: int = Field(30, description="超时时间")
    headless: bool = Field(True, description="是否无头模式")
    use_pytest: bool = Field(True, description="是否使用pytest")
    description: str = Field("", description="测试描述")


class RequirementRetrievalRequest(BaseModel):
    """需求检索请求"""
    query: str = Field(..., description="查询内容")
    knowledge_base_id: str = Field(..., description="知识库ID")
    requirement_types: List[str] = Field(default=[], description="需求类型过滤")
    top_k: int = Field(5, description="返回结果数量")


class TestCaseGenerationRequest(BaseModel):
    """测试用例生成请求"""
    requirement: str = Field(..., description="需求描述")
    knowledge_base_id: Optional[str] = Field(None, description="知识库ID")
    similar_cases: List[Dict[str, Any]] = Field(default=[], description="相似测试用例")


class ContextAwareGenerationRequest(BaseModel):
    """上下文感知生成请求"""
    request: str = Field(..., description="生成请求")
    knowledge_base_id: str = Field(..., description="知识库ID")
    generation_type: str = Field("test_case", description="生成类型")
    context_sources: List[str] = Field(default=[], description="上下文来源")


class QualityAssessmentRequest(BaseModel):
    """质量评估请求"""
    content: Dict[str, Any] = Field(..., description="要评估的内容")
    content_type: str = Field(..., description="内容类型")
    knowledge_base_id: Optional[str] = Field(None, description="知识库ID")
    reference_data: List[Dict[str, Any]] = Field(default=[], description="参考数据")


# ==================== LangGraph智能编排 ====================

@router.post("/projects/{project_id}/rag-query")
async def rag_query(project_id: int, request: RAGQueryRequest):
    """
    执行RAG查询
    """
    try:
        # 暂时返回模拟数据，等待完整的RAG服务实现
        result = {
            "question": request.question,
            "answer": "这是一个模拟的RAG查询响应。RAG服务正在开发中。",
            "context": [
                {
                    "content": "模拟的上下文内容",
                    "metadata": {"source": "模拟文档"},
                    "similarity_score": 0.85
                }
            ],
            "retrieval_time": 0.1,
            "generation_time": 0.2,
            "total_time": 0.3
        }
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG查询失败: {str(e)}")


@router.post("/projects/{project_id}/agent-execution")
async def agent_execution(project_id: int, request: AgentExecutionRequest):
    """
    执行Agent任务
    """
    try:
        # 暂时返回模拟数据，等待完整的Agent服务实现
        result = {
            "status": "completed",
            "response": "这是一个模拟的Agent执行响应。Agent服务正在开发中。",
            "steps": 3,
            "history": [
                "步骤1: 分析目标",
                "步骤2: 执行操作", 
                "步骤3: 生成结果"
            ],
            "task_id": f"task_{project_id}_{request.session_id}"
        }
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent执行失败: {str(e)}")


@router.get("/projects/{project_id}/knowledge-bases")
async def get_project_knowledge_bases(project_id: int):
    """
    获取项目知识库列表
    """
    try:
        # 直接查询数据库，不依赖复杂的服务
        knowledge_bases = await aitestrebortKnowledgeBase.filter(
            project_id=project_id, is_active=True
        ).all()

        result = []
        for kb in knowledge_bases:
            # 计算文档数量
            doc_count = await aitestrebortDocument.filter(knowledge_base=kb).count()
            
            result.append({
                "id": str(kb.id),
                "name": kb.name,
                "description": kb.description or "",
                "document_count": doc_count,
                "created_at": kb.created_at.isoformat(),
                "updated_at": kb.updated_at.isoformat()
            })

        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"获取知识库列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取知识库列表失败: {str(e)}")


# ==================== 图表生成 ====================

class DiagramGenerationRequest(BaseModel):
    """图表生成请求"""
    diagram_type: str = Field(..., description="图表类型")
    data_source: str = Field(..., description="数据源类型")
    document_id: Optional[str] = Field(None, description="文档ID")
    knowledge_base_id: Optional[str] = Field(None, description="知识库ID")
    description: str = Field(..., description="生成描述")
    style: str = Field("simple", description="图表风格")


@router.post("/projects/{project_id}/generate-diagram")
async def generate_diagram(project_id: int, request: DiagramGenerationRequest):
    """
    生成AI图表
    """
    try:
        logger.info(f"开始生成图表，项目ID: {project_id}, 类型: {request.diagram_type}")
        
        # 根据数据源获取内容
        source_content = ""
        if request.data_source == "requirement" and request.document_id:
            # 从需求文档获取内容
            try:
                from app.models.aitestrebort.requirements import RequirementDocument
                doc = await RequirementDocument.get(id=request.document_id)
                source_content = doc.content or ""
            except Exception as e:
                logger.warning(f"获取需求文档失败: {e}")
                
        elif request.data_source == "knowledge" and request.knowledge_base_id:
            # 从知识库获取内容
            try:
                docs = await aitestrebortDocument.filter(
                    knowledge_base_id=request.knowledge_base_id
                ).limit(5).all()
                source_content = "\n".join([doc.content for doc in docs if doc.content])
            except Exception as e:
                logger.warning(f"获取知识库内容失败: {e}")
        
        # 生成图表代码
        diagram_result = await _generate_diagram_code(
            diagram_type=request.diagram_type,
            description=request.description,
            source_content=source_content,
            style=request.style
        )
        
        result = {
            "id": f"diagram_{int(time.time())}",
            "diagram_type": request.diagram_type,
            "mermaid_code": diagram_result["mermaid_code"],
            "plantuml_code": diagram_result.get("plantuml_code", ""),
            "description": diagram_result["description"],
            "style": request.style,
            "data_source": request.data_source,
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"图表生成成功: {request.diagram_type}")
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"图表生成失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"图表生成失败: {str(e)}")


async def _generate_diagram_code(diagram_type: str, description: str, source_content: str, style: str) -> Dict[str, Any]:
    """
    生成图表代码的核心逻辑
    """
    import time
    from datetime import datetime
    
    # 根据图表类型生成对应的代码
    diagram_templates = {
        "flowchart": {
            "mermaid": """graph TD
    A[开始] --> B{条件判断}
    B -->|是| C[执行操作A]
    B -->|否| D[执行操作B]
    C --> E[结束]
    D --> E""",
            "description": "基于需求生成的业务流程图"
        },
        "sequence": {
            "mermaid": """sequenceDiagram
    participant U as 用户
    participant S as 系统
    participant D as 数据库
    U->>S: 发送请求
    S->>D: 查询数据
    D-->>S: 返回结果
    S-->>U: 响应数据""",
            "description": "基于需求生成的时序图"
        },
        "class": {
            "mermaid": """classDiagram
    class User {
        +String name
        +String email
        +login()
        +logout()
    }
    class System {
        +authenticate()
        +authorize()
    }
    User --> System : uses""",
            "description": "基于需求生成的类图"
        },
        "usecase": {
            "mermaid": """graph LR
    U[用户] --> UC1[登录系统]
    U --> UC2[查看数据]
    U --> UC3[修改信息]
    UC1 --> S[系统]
    UC2 --> S
    UC3 --> S""",
            "description": "基于需求生成的用例图"
        },
        "er": {
            "mermaid": """erDiagram
    USER {
        int id PK
        string name
        string email
    }
    ORDER {
        int id PK
        int user_id FK
        datetime created_at
    }
    USER ||--o{ ORDER : places""",
            "description": "基于需求生成的ER图"
        },
        "architecture": {
            "mermaid": """graph TB
    subgraph "前端层"
        A[Web界面]
        B[移动端]
    end
    subgraph "服务层"
        C[API网关]
        D[业务服务]
    end
    subgraph "数据层"
        E[数据库]
        F[缓存]
    end
    A --> C
    B --> C
    C --> D
    D --> E
    D --> F""",
            "description": "基于需求生成的系统架构图"
        },
        "mindmap": {
            "mermaid": """mindmap
  root((核心功能))
    用户管理
      注册登录
      权限控制
    数据管理
      数据录入
      数据查询
    系统管理
      配置管理
      监控告警""",
            "description": "基于需求生成的思维导图"
        },
        "gantt": {
            "mermaid": """gantt
    title 项目开发计划
    dateFormat  YYYY-MM-DD
    section 需求分析
    需求收集    :done, req1, 2024-01-01, 2024-01-07
    需求分析    :done, req2, after req1, 7d
    section 开发阶段
    前端开发    :active, dev1, 2024-01-15, 14d
    后端开发    :dev2, 2024-01-15, 14d
    section 测试阶段
    单元测试    :test1, after dev1, 7d
    集成测试    :test2, after test1, 7d""",
            "description": "基于需求生成的甘特图"
        }
    }
    
    template = diagram_templates.get(diagram_type, diagram_templates["flowchart"])
    
    # 如果有源内容，可以基于内容进行一些智能调整
    mermaid_code = template["mermaid"]
    if source_content and len(source_content) > 50:
        # 这里可以添加基于内容的智能生成逻辑
        # 暂时使用模板，实际项目中可以集成LLM进行智能生成
        pass
    
    # 根据风格调整
    if style == "colorful":
        mermaid_code += "\n    classDef default fill:#e1f5fe,stroke:#01579b,stroke-width:2px"
    elif style == "professional":
        mermaid_code += "\n    classDef default fill:#f5f5f5,stroke:#333,stroke-width:1px"
    
    return {
        "mermaid_code": mermaid_code,
        "plantuml_code": f"@startuml\n' {template['description']}\n' 这里是PlantUML代码\n@enduml",
        "description": template["description"]
    }


# ==================== 脚本生成 ====================

@router.post("/projects/{project_id}/generate-playwright-script")
async def generate_playwright_script(project_id: int, request: ScriptGenerationRequest):
    """
    生成Playwright脚本
    """
    try:
        logger.info(f"开始生成Playwright脚本，项目ID: {project_id}")
        logger.info(f"请求参数: {request.dict()}")
        
        generator = PlaywrightScriptGenerator(use_pytest=request.use_pytest)
        
        script = generator.generate_script(
            recorded_steps=request.recorded_steps,
            test_case_name=request.test_case_name,
            target_url=request.target_url,
            timeout_seconds=request.timeout_seconds,
            headless=request.headless,
            description=request.description
        )
        
        result = {
            "status": "success",
            "data": {
                "script": script,
                "test_case_name": request.test_case_name,
                "use_pytest": request.use_pytest,
                "step_count": len(request.recorded_steps)
            }
        }
        
        logger.info(f"脚本生成成功，脚本长度: {len(script)}")
        return result
        
    except Exception as e:
        logger.error(f"脚本生成失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"脚本生成失败: {str(e)}")


@router.post("/projects/{project_id}/generate-test-case-template")
async def generate_test_case_template(project_id: int, request: TestCaseGenerationRequest):
    """
    生成测试用例模板
    """
    try:
        generator = TestCaseTemplateGenerator(knowledge_service=None)
        
        template = await generator.generate_test_case_template(
            requirement=request.requirement,
            project_id=str(project_id),
            knowledge_base_id=request.knowledge_base_id,
            similar_cases=request.similar_cases
        )
        
        return {
            "status": "success",
            "data": template
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"测试用例模板生成失败: {str(e)}")


# ==================== 需求检索 ====================

@router.post("/projects/{project_id}/retrieve-requirements")
async def retrieve_requirements(project_id: int, request: RequirementRetrievalRequest):
    """
    检索相关需求文档
    """
    try:
        # 暂时返回模拟数据，等待完整的需求检索服务实现
        result = {
            "query": request.query,
            "enhanced_query": f"增强查询: {request.query}",
            "total_found": 3,
            "filtered_count": 3,
            "requirements": [
                {
                    "content": "模拟需求内容1",
                    "metadata": {"source": "需求文档1"},
                    "requirement_type": "functional",
                    "priority": "high",
                    "status": "active",
                    "stakeholders": ["产品经理", "开发工程师"],
                    "similarity_score": 0.9
                }
            ],
            "analysis": {
                "total_requirements": 3,
                "type_distribution": {"functional": 2, "non-functional": 1},
                "priority_distribution": {"high": 1, "medium": 2},
                "status_distribution": {"active": 3},
                "key_themes": ["用户体验", "性能优化"],
                "recommendations": ["建议优先实现高优先级需求"],
                "summary": "检索到3个相关需求"
            },
            "retrieval_time": "0.1s"
        }
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"需求检索失败: {str(e)}")


@router.post("/projects/{project_id}/context-aware-generation")
async def context_aware_generation(project_id: int, request: ContextAwareGenerationRequest):
    """
    上下文感知生成
    """
    try:
        # 暂时返回模拟数据，等待完整的上下文感知生成服务实现
        result = {
            "generated_content": {
                "title": f"基于'{request.request}'的生成内容",
                "content": "这是一个模拟的上下文感知生成结果。服务正在开发中。",
                "type": request.generation_type
            },
            "generation_method": "template_based",
            "confidence": "medium",
            "context_info": {
                "sources_used": len(request.context_sources),
                "context_quality": "medium",
                "generation_type": request.generation_type
            }
        }
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上下文感知生成失败: {str(e)}")


# ==================== 质量评估 ====================

@router.post("/projects/{project_id}/assess-quality")
async def assess_quality(project_id: int, request: QualityAssessmentRequest):
    """
    评估内容质量
    """
    try:
        # 暂时返回模拟数据，等待完整的质量评估服务实现
        result = {
            "overall_score": 85,
            "max_possible_score": 100,
            "grade": "B",
            "metrics": [
                {
                    "name": "完整性",
                    "score": 90,
                    "max_score": 100,
                    "description": "内容完整性评估",
                    "suggestions": ["建议补充更多细节"],
                    "severity": "low"
                },
                {
                    "name": "准确性",
                    "score": 80,
                    "max_score": 100,
                    "description": "内容准确性评估",
                    "suggestions": ["建议验证关键信息"],
                    "severity": "medium"
                }
            ],
            "summary": "整体质量良好，有改进空间",
            "recommendations": [
                "建议增加更多测试场景",
                "建议完善错误处理逻辑"
            ],
            "assessment_time": "2024-01-15T10:30:00Z",
            "content_type": request.content_type
        }
        
        return {
            "status": "success",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"质量评估失败: {str(e)}")


# ==================== 系统状态和工具 ====================

@router.post("/projects/{project_id}/create-test-requirements")
async def create_test_requirements(project_id: int):
    """
    为项目创建测试需求数据（用于AI图表生成测试）
    """
    try:
        from app.models.aitestrebort.requirements import Requirement
        
        # 检查是否已有需求数据
        existing_count = await Requirement.filter(project_id=project_id).count()
        if existing_count > 0:
            return {
                "status": "success",
                "message": f"项目已有 {existing_count} 个需求，无需创建测试数据",
                "data": {"existing_count": existing_count}
            }
        
        # 创建测试需求数据
        test_requirements = [
            {
                "project_id": project_id,
                "title": "用户管理系统需求",
                "description": "实现用户注册、登录、权限管理、个人信息管理等功能。包括用户认证、角色权限控制、密码安全策略等。",
                "type": "functional",
                "priority": "high",
                "status": "active",
                "stakeholders": ["产品经理", "开发工程师", "测试工程师"],
                "creator_name": "系统管理员"
            },
            {
                "project_id": project_id,
                "title": "订单管理系统需求",
                "description": "实现订单创建、支付处理、订单状态跟踪、退款处理等功能。支持多种支付方式，订单状态实时更新。",
                "type": "functional",
                "priority": "high",
                "status": "active",
                "stakeholders": ["产品经理", "开发工程师"],
                "creator_name": "系统管理员"
            },
            {
                "project_id": project_id,
                "title": "商品管理系统需求",
                "description": "实现商品信息管理、库存管理、价格管理、商品分类等功能。支持批量操作和商品导入导出。",
                "type": "functional",
                "priority": "medium",
                "status": "active",
                "stakeholders": ["产品经理", "运营人员"],
                "creator_name": "系统管理员"
            },
            {
                "project_id": project_id,
                "title": "系统性能需求",
                "description": "系统响应时间不超过2秒，支持1000并发用户，99.9%可用性，数据备份和恢复机制。",
                "type": "non-functional",
                "priority": "high",
                "status": "active",
                "stakeholders": ["技术架构师", "运维工程师"],
                "creator_name": "系统管理员"
            },
            {
                "project_id": project_id,
                "title": "数据安全需求",
                "description": "用户数据加密存储，敏感信息脱敏处理，访问日志记录，符合数据保护法规要求。",
                "type": "non-functional",
                "priority": "high",
                "status": "active",
                "stakeholders": ["安全工程师", "法务人员"],
                "creator_name": "系统管理员"
            }
        ]
        
        created_requirements = []
        for req_data in test_requirements:
            requirement = await Requirement.create(**req_data)
            created_requirements.append({
                "id": str(requirement.id),
                "title": requirement.title,
                "type": requirement.type,
                "priority": requirement.priority
            })
        
        return {
            "status": "success",
            "message": f"成功创建 {len(created_requirements)} 个测试需求",
            "data": {
                "created_count": len(created_requirements),
                "requirements": created_requirements
            }
        }
        
    except Exception as e:
        logger.error(f"创建测试需求失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建测试需求失败: {str(e)}")


@router.get("/projects/{project_id}/system-capabilities")
async def get_system_capabilities(project_id: int):
    """
    获取系统高级功能能力
    """
    try:
        capabilities = {
            "langgraph_integration": {
                "available": True,
                "features": [
                    "RAG查询",
                    "对话上下文压缩",
                    "知识库增强对话",
                    "状态管理"
                ]
            },
            "agent_orchestration": {
                "available": True,
                "features": [
                    "多步骤智能推理",
                    "工具链集成",
                    "任务分解执行",
                    "状态持久化"
                ]
            },
            "script_generation": {
                "available": True,
                "features": [
                    "Playwright脚本生成",
                    "测试用例模板生成",
                    "多格式支持",
                    "自动化测试集成"
                ]
            },
            "requirement_retrieval": {
                "available": True,
                "features": [
                    "智能需求检索",
                    "需求分类分析",
                    "上下文感知生成",
                    "多维度过滤"
                ]
            },
            "quality_assessment": {
                "available": True,
                "features": [
                    "测试用例质量评估",
                    "多维度质量指标",
                    "改进建议生成",
                    "知识库一致性检查"
                ]
            }
        }
        
        return {
            "status": "success",
            "data": capabilities
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取系统能力失败: {str(e)}")


@router.get("/projects/{project_id}/available-tools")
async def get_available_tools(project_id: int):
    """
    获取可用工具列表
    """
    try:
        # 这里应该根据项目配置返回实际可用的工具
        tools = [
            {
                "name": "knowledge_search",
                "description": "搜索知识库获取相关信息",
                "category": "knowledge",
                "available": True
            },
            {
                "name": "playwright_browser",
                "description": "Playwright浏览器自动化工具",
                "category": "automation",
                "available": True
            },
            {
                "name": "mcp_tools",
                "description": "MCP远程工具集成",
                "category": "integration",
                "available": True
            }
        ]
        
        return {
            "status": "success",
            "data": tools
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取工具列表失败: {str(e)}")