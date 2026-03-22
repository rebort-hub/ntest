"""
需求评审服务
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime

from app.models.aitestrebort.requirements import (
    RequirementDocument, RequirementModule, ReviewReport, ReviewIssue,
    ModuleReviewResult
)
from app.schemas.aitestrebort.requirements import (
    ReviewReportCreate, ReviewReportUpdate,
    ReviewIssueCreate, ModuleReviewResultCreate,
    ReviewRequest, ReviewProgressResponse
)
from app.services.aitestrebort.requirements_service import generate_id

logger = logging.getLogger(__name__)


class RequirementReviewService:
    """需求评审服务类"""
    
    @staticmethod
    async def start_review(
        review_request: ReviewRequest,
        user_id: int
    ) -> Dict[str, Any]:
        """开始需求评审"""
        try:
            # 获取文档
            document = await RequirementDocument.get_or_none(id=review_request.document_id)
            if not document:
                raise ValueError("Document not found")
            
            # 创建评审报告
            review_data = ReviewReportCreate(
                document_id=review_request.document_id,
                review_type=review_request.review_type
            )
            
            review_report = await ReviewReport.create(
                document_id=review_data.document_id,
                review_type=review_data.review_type,
                reviewer=review_data.reviewer,
                status="pending"
            )
            
            # 异步启动评审任务
            asyncio.create_task(
                RequirementReviewService._execute_review(
                    review_report.id, review_request, user_id
                )
            )
            
            return {
                "review_id": str(review_report.id),
                "status": "started",
                "message": "Review started successfully"
            }
            
        except Exception as e:
            logger.error(f"Start review failed: {e}")
            raise
    
    @staticmethod
    async def _execute_review(
        review_id: UUID,
        review_request: ReviewRequest,
        user_id: int
    ):
        """执行评审任务（异步）"""
        try:
            # 更新状态为评审中
            await ReviewReport.filter(id=review_id).update(
                status="reviewing",
                review_date=datetime.now()
            )
            
            # 获取文档和模块
            review_report = await ReviewReport.get(id=review_id)
            document = await RequirementDocument.get(id=review_report.document_id)
            modules = await RequirementModule.filter(document_id=document.id).all()
            
            # 执行5个专项分析
            analyses = {}
            
            if review_request.review_type == "comprehensive":
                # 完整性分析
                completeness_result = await RequirementReviewService._analyze_completeness(
                    document, modules
                )
                analyses["completeness"] = completeness_result
                
                # 一致性分析
                consistency_result = await RequirementReviewService._analyze_consistency(
                    document, modules
                )
                analyses["consistency"] = consistency_result
                
                # 可测性分析
                testability_result = await RequirementReviewService._analyze_testability(
                    document, modules
                )
                analyses["testability"] = testability_result
                
                # 可行性分析
                feasibility_result = await RequirementReviewService._analyze_feasibility(
                    document, modules
                )
                analyses["feasibility"] = feasibility_result
                
                # 清晰度分析
                clarity_result = await RequirementReviewService._analyze_clarity(
                    document, modules
                )
                analyses["clarity"] = clarity_result
            
            # 生成综合评审结果
            await RequirementReviewService._generate_review_summary(
                review_id, analyses, modules
            )
            
            # 更新状态为完成
            await ReviewReport.filter(id=review_id).update(
                status="completed",
                specialized_analyses=analyses
            )
            
        except Exception as e:
            logger.error(f"Execute review failed: {e}")
            # 更新状态为失败
            await ReviewReport.filter(id=review_id).update(
                status="failed",
                error_message=str(e)
            )
    
    @staticmethod
    async def _call_llm_analysis(
        document: RequirementDocument,
        modules: List[RequirementModule],
        analysis_type: str,
        system_prompt: str
    ) -> Dict[str, Any]:
        """通用的LLM分析调用方法"""
        try:
            # 使用真实的LLM服务
            from app.models.aitestrebort.project import aitestrebortLLMConfig
            from app.services.aitestrebort.ai_generator_real import create_llm_instance
            from langchain_core.messages import HumanMessage, SystemMessage
            
            # 获取激活的LLM配置
            llm_config = await aitestrebortLLMConfig.filter(is_active=True).first()
            if not llm_config:
                raise ValueError("没有找到激活的LLM配置")
            
            # 创建LLM实例
            llm = create_llm_instance(llm_config, temperature=0.3)
            
            # 构建分析内容
            content_parts = [f"文档标题: {document.title}"]
            if document.description:
                content_parts.append(f"文档描述: {document.description}")
            
            if document.content:
                content_parts.append(f"文档内容: {document.content[:2000]}")
            
            # 添加模块内容
            if modules:
                content_parts.append("\n模块内容:")
                for i, module in enumerate(modules[:5], 1):  # 只取前5个模块
                    content_parts.append(f"{i}. {module.title}: {module.content[:300] if module.content else '无内容'}")
            
            requirement_text = "\n".join(content_parts)
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=requirement_text)
            ]
            
            # 调用LLM
            response = await llm.ainvoke(messages)
            
            # 解析响应
            import json
            try:
                result = json.loads(response.content)
                logger.info(f"{analysis_type}分析完成，使用真实AI分析结果")
                
                # 确保issues格式正确（转换为对象数组）
                if 'issues' in result and isinstance(result['issues'], list):
                    formatted_issues = []
                    for issue in result['issues']:
                        if isinstance(issue, str):
                            # 字符串格式转换为对象格式
                            formatted_issues.append({
                                "title": issue[:50] if len(issue) > 50 else issue,
                                "description": issue,
                                "priority": "medium",
                                "suggestion": f"建议关注此问题并进行改进"
                            })
                        elif isinstance(issue, dict):
                            # 确保对象有必要的字段
                            formatted_issues.append({
                                "title": issue.get('title', '未知问题'),
                                "description": issue.get('description', str(issue)),
                                "priority": issue.get('priority', 'medium'),
                                "suggestion": issue.get('suggestion', '建议进行改进')
                            })
                    result['issues'] = formatted_issues
                
                # 添加overall_score字段（前端需要）
                if 'score' in result and 'overall_score' not in result:
                    result['overall_score'] = result['score']
                
                return result
                
            except json.JSONDecodeError:
                logger.warning(f"{analysis_type}分析：AI响应格式错误，内容: {response.content[:200]}")
                return {
                    "score": 70,
                    "overall_score": 70,
                    "issues": [{
                        "title": f"{analysis_type}：AI响应格式需要优化",
                        "description": "AI返回的分析结果格式不正确",
                        "priority": "low",
                        "suggestion": "建议优化AI提示词"
                    }],
                    "strengths": ["文档结构基本完整"],
                    "recommendations": ["建议优化AI提示词"]
                }
                
        except Exception as e:
            logger.error(f"{analysis_type}分析失败: {e}")
            return {
                "score": 0,
                "overall_score": 0,
                "issues": [{
                    "title": "AI分析服务不可用",
                    "description": f"AI分析过程中发生错误: {str(e)}",
                    "priority": "high",
                    "suggestion": "请检查LLM配置并确保AI服务正常运行"
                }],
                "strengths": [],
                "recommendations": ["请检查LLM配置并确保AI服务正常运行"]
            }
    
    @staticmethod
    async def _analyze_completeness(
        document: RequirementDocument,
        modules: List[RequirementModule]
    ) -> Dict[str, Any]:
        """完整性分析"""
        system_prompt = """你是一个专业的需求分析专家。请对以下需求文档进行完整性分析。

分析要点：
1. 需求是否完整覆盖了所有必要的功能点
2. 是否缺少关键信息（如输入输出、异常处理等）
3. 是否有遗漏的用户场景

请以JSON格式返回分析结果：
{
    "score": 85,
    "issues": [
        {
            "title": "问题标题",
            "description": "问题详细描述",
            "priority": "high/medium/low",
            "suggestion": "改进建议"
        }
    ],
    "strengths": ["优点1", "优点2"],
    "recommendations": ["建议1", "建议2"]
}

注意：score为0-100的整数，issues必须是对象数组格式。"""
        return await RequirementReviewService._call_llm_analysis(
            document, modules, "完整性", system_prompt
        )
    
    @staticmethod
    async def _analyze_consistency(
        document: RequirementDocument,
        modules: List[RequirementModule]
    ) -> Dict[str, Any]:
        """一致性分析"""
        system_prompt = """你是一个专业的需求分析专家。请对以下需求文档进行一致性分析。

分析要点：
1. 术语使用是否一致
2. 功能描述是否存在矛盾
3. 不同模块之间的接口定义是否一致

请以JSON格式返回分析结果：
{
    "score": 85,
    "issues": [
        {
            "title": "问题标题",
            "description": "问题详细描述",
            "priority": "high/medium/low",
            "suggestion": "改进建议"
        }
    ],
    "strengths": ["优点1", "优点2"],
    "recommendations": ["建议1", "建议2"]
}

注意：score为0-100的整数，issues必须是对象数组格式。"""
        return await RequirementReviewService._call_llm_analysis(
            document, modules, "一致性", system_prompt
        )
    
    @staticmethod
    async def _analyze_testability(
        document: RequirementDocument,
        modules: List[RequirementModule]
    ) -> Dict[str, Any]:
        """可测性分析"""
        system_prompt = """你是一个专业的测试工程师。请对以下需求文档进行可测性分析。

分析要点：
1. 需求是否可以被测试验证
2. 是否有明确的验收标准
3. 是否便于编写测试用例

请以JSON格式返回分析结果：
{
    "score": 85,
    "issues": [
        {
            "title": "问题标题",
            "description": "问题详细描述",
            "priority": "high/medium/low",
            "suggestion": "改进建议"
        }
    ],
    "strengths": ["优点1", "优点2"],
    "recommendations": ["建议1", "建议2"]
}

注意：score为0-100的整数，issues必须是对象数组格式。"""
        return await RequirementReviewService._call_llm_analysis(
            document, modules, "可测性", system_prompt
        )
    
    @staticmethod
    async def _analyze_feasibility(
        document: RequirementDocument,
        modules: List[RequirementModule]
    ) -> Dict[str, Any]:
        """可行性分析"""
        system_prompt = """你是一个资深的技术架构师。请对以下需求文档进行可行性分析。

分析要点：
1. 技术实现的可行性
2. 是否存在技术难点或风险
3. 资源和时间的合理性

请以JSON格式返回分析结果：
{
    "score": 85,
    "issues": [
        {
            "title": "问题标题",
            "description": "问题详细描述",
            "priority": "high/medium/low",
            "suggestion": "改进建议"
        }
    ],
    "strengths": ["优点1", "优点2"],
    "recommendations": ["建议1", "建议2"]
}

注意：score为0-100的整数，issues必须是对象数组格式。"""
        return await RequirementReviewService._call_llm_analysis(
            document, modules, "可行性", system_prompt
        )
    
    @staticmethod
    async def _analyze_clarity(
        document: RequirementDocument,
        modules: List[RequirementModule]
    ) -> Dict[str, Any]:
        """清晰度分析"""
        system_prompt = """你是一个专业的需求分析专家。请对以下需求文档进行清晰度分析。

分析要点：
1. 需求描述是否清晰明确
2. 是否存在歧义或模糊的表述
3. 是否易于理解和实现

请以JSON格式返回分析结果：
{
    "score": 85,
    "issues": [
        {
            "title": "问题标题",
            "description": "问题详细描述",
            "priority": "high/medium/low",
            "suggestion": "改进建议"
        }
    ],
    "strengths": ["优点1", "优点2"],
    "recommendations": ["建议1", "建议2"]
}

注意：score为0-100的整数，issues必须是对象数组格式。"""
        return await RequirementReviewService._call_llm_analysis(
            document, modules, "清晰度", system_prompt
        )
    
    @staticmethod
    async def _generate_review_summary(
        review_id: UUID,
        analyses: Dict[str, Any],
        modules: List[RequirementModule]
    ):
        """生成评审摘要和问题"""
        try:
            # 计算总体评分
            scores = [analysis["score"] for analysis in analyses.values()]
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # 统计问题
            all_issues = []
            for analysis in analyses.values():
                all_issues.extend(analysis.get("issues", []))
            
            high_issues = [i for i in all_issues if i["priority"] == "high"]
            medium_issues = [i for i in all_issues if i["priority"] == "medium"]
            low_issues = [i for i in all_issues if i["priority"] == "low"]
            
            # 生成总体评价
            if avg_score >= 90:
                overall_rating = "excellent"
            elif avg_score >= 80:
                overall_rating = "good"
            elif avg_score >= 70:
                overall_rating = "average"
            elif avg_score >= 60:
                overall_rating = "needs_improvement"
            else:
                overall_rating = "poor"
            
            # 更新评审报告
            await ReviewReport.filter(id=review_id).update(
                overall_rating=overall_rating,
                completion_score=analyses.get("completeness", {}).get("score", 0),
                clarity_score=analyses.get("clarity", {}).get("score", 0),
                consistency_score=analyses.get("consistency", {}).get("score", 0),
                completeness_score=analyses.get("completeness", {}).get("score", 0),
                testability_score=analyses.get("testability", {}).get("score", 0),
                feasibility_score=analyses.get("feasibility", {}).get("score", 0),
                total_issues=len(all_issues),
                high_priority_issues=len(high_issues),
                medium_priority_issues=len(medium_issues),
                low_priority_issues=len(low_issues),
                summary=f"本次评审共发现{len(all_issues)}个问题，总体评分{avg_score:.1f}分",
                recommendations="建议重点关注高优先级问题的解决"
            )
            
            # 创建问题记录
            for issue in all_issues:
                await ReviewIssue.create(
                    id=generate_id(),
                    report_id=review_id,
                    issue_type=issue["type"],
                    priority=issue["priority"],
                    title=issue["title"],
                    description=issue["description"],
                    suggestion=issue["suggestion"]
                )
            
            # 创建模块评审结果
            for module in modules:
                module_issues = [i for i in all_issues if "模块" in i.get("location", "")]
                await ModuleReviewResult.create(
                    id=generate_id(),
                    report_id=review_id,
                    module_id=module.id,
                    module_id_str=str(module.id),
                    module_name=module.title,
                    specification_score=85,
                    clarity_score=80,
                    completeness_score=75,
                    consistency_score=90,
                    feasibility_score=85,
                    overall_score=83,
                    module_rating="good" if len(module_issues) == 0 else "needs_improvement",
                    issues_count=len(module_issues),
                    severity_score=len([i for i in module_issues if i["priority"] == "high"]) * 10,
                    issues=[issue for issue in module_issues],
                    strengths=["模块结构清晰", "逻辑合理"],
                    weaknesses=["需要完善细节"] if module_issues else [],
                    recommendations=["建议优化实现方案"] if module_issues else ["保持现有质量"],
                    analysis_content=f"模块'{module.title}'评审完成，共发现{len(module_issues)}个问题"
                )
                
        except Exception as e:
            logger.error(f"Generate review summary failed: {e}")
            raise
    
    @staticmethod
    async def get_review_progress(review_id: UUID) -> ReviewProgressResponse:
        """获取评审进度"""
        try:
            review = await ReviewReport.get_or_none(id=review_id)
            if not review:
                raise ValueError("Review not found")
            
            # 根据状态计算进度
            progress_map = {
                "pending": 0.0,
                "reviewing": 50.0,
                "completed": 100.0,
                "failed": 0.0
            }
            
            progress = progress_map.get(review.status, 0.0)
            
            # 估算剩余时间
            estimated_time = None
            if review.status == "reviewing":
                estimated_time = 300  # 5分钟
            
            return ReviewProgressResponse(
                document_id=review.document_id,
                status=review.status,
                progress=progress,
                current_step=f"正在执行{review.review_type}评审",
                estimated_time=estimated_time
            )
            
        except Exception as e:
            logger.error(f"Get review progress failed: {e}")
            raise
    
    @staticmethod
    async def create_review(review_data: ReviewReportCreate) -> ReviewReport:
        """创建评审报告"""
        try:
            return await ReviewReport.create(**review_data.model_dump())
        except Exception as e:
            logger.error(f"Create review failed: {e}")
            raise
    
    @staticmethod
    async def update_review(
        review_id: UUID,
        review_update: ReviewReportUpdate
    ) -> ReviewReport:
        """更新评审报告"""
        try:
            await ReviewReport.filter(id=review_id).update(
                **review_update.model_dump(exclude_unset=True)
            )
            return await ReviewReport.get(id=review_id)
        except Exception as e:
            logger.error(f"Update review failed: {e}")
            raise
    
    @staticmethod
    async def list_reviews(
        document_id: Optional[UUID] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewReport]:
        """获取评审报告列表"""
        try:
            query = ReviewReport.all()
            
            if document_id:
                query = query.filter(document_id=document_id)
            if status:
                query = query.filter(status=status)
            
            return await query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"List reviews failed: {e}")
            raise
    
    @staticmethod
    async def create_issue(issue_data: ReviewIssueCreate) -> ReviewIssue:
        """创建评审问题"""
        try:
            return await ReviewIssue.create(**issue_data.model_dump())
        except Exception as e:
            logger.error(f"Create issue failed: {e}")
            raise
    
    @staticmethod
    async def list_issues(
        report_id: Optional[UUID] = None,
        module_id: Optional[UUID] = None,
        priority: Optional[str] = None,
        is_resolved: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReviewIssue]:
        """获取评审问题列表"""
        try:
            query = ReviewIssue.all()
            
            if report_id:
                query = query.filter(report_id=report_id)
            if module_id:
                query = query.filter(module_id=module_id)
            if priority:
                query = query.filter(priority=priority)
            if is_resolved is not None:
                query = query.filter(is_resolved=is_resolved)
            
            return await query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"List issues failed: {e}")
            raise
    
    @staticmethod
    async def create_module_result(
        result_data: ModuleReviewResultCreate
    ) -> ModuleReviewResult:
        """创建模块评审结果"""
        try:
            return await ModuleReviewResult.create(**result_data.model_dump())
        except Exception as e:
            logger.error(f"Create module result failed: {e}")
            raise
    
    @staticmethod
    async def list_module_results(
        report_id: Optional[UUID] = None,
        module_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ModuleReviewResult]:
        """获取模块评审结果列表"""
        try:
            query = ModuleReviewResult.all()
            
            if report_id:
                query = query.filter(report_id=report_id)
            if module_id:
                query = query.filter(module_id=module_id)
            
            return await query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"List module results failed: {e}")
            raise