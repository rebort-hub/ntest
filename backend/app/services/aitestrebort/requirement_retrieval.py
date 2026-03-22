"""
需求文档检索服务
从知识库中智能检索相关需求文档，支持上下文感知生成
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RequirementRetrievalService:
    """
    需求文档检索服务
    
    提供智能的需求文档检索和分析功能
    """
    
    def __init__(self, knowledge_service=None):
        self.knowledge_service = knowledge_service
    
    async def retrieve_requirements(
        self,
        query: str,
        project_id: str,
        knowledge_base_id: str,
        requirement_types: List[str] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        检索相关需求文档
        
        Args:
            query: 查询内容
            project_id: 项目ID
            knowledge_base_id: 知识库ID
            requirement_types: 需求类型过滤
            top_k: 返回结果数量
            
        Returns:
            检索结果和分析
        """
        try:
            if not self.knowledge_service:
                return {
                    'error': '知识库服务未初始化',
                    'requirements': [],
                    'analysis': {}
                }
            
            # 1. 构建增强查询
            enhanced_query = self._enhance_query(query, requirement_types)
            
            # 2. 执行知识库检索
            kb_service = self.knowledge_service(knowledge_base_id)
            await kb_service.initialize()
            
            search_results = await kb_service.search_knowledge(
                enhanced_query, top_k=top_k * 2  # 多检索一些，后续过滤
            )
            
            # 3. 过滤和分类需求文档
            filtered_requirements = self._filter_requirements(
                search_results, requirement_types, top_k
            )
            
            # 4. 分析需求文档
            analysis = self._analyze_requirements(filtered_requirements, query)
            
            # 5. 生成检索报告
            retrieval_report = {
                'query': query,
                'enhanced_query': enhanced_query,
                'total_found': len(search_results),
                'filtered_count': len(filtered_requirements),
                'requirements': filtered_requirements,
                'analysis': analysis,
                'retrieval_time': datetime.now().isoformat(),
                'project_id': project_id,
                'knowledge_base_id': knowledge_base_id
            }
            
            return retrieval_report
            
        except Exception as e:
            logger.error(f"需求检索失败: {e}")
            return {
                'error': str(e),
                'requirements': [],
                'analysis': {}
            }
    
    def _enhance_query(self, query: str, requirement_types: List[str] = None) -> str:
        """
        增强查询语句，提高检索准确性
        """
        enhanced_parts = [query]
        
        # 添加需求相关关键词
        requirement_keywords = ['需求', '功能', '特性', '规格', '要求']
        enhanced_parts.extend(requirement_keywords)
        
        # 添加类型过滤
        if requirement_types:
            enhanced_parts.extend(requirement_types)
        
        # 添加常见需求文档关键词
        doc_keywords = ['用户故事', '功能点', '业务流程', '接口规范']
        enhanced_parts.extend(doc_keywords)
        
        return ' '.join(enhanced_parts)
    
    def _filter_requirements(
        self,
        search_results: List[Dict[str, Any]],
        requirement_types: List[str] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        过滤和分类需求文档
        """
        filtered_results = []
        
        for result in search_results:
            content = result.get('content', '')
            metadata = result.get('metadata', {})
            
            # 检查是否是需求文档
            if self._is_requirement_document(content, metadata):
                # 分类需求类型
                req_type = self._classify_requirement_type(content)
                
                # 类型过滤
                if requirement_types and req_type not in requirement_types:
                    continue
                
                # 增强结果信息
                enhanced_result = {
                    **result,
                    'requirement_type': req_type,
                    'priority': self._extract_priority(content),
                    'status': self._extract_status(content),
                    'stakeholders': self._extract_stakeholders(content)
                }
                
                filtered_results.append(enhanced_result)
        
        # 按相似度排序并限制数量
        filtered_results.sort(
            key=lambda x: x.get('similarity_score', 0), 
            reverse=True
        )
        
        return filtered_results[:top_k]
    
    def _is_requirement_document(self, content: str, metadata: Dict[str, Any]) -> bool:
        """
        判断是否是需求文档
        """
        # 检查内容关键词
        requirement_indicators = [
            '需求', '功能', '特性', '用户故事', '业务流程',
            '接口规范', '技术规格', '产品规格', '系统要求'
        ]
        
        content_lower = content.lower()
        has_requirement_keywords = any(
            keyword in content_lower for keyword in requirement_indicators
        )
        
        # 检查文档标题或路径
        source = metadata.get('source', '').lower()
        title_indicators = ['requirement', 'spec', 'feature', '需求', '规格']
        has_title_indicators = any(
            indicator in source for indicator in title_indicators
        )
        
        return has_requirement_keywords or has_title_indicators
    
    def _classify_requirement_type(self, content: str) -> str:
        """
        分类需求类型
        """
        content_lower = content.lower()
        
        # 功能需求
        if any(keyword in content_lower for keyword in ['功能', '特性', '用户故事', 'feature']):
            return 'functional'
        
        # 性能需求
        if any(keyword in content_lower for keyword in ['性能', '响应时间', '吞吐量', 'performance']):
            return 'performance'
        
        # 安全需求
        if any(keyword in content_lower for keyword in ['安全', '权限', '认证', 'security']):
            return 'security'
        
        # 接口需求
        if any(keyword in content_lower for keyword in ['接口', 'api', '集成', 'interface']):
            return 'interface'
        
        # 用户体验需求
        if any(keyword in content_lower for keyword in ['用户体验', 'ui', 'ux', '界面']):
            return 'usability'
        
        return 'general'
    
    def _extract_priority(self, content: str) -> str:
        """
        提取需求优先级
        """
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['高优先级', 'high priority', '紧急', 'critical']):
            return 'high'
        elif any(keyword in content_lower for keyword in ['低优先级', 'low priority', '可选', 'optional']):
            return 'low'
        else:
            return 'medium'
    
    def _extract_status(self, content: str) -> str:
        """
        提取需求状态
        """
        content_lower = content.lower()
        
        if any(keyword in content_lower for keyword in ['已完成', 'completed', 'done']):
            return 'completed'
        elif any(keyword in content_lower for keyword in ['进行中', 'in progress', 'developing']):
            return 'in_progress'
        elif any(keyword in content_lower for keyword in ['待开发', 'pending', 'todo']):
            return 'pending'
        else:
            return 'unknown'
    
    def _extract_stakeholders(self, content: str) -> List[str]:
        """
        提取相关干系人
        """
        stakeholders = []
        
        # 常见角色关键词
        role_patterns = [
            ('产品经理', ['产品经理', 'pm', 'product manager']),
            ('开发人员', ['开发', '程序员', 'developer', 'engineer']),
            ('测试人员', ['测试', 'tester', 'qa']),
            ('用户', ['用户', 'user', '客户', 'customer']),
            ('运维', ['运维', 'ops', 'devops'])
        ]
        
        content_lower = content.lower()
        for role, keywords in role_patterns:
            if any(keyword in content_lower for keyword in keywords):
                stakeholders.append(role)
        
        return stakeholders
    
    def _analyze_requirements(
        self,
        requirements: List[Dict[str, Any]],
        original_query: str
    ) -> Dict[str, Any]:
        """
        分析需求文档，生成洞察
        """
        if not requirements:
            return {
                'summary': '未找到相关需求文档',
                'recommendations': []
            }
        
        # 统计分析
        type_distribution = {}
        priority_distribution = {}
        status_distribution = {}
        
        for req in requirements:
            req_type = req.get('requirement_type', 'unknown')
            priority = req.get('priority', 'unknown')
            status = req.get('status', 'unknown')
            
            type_distribution[req_type] = type_distribution.get(req_type, 0) + 1
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
            status_distribution[status] = status_distribution.get(status, 0) + 1
        
        # 生成建议
        recommendations = self._generate_recommendations(
            requirements, original_query, type_distribution
        )
        
        # 识别关键主题
        key_themes = self._extract_key_themes(requirements)
        
        return {
            'total_requirements': len(requirements),
            'type_distribution': type_distribution,
            'priority_distribution': priority_distribution,
            'status_distribution': status_distribution,
            'key_themes': key_themes,
            'recommendations': recommendations,
            'summary': f'找到 {len(requirements)} 个相关需求文档，主要涉及 {", ".join(key_themes[:3])} 等方面'
        }
    
    def _generate_recommendations(
        self,
        requirements: List[Dict[str, Any]],
        query: str,
        type_distribution: Dict[str, int]
    ) -> List[str]:
        """
        基于需求分析生成建议
        """
        recommendations = []
        
        # 基于需求类型分布的建议
        if type_distribution.get('functional', 0) > 0:
            recommendations.append('建议重点关注功能需求的测试覆盖')
        
        if type_distribution.get('performance', 0) > 0:
            recommendations.append('需要制定性能测试计划')
        
        if type_distribution.get('security', 0) > 0:
            recommendations.append('建议进行安全测试和风险评估')
        
        # 基于查询内容的建议
        if '测试' in query:
            recommendations.append('建议基于检索到的需求制定详细的测试用例')
        
        if '接口' in query or 'api' in query.lower():
            recommendations.append('建议进行接口兼容性和集成测试')
        
        # 通用建议
        recommendations.append('建议与需求相关的干系人确认理解的准确性')
        
        return recommendations
    
    def _extract_key_themes(self, requirements: List[Dict[str, Any]]) -> List[str]:
        """
        提取关键主题
        """
        # 简单的关键词提取
        all_content = ' '.join([
            req.get('content', '') for req in requirements
        ])
        
        # 常见主题关键词
        theme_keywords = {
            '用户管理': ['用户', '账号', '登录', '注册'],
            '数据管理': ['数据', '存储', '数据库', '备份'],
            '接口集成': ['接口', 'api', '集成', '对接'],
            '权限控制': ['权限', '角色', '访问控制', '授权'],
            '性能优化': ['性能', '优化', '响应时间', '并发'],
            '安全防护': ['安全', '加密', '防护', '漏洞'],
            '用户体验': ['界面', '交互', '体验', 'ui'],
            '系统监控': ['监控', '日志', '告警', '统计']
        }
        
        detected_themes = []
        content_lower = all_content.lower()
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                detected_themes.append(theme)
        
        return detected_themes[:5]  # 返回前5个主题


class ContextAwareGenerator:
    """
    上下文感知生成器
    
    结合项目知识库进行智能生成
    """
    
    def __init__(self, knowledge_service=None, requirement_service=None):
        self.knowledge_service = knowledge_service
        self.requirement_service = requirement_service or RequirementRetrievalService(knowledge_service)
    
    async def generate_with_context(
        self,
        request: str,
        project_id: str,
        knowledge_base_id: str,
        generation_type: str = 'test_case',
        context_sources: List[str] = None
    ) -> Dict[str, Any]:
        """
        基于上下文进行智能生成
        
        Args:
            request: 生成请求
            project_id: 项目ID
            knowledge_base_id: 知识库ID
            generation_type: 生成类型 (test_case, requirement, documentation)
            context_sources: 上下文来源
            
        Returns:
            生成结果
        """
        try:
            # 1. 检索相关需求和文档
            retrieval_result = await self.requirement_service.retrieve_requirements(
                request, project_id, knowledge_base_id, top_k=3
            )
            
            # 2. 构建上下文
            context = self._build_generation_context(
                request, retrieval_result, context_sources
            )
            
            # 3. 根据类型进行生成
            if generation_type == 'test_case':
                result = await self._generate_test_case(request, context)
            elif generation_type == 'requirement':
                result = await self._generate_requirement(request, context)
            elif generation_type == 'documentation':
                result = await self._generate_documentation(request, context)
            else:
                result = {'error': f'不支持的生成类型: {generation_type}'}
            
            # 4. 添加上下文信息
            result['context_info'] = {
                'sources_used': len(retrieval_result.get('requirements', [])),
                'context_quality': self._assess_context_quality(context),
                'generation_type': generation_type
            }
            
            return result
            
        except Exception as e:
            logger.error(f"上下文感知生成失败: {e}")
            return {
                'error': str(e),
                'generated_content': None
            }
    
    def _build_generation_context(
        self,
        request: str,
        retrieval_result: Dict[str, Any],
        context_sources: List[str] = None
    ) -> Dict[str, Any]:
        """
        构建生成上下文
        """
        context = {
            'original_request': request,
            'requirements': retrieval_result.get('requirements', []),
            'analysis': retrieval_result.get('analysis', {}),
            'context_sources': context_sources or [],
            'generation_time': datetime.now().isoformat()
        }
        
        # 提取关键信息
        if context['requirements']:
            context['key_requirements'] = [
                {
                    'content': req.get('content', '')[:300] + '...',
                    'type': req.get('requirement_type', 'unknown'),
                    'priority': req.get('priority', 'medium')
                }
                for req in context['requirements'][:3]
            ]
        
        return context
    
    def _assess_context_quality(self, context: Dict[str, Any]) -> str:
        """
        评估上下文质量
        """
        requirements_count = len(context.get('requirements', []))
        
        if requirements_count >= 3:
            return 'high'
        elif requirements_count >= 1:
            return 'medium'
        else:
            return 'low'
    
    async def _generate_test_case(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成测试用例
        """
        # 基于上下文生成测试用例
        requirements = context.get('requirements', [])
        
        test_case = {
            'name': f'{request} - 测试用例',
            'description': f'基于需求"{request}"和相关文档生成的测试用例',
            'priority': 'medium',
            'type': 'functional',
            'preconditions': [],
            'test_steps': [],
            'expected_results': [],
            'context_based': True
        }
        
        # 基于需求生成测试步骤
        if requirements:
            for i, req in enumerate(requirements[:2], 1):
                req_type = req.get('requirement_type', 'functional')
                test_case['test_steps'].append({
                    'step_number': i,
                    'action': f'验证需求: {req.get("content", "")[:100]}...',
                    'expected_result': f'满足{req_type}需求',
                    'source_requirement': req.get('metadata', {}).get('source', '未知')
                })
        
        return {
            'generated_content': test_case,
            'generation_method': 'context_aware',
            'confidence': 'high' if len(requirements) >= 2 else 'medium'
        }
    
    async def _generate_requirement(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成需求文档
        """
        requirements = context.get('requirements', [])
        
        requirement_doc = {
            'title': request,
            'description': f'基于现有需求和上下文生成的需求文档',
            'type': 'functional',
            'priority': 'medium',
            'acceptance_criteria': [],
            'related_requirements': [],
            'context_based': True
        }
        
        # 基于相关需求生成验收标准
        if requirements:
            for req in requirements[:3]:
                requirement_doc['related_requirements'].append({
                    'source': req.get('metadata', {}).get('source', '未知'),
                    'type': req.get('requirement_type', 'unknown'),
                    'summary': req.get('content', '')[:200] + '...'
                })
        
        return {
            'generated_content': requirement_doc,
            'generation_method': 'context_aware',
            'confidence': 'high' if len(requirements) >= 2 else 'medium'
        }
    
    async def _generate_documentation(self, request: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成文档
        """
        requirements = context.get('requirements', [])
        
        documentation = {
            'title': request,
            'sections': [],
            'references': [],
            'context_based': True
        }
        
        # 基于需求生成文档章节
        if requirements:
            documentation['sections'] = [
                {
                    'title': f'相关需求 {i+1}',
                    'content': req.get('content', '')[:500] + '...',
                    'source': req.get('metadata', {}).get('source', '未知')
                }
                for i, req in enumerate(requirements[:3])
            ]
        
        return {
            'generated_content': documentation,
            'generation_method': 'context_aware',
            'confidence': 'high' if len(requirements) >= 2 else 'medium'
        }