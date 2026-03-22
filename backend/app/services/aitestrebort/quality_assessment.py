"""
生成质量评估服务

基于知识库内容对生成的测试用例、需求文档等进行质量检查和评估
"""
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QualityMetric:
    """质量指标"""
    name: str
    score: float  # 0-100
    max_score: float
    description: str
    suggestions: List[str]
    severity: str  # 'low', 'medium', 'high', 'critical'


@dataclass
class QualityAssessmentResult:
    """质量评估结果"""
    overall_score: float
    max_possible_score: float
    grade: str  # A, B, C, D, F
    metrics: List[QualityMetric]
    summary: str
    recommendations: List[str]
    assessment_time: str
    content_type: str


class TestCaseQualityAssessor:
    """
    测试用例质量评估器
    """
    
    def __init__(self, knowledge_service=None):
        self.knowledge_service = knowledge_service
    
    async def assess_test_case(
        self,
        test_case: Dict[str, Any],
        project_id: str,
        knowledge_base_id: str = None,
        reference_requirements: List[Dict[str, Any]] = None
    ) -> QualityAssessmentResult:
        """
        评估测试用例质量
        
        Args:
            test_case: 测试用例数据
            project_id: 项目ID
            knowledge_base_id: 知识库ID
            reference_requirements: 参考需求文档
            
        Returns:
            质量评估结果
        """
        try:
            metrics = []
            
            # 1. 基础结构完整性检查
            structure_metric = self._assess_structure_completeness(test_case)
            metrics.append(structure_metric)
            
            # 2. 测试步骤质量检查
            steps_metric = self._assess_test_steps_quality(test_case)
            metrics.append(steps_metric)
            
            # 3. 预期结果明确性检查
            results_metric = self._assess_expected_results_clarity(test_case)
            metrics.append(results_metric)
            
            # 4. 可执行性检查
            executability_metric = self._assess_executability(test_case)
            metrics.append(executability_metric)
            
            # 5. 需求覆盖度检查
            if reference_requirements:
                coverage_metric = self._assess_requirement_coverage(
                    test_case, reference_requirements
                )
                metrics.append(coverage_metric)
            
            # 6. 知识库一致性检查
            if knowledge_base_id and self.knowledge_service:
                consistency_metric = await self._assess_knowledge_consistency(
                    test_case, knowledge_base_id
                )
                metrics.append(consistency_metric)
            
            # 计算总分和等级
            total_score = sum(m.score for m in metrics)
            max_score = sum(m.max_score for m in metrics)
            overall_score = (total_score / max_score * 100) if max_score > 0 else 0
            
            grade = self._calculate_grade(overall_score)
            
            # 生成总结和建议
            summary = self._generate_test_case_summary(overall_score, metrics)
            recommendations = self._generate_test_case_recommendations(metrics)
            
            return QualityAssessmentResult(
                overall_score=overall_score,
                max_possible_score=100.0,
                grade=grade,
                metrics=metrics,
                summary=summary,
                recommendations=recommendations,
                assessment_time=datetime.now().isoformat(),
                content_type='test_case'
            )
            
        except Exception as e:
            logger.error(f"测试用例质量评估失败: {e}")
            return QualityAssessmentResult(
                overall_score=0.0,
                max_possible_score=100.0,
                grade='F',
                metrics=[],
                summary=f'评估失败: {str(e)}',
                recommendations=['请检查测试用例格式和内容'],
                assessment_time=datetime.now().isoformat(),
                content_type='test_case'
            )
    
    def _assess_structure_completeness(self, test_case: Dict[str, Any]) -> QualityMetric:
        """
        评估测试用例结构完整性
        """
        required_fields = {
            'name': '测试用例名称',
            'description': '测试用例描述',
            'test_steps': '测试步骤',
            'expected_results': '预期结果'
        }
        
        optional_fields = {
            'preconditions': '前置条件',
            'priority': '优先级',
            'type': '测试类型',
            'tags': '标签'
        }
        
        score = 0
        max_score = 20
        suggestions = []
        
        # 检查必填字段
        missing_required = []
        for field, desc in required_fields.items():
            if field not in test_case or not test_case[field]:
                missing_required.append(desc)
            else:
                score += 4  # 每个必填字段4分
        
        # 检查可选字段
        present_optional = 0
        for field in optional_fields:
            if field in test_case and test_case[field]:
                present_optional += 1
        
        score += min(present_optional, 4)  # 可选字段最多4分
        
        if missing_required:
            suggestions.append(f"缺少必填字段: {', '.join(missing_required)}")
        
        if present_optional < 2:
            suggestions.append("建议添加更多可选字段以提高测试用例完整性")
        
        severity = 'critical' if len(missing_required) > 2 else 'medium' if missing_required else 'low'
        
        return QualityMetric(
            name='结构完整性',
            score=score,
            max_score=max_score,
            description=f'测试用例结构完整性评估，缺少{len(missing_required)}个必填字段',
            suggestions=suggestions,
            severity=severity
        )
    
    def _assess_test_steps_quality(self, test_case: Dict[str, Any]) -> QualityMetric:
        """
        评估测试步骤质量
        """
        steps = test_case.get('test_steps', [])
        score = 0
        max_score = 25
        suggestions = []
        
        if not steps:
            return QualityMetric(
                name='测试步骤质量',
                score=0,
                max_score=max_score,
                description='缺少测试步骤',
                suggestions=['必须提供详细的测试步骤'],
                severity='critical'
            )
        
        # 检查步骤数量
        step_count = len(steps)
        if step_count >= 3:
            score += 5
        elif step_count >= 1:
            score += 3
        else:
            suggestions.append('测试步骤过少，建议至少包含3个步骤')
        
        # 检查步骤详细程度
        detailed_steps = 0
        for step in steps:
            if isinstance(step, dict):
                action = step.get('action', '')
                expected = step.get('expected_result', '')
                
                if len(action) > 10:  # 操作描述足够详细
                    detailed_steps += 1
                    score += 2
                
                if len(expected) > 5:  # 有预期结果
                    score += 2
            elif isinstance(step, str) and len(step) > 10:
                detailed_steps += 1
                score += 2
        
        # 检查步骤逻辑性
        if self._check_steps_logical_flow(steps):
            score += 5
        else:
            suggestions.append('测试步骤逻辑流程不够清晰')
        
        # 检查可操作性
        actionable_steps = self._count_actionable_steps(steps)
        if actionable_steps >= len(steps) * 0.8:
            score += 5
        else:
            suggestions.append('部分测试步骤缺乏明确的操作指导')
        
        if detailed_steps < len(steps) * 0.5:
            suggestions.append('建议为每个步骤提供更详细的描述')
        
        severity = 'high' if score < max_score * 0.4 else 'medium' if score < max_score * 0.7 else 'low'
        
        return QualityMetric(
            name='测试步骤质量',
            score=min(score, max_score),
            max_score=max_score,
            description=f'测试步骤质量评估，共{step_count}个步骤，{detailed_steps}个详细步骤',
            suggestions=suggestions,
            severity=severity
        )
    
    def _assess_expected_results_clarity(self, test_case: Dict[str, Any]) -> QualityMetric:
        """
        评估预期结果明确性
        """
        expected_results = test_case.get('expected_results', [])
        steps = test_case.get('test_steps', [])
        
        score = 0
        max_score = 20
        suggestions = []
        
        # 检查是否有预期结果
        if not expected_results and not any(
            isinstance(step, dict) and step.get('expected_result') 
            for step in steps
        ):
            return QualityMetric(
                name='预期结果明确性',
                score=0,
                max_score=max_score,
                description='缺少预期结果',
                suggestions=['必须为每个测试步骤定义明确的预期结果'],
                severity='critical'
            )
        
        # 检查预期结果的详细程度
        clear_results = 0
        total_results = len(expected_results)
        
        # 检查步骤中的预期结果
        for step in steps:
            if isinstance(step, dict) and step.get('expected_result'):
                total_results += 1
                expected = step.get('expected_result', '')
                if self._is_clear_expected_result(expected):
                    clear_results += 1
        
        # 检查独立的预期结果列表
        for result in expected_results:
            if isinstance(result, str) and self._is_clear_expected_result(result):
                clear_results += 1
        
        if total_results > 0:
            clarity_ratio = clear_results / total_results
            score = int(max_score * clarity_ratio)
        
        if clarity_ratio < 0.5:
            suggestions.append('预期结果描述不够明确，建议使用具体、可验证的表述')
        
        if clarity_ratio < 0.8:
            suggestions.append('建议为每个操作步骤都定义明确的预期结果')
        
        severity = 'high' if clarity_ratio < 0.3 else 'medium' if clarity_ratio < 0.7 else 'low'
        
        return QualityMetric(
            name='预期结果明确性',
            score=score,
            max_score=max_score,
            description=f'预期结果明确性评估，{clear_results}/{total_results}个结果明确',
            suggestions=suggestions,
            severity=severity
        )
    
    def _assess_executability(self, test_case: Dict[str, Any]) -> QualityMetric:
        """
        评估测试用例可执行性
        """
        score = 0
        max_score = 15
        suggestions = []
        
        # 检查前置条件
        preconditions = test_case.get('preconditions', [])
        if preconditions:
            score += 3
        else:
            suggestions.append('建议添加前置条件以确保测试环境准备充分')
        
        # 检查测试数据
        test_data = test_case.get('test_data', {})
        if test_data:
            score += 3
        
        # 检查步骤的可操作性
        steps = test_case.get('test_steps', [])
        actionable_count = self._count_actionable_steps(steps)
        if steps and actionable_count >= len(steps) * 0.8:
            score += 5
        elif actionable_count >= len(steps) * 0.5:
            score += 3
            suggestions.append('部分测试步骤需要更明确的操作指导')
        else:
            suggestions.append('测试步骤缺乏明确的操作指导，影响执行效率')
        
        # 检查环境依赖
        if self._has_environment_info(test_case):
            score += 2
        
        # 检查时间估算
        if test_case.get('estimated_time'):
            score += 2
        else:
            suggestions.append('建议添加执行时间估算')
        
        severity = 'medium' if score < max_score * 0.6 else 'low'
        
        return QualityMetric(
            name='可执行性',
            score=score,
            max_score=max_score,
            description=f'测试用例可执行性评估，{actionable_count}/{len(steps)}个步骤可操作',
            suggestions=suggestions,
            severity=severity
        )
    
    def _assess_requirement_coverage(
        self,
        test_case: Dict[str, Any],
        requirements: List[Dict[str, Any]]
    ) -> QualityMetric:
        """
        评估需求覆盖度
        """
        score = 0
        max_score = 20
        suggestions = []
        
        if not requirements:
            return QualityMetric(
                name='需求覆盖度',
                score=max_score // 2,  # 没有参考需求时给中等分数
                max_score=max_score,
                description='无参考需求文档',
                suggestions=[],
                severity='low'
            )
        
        # 检查测试用例是否覆盖了需求要点
        test_content = self._extract_test_case_content(test_case)
        covered_requirements = 0
        
        for req in requirements:
            req_content = req.get('content', '')
            if self._check_requirement_coverage(test_content, req_content):
                covered_requirements += 1
        
        coverage_ratio = covered_requirements / len(requirements)
        score = int(max_score * coverage_ratio)
        
        if coverage_ratio < 0.5:
            suggestions.append('测试用例未充分覆盖相关需求，建议增加测试场景')
        
        if coverage_ratio < 0.8:
            suggestions.append('建议检查是否遗漏了重要的需求验证点')
        
        severity = 'high' if coverage_ratio < 0.3 else 'medium' if coverage_ratio < 0.7 else 'low'
        
        return QualityMetric(
            name='需求覆盖度',
            score=score,
            max_score=max_score,
            description=f'需求覆盖度评估，覆盖{covered_requirements}/{len(requirements)}个需求',
            suggestions=suggestions,
            severity=severity
        )
    
    async def _assess_knowledge_consistency(
        self,
        test_case: Dict[str, Any],
        knowledge_base_id: str
    ) -> QualityMetric:
        """
        评估与知识库的一致性
        """
        score = 0
        max_score = 15
        suggestions = []
        
        try:
            # 提取测试用例关键信息
            test_content = self._extract_test_case_content(test_case)
            
            # 在知识库中搜索相关内容
            kb_service = self.knowledge_service(knowledge_base_id)
            await kb_service.initialize()
            
            search_results = await kb_service.search_knowledge(
                test_content[:200], top_k=3
            )
            
            if search_results:
                # 检查一致性
                consistency_score = self._calculate_consistency_score(
                    test_case, search_results
                )
                score = int(max_score * consistency_score)
                
                if consistency_score < 0.5:
                    suggestions.append('测试用例与知识库内容存在不一致，建议核实相关信息')
                
                if consistency_score < 0.8:
                    suggestions.append('建议参考知识库中的最佳实践和标准')
            else:
                score = max_score // 2  # 没有相关内容时给中等分数
                suggestions.append('知识库中未找到相关参考内容')
            
        except Exception as e:
            logger.error(f"知识库一致性检查失败: {e}")
            score = max_score // 2
            suggestions.append('知识库一致性检查失败，请手动验证')
        
        severity = 'medium' if score < max_score * 0.6 else 'low'
        
        return QualityMetric(
            name='知识库一致性',
            score=score,
            max_score=max_score,
            description='与项目知识库内容的一致性评估',
            suggestions=suggestions,
            severity=severity
        )
    
    # 辅助方法
    def _check_steps_logical_flow(self, steps: List) -> bool:
        """检查步骤逻辑流程"""
        if len(steps) < 2:
            return True
        
        # 简单的逻辑检查：是否有明显的顺序关系
        setup_keywords = ['打开', '登录', '进入', '启动', '初始化']
        action_keywords = ['点击', '输入', '选择', '填写', '执行']
        verify_keywords = ['验证', '检查', '确认', '断言']
        
        has_setup = any(
            any(keyword in str(step).lower() for keyword in setup_keywords)
            for step in steps[:2]
        )
        
        has_action = any(
            any(keyword in str(step).lower() for keyword in action_keywords)
            for step in steps
        )
        
        has_verify = any(
            any(keyword in str(step).lower() for keyword in verify_keywords)
            for step in steps[-2:]
        )
        
        return has_setup and has_action
    
    def _count_actionable_steps(self, steps: List) -> int:
        """统计可操作的步骤数量"""
        actionable_keywords = [
            '点击', '输入', '选择', '填写', '提交', '打开', '关闭',
            '滚动', '拖拽', '双击', '右键', '按下', '释放'
        ]
        
        count = 0
        for step in steps:
            step_text = str(step).lower()
            if any(keyword in step_text for keyword in actionable_keywords):
                count += 1
        
        return count
    
    def _is_clear_expected_result(self, result: str) -> bool:
        """判断预期结果是否明确"""
        if len(result) < 5:
            return False
        
        # 检查是否包含具体的验证点
        clear_indicators = [
            '显示', '出现', '消失', '变为', '等于', '包含',
            '成功', '失败', '错误', '正确', '跳转', '刷新'
        ]
        
        return any(indicator in result for indicator in clear_indicators)
    
    def _has_environment_info(self, test_case: Dict[str, Any]) -> bool:
        """检查是否包含环境信息"""
        env_fields = ['environment', 'browser', 'platform', 'version']
        return any(field in test_case for field in env_fields)
    
    def _extract_test_case_content(self, test_case: Dict[str, Any]) -> str:
        """提取测试用例的文本内容"""
        content_parts = []
        
        if test_case.get('name'):
            content_parts.append(test_case['name'])
        
        if test_case.get('description'):
            content_parts.append(test_case['description'])
        
        # 提取步骤内容
        steps = test_case.get('test_steps', [])
        for step in steps:
            if isinstance(step, dict):
                if step.get('action'):
                    content_parts.append(step['action'])
                if step.get('expected_result'):
                    content_parts.append(step['expected_result'])
            else:
                content_parts.append(str(step))
        
        return ' '.join(content_parts)
    
    def _check_requirement_coverage(self, test_content: str, req_content: str) -> bool:
        """检查测试用例是否覆盖了需求"""
        # 提取需求中的关键词
        req_keywords = self._extract_keywords(req_content)
        test_keywords = self._extract_keywords(test_content)
        
        # 计算关键词重叠度
        if not req_keywords:
            return False
        
        overlap = len(set(req_keywords) & set(test_keywords))
        coverage_ratio = overlap / len(req_keywords)
        
        return coverage_ratio >= 0.3  # 30%的关键词重叠认为有覆盖
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取文本关键词"""
        # 简单的关键词提取
        words = re.findall(r'\b\w{2,}\b', text.lower())
        
        # 过滤停用词
        stop_words = {'的', '是', '在', '有', '和', '或', '但', '如果', '那么', '这个', '那个'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return list(set(keywords))  # 去重
    
    def _calculate_consistency_score(
        self,
        test_case: Dict[str, Any],
        search_results: List[Dict[str, Any]]
    ) -> float:
        """计算与知识库内容的一致性分数"""
        test_content = self._extract_test_case_content(test_case)
        test_keywords = set(self._extract_keywords(test_content))
        
        if not test_keywords:
            return 0.5
        
        total_similarity = 0
        for result in search_results:
            kb_content = result.get('content', '')
            kb_keywords = set(self._extract_keywords(kb_content))
            
            if kb_keywords:
                similarity = len(test_keywords & kb_keywords) / len(test_keywords | kb_keywords)
                total_similarity += similarity
        
        return total_similarity / len(search_results) if search_results else 0.5
    
    def _calculate_grade(self, score: float) -> str:
        """计算等级"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _generate_test_case_summary(self, score: float, metrics: List[QualityMetric]) -> str:
        """生成测试用例质量总结"""
        grade = self._calculate_grade(score)
        
        critical_issues = [m for m in metrics if m.severity == 'critical']
        high_issues = [m for m in metrics if m.severity == 'high']
        
        if critical_issues:
            return f"测试用例质量等级: {grade} ({score:.1f}分)。存在{len(critical_issues)}个严重问题需要立即修复。"
        elif high_issues:
            return f"测试用例质量等级: {grade} ({score:.1f}分)。存在{len(high_issues)}个重要问题建议优化。"
        else:
            return f"测试用例质量等级: {grade} ({score:.1f}分)。整体质量良好。"
    
    def _generate_test_case_recommendations(self, metrics: List[QualityMetric]) -> List[str]:
        """生成测试用例改进建议"""
        recommendations = []
        
        # 收集所有建议
        for metric in metrics:
            recommendations.extend(metric.suggestions)
        
        # 按严重程度排序建议
        critical_suggestions = []
        other_suggestions = []
        
        for metric in metrics:
            if metric.severity in ['critical', 'high']:
                critical_suggestions.extend(metric.suggestions)
            else:
                other_suggestions.extend(metric.suggestions)
        
        # 去重并排序
        all_suggestions = list(set(critical_suggestions + other_suggestions))
        
        # 添加通用建议
        if any(m.severity == 'critical' for m in metrics):
            all_suggestions.insert(0, '优先解决标记为严重的质量问题')
        
        all_suggestions.append('建议在实际执行前进行同行评审')
        
        return all_suggestions[:10]  # 最多返回10个建议


class QualityAssessmentService:
    """
    质量评估服务主入口
    """
    
    def __init__(self, knowledge_service=None):
        self.knowledge_service = knowledge_service
        self.test_case_assessor = TestCaseQualityAssessor(knowledge_service)
    
    async def assess_content_quality(
        self,
        content: Dict[str, Any],
        content_type: str,
        project_id: str,
        knowledge_base_id: str = None,
        reference_data: List[Dict[str, Any]] = None
    ) -> QualityAssessmentResult:
        """
        评估内容质量
        
        Args:
            content: 要评估的内容
            content_type: 内容类型 (test_case, requirement, documentation)
            project_id: 项目ID
            knowledge_base_id: 知识库ID
            reference_data: 参考数据
            
        Returns:
            质量评估结果
        """
        if content_type == 'test_case':
            return await self.test_case_assessor.assess_test_case(
                content, project_id, knowledge_base_id, reference_data
            )
        else:
            # 其他类型的评估可以在这里扩展
            return QualityAssessmentResult(
                overall_score=0.0,
                max_possible_score=100.0,
                grade='F',
                metrics=[],
                summary=f'不支持的内容类型: {content_type}',
                recommendations=[],
                assessment_time=datetime.now().isoformat(),
                content_type=content_type
            )