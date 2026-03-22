"""
基于知识库的测试用例生成服务
"""
import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import re

logger = logging.getLogger(__name__)

# 测试用例模板
TEST_CASE_TEMPLATES = {
    'functional': {
        'name': '功能测试用例模板',
        'description': '用于功能性需求的测试用例生成',
        'prompt': """你是一个专业的测试工程师，擅长根据需求文档生成详细的功能测试用例。

请根据以下需求文档，生成完整的功能测试用例。

**生成规则：**
1. 识别所有可能的测试场景
2. 包含正向测试和负向测试
3. 提供具体的测试数据
4. 明确的预期结果描述

**输出格式（JSON）：**
```json
{
  "test_suite": {
    "name": "测试套件名称",
    "description": "测试套件描述",
    "test_cases": [
      {
        "id": "TC001",
        "title": "测试用例标题",
        "priority": "High",
        "type": "Positive",
        "preconditions": ["前置条件"],
        "test_steps": [
          {
            "step": 1,
            "action": "操作描述",
            "expected": "预期结果"
          }
        ],
        "test_data": {
          "input": "输入数据",
          "expected_output": "预期输出"
        }
      }
    ]
  }
}
```"""
    },
    'api': {
        'name': 'API测试用例模板',
        'description': '用于API接口的测试用例生成',
        'prompt': """你是一个API测试专家，擅长根据接口文档生成全面的API测试用例。

请根据以下API文档，生成完整的API测试用例。

**生成规则：**
1. HTTP方法、URL、参数验证
2. 请求/响应数据格式验证
3. 各种HTTP状态码场景
4. 认证、授权、输入验证

**输出格式（JSON）：**
```json
{
  "api_test_suite": {
    "name": "API测试套件名称",
    "test_cases": [
      {
        "id": "API001",
        "title": "API测试用例标题",
        "method": "GET",
        "endpoint": "/api/endpoint",
        "expected_status": 200,
        "test_scenarios": [
          {
            "scenario": "正常请求",
            "input": {},
            "expected": {}
          }
        ]
      }
    ]
  }
}
```"""
    },
    'ui': {
        'name': 'UI测试用例模板',
        'description': '用于用户界面的测试用例生成',
        'prompt': """你是一个UI测试专家，擅长根据界面设计文档生成详细的UI测试用例。

请根据以下UI设计文档，生成完整的UI测试用例。

**生成规则：**
1. 界面元素测试
2. 用户操作流程测试
3. 响应式设计测试
4. 浏览器兼容性

**输出格式（JSON）：**
```json
{
  "ui_test_suite": {
    "name": "UI测试套件名称",
    "test_cases": [
      {
        "id": "UI001",
        "title": "UI测试用例标题",
        "element_type": "button",
        "test_steps": [
          {
            "step": 1,
            "action": "click",
            "target": "目标元素",
            "expected": "预期结果"
          }
        ]
      }
    ]
  }
}
```"""
    },
    'performance': {
        'name': '性能测试用例模板',
        'description': '用于性能测试的测试用例生成',
        'prompt': """你是一个性能测试专家，擅长根据性能需求生成详细的性能测试用例。

请根据以下性能需求文档，生成完整的性能测试用例。

**生成规则：**
1. 负载测试场景
2. 压力测试场景
3. 性能指标定义
4. 资源监控要求

**输出格式（JSON）：**
```json
{
  "performance_test_suite": {
    "name": "性能测试套件名称",
    "test_cases": [
      {
        "id": "PERF001",
        "title": "性能测试用例标题",
        "test_type": "Load",
        "performance_criteria": {
          "response_time": "< 2秒",
          "throughput": "> 1000 TPS"
        }
      }
    ]
  }
}
```"""
    }
}


class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, kb_service, rag_service, agents_service=None):
        """
        初始化测试用例生成器
        Args:
            kb_service: 知识库服务
            rag_service: RAG服务
            agents_service: 智能体服务（可选，用于增强分析）
        """
        self.kb_service = kb_service
        self.rag_service = rag_service
        self.agents_service = agents_service
    
    async def generate_test_cases(
        self,
        requirement_query: str,
        test_type: str = 'functional',
        top_k: int = 5,
        score_threshold: float = 0.3,
        llm_config: Optional[Dict[str, Any]] = None,
        use_agents: bool = False
    ) -> Dict[str, Any]:
        """
        生成测试用例（基于RAG增强分析或智能体分析）
        
        流程：
        1. 检索知识库获取相关文档
        2. 如果启用智能体：使用智能体进行深度分析
           否则：使用RAG增强分析
        3. 生成增强的上下文
        4. 调用LLM生成全面的测试用例
        
        Args:
            use_agents: 是否使用智能体服务进行增强分析
        """
        start_time = time.time()
        
        try:
            mode = "agents-enhanced" if (use_agents and self.agents_service) else "rag-enhanced"
            logger.info(f"Starting {mode} test case generation for type: {test_type}")
            
            # 1. 直接从数据库获取文档内容（不使用向量检索，避免阻塞）
            logger.info(f"开始获取知识库文档...")
            retrieval_start = time.time()
            
            try:
                # 直接从数据库读取文档
                from app.models.aitestrebort.knowledge import aitestrebortDocument
                
                documents = await aitestrebortDocument.filter(
                    knowledge_base_id=self.kb_service.knowledge_base_id,
                    status='completed'
                ).limit(top_k).all()
                
                if not documents:
                    logger.warning("知识库中没有已完成的文档")
                    return {
                        'success': False,
                        'message': '知识库中没有可用的文档',
                        'test_cases': [],
                        'retrieval_time': time.time() - retrieval_start,
                        'total_time': time.time() - start_time
                    }
                
                # 构建context_chunks格式
                context_chunks = []
                for doc in documents:
                    if doc.content:
                        context_chunks.append({
                            'content': doc.content[:5000],  # 限制长度，避免太长
                            'metadata': {
                                'document_id': str(doc.id),
                                'title': doc.title,
                                'source': doc.file_path or 'unknown'
                            },
                            'score': 1.0  # 直接读取，不计算相似度
                        })
                
                retrieval_time = time.time() - retrieval_start
                logger.info(f"从数据库获取了 {len(context_chunks)} 个文档，耗时: {retrieval_time:.2f}s")
                
            except Exception as e:
                logger.error(f"获取文档失败: {e}", exc_info=True)
                return {
                    'success': False,
                    'message': f'获取文档失败: {str(e)}',
                    'test_cases': [],
                    'retrieval_time': time.time() - retrieval_start,
                    'total_time': time.time() - start_time
                }
            
            if not context_chunks:
                logger.warning("未找到可用的文档内容")
                return {
                    'success': False,
                    'message': '未找到可用的文档内容',
                    'test_cases': [],
                    'retrieval_time': retrieval_time,
                    'total_time': time.time() - start_time
                }
            
            logger.info(f"准备了 {len(context_chunks)} 个文档片段用于分析")
            
            # 2. 使用智能体生成测试用例
            analysis_start = time.time()
            if use_agents and llm_config:
                # 使用简化的智能体服务
                logger.info("Using simplified agents service")
                
                # 合并检索到的文档内容
                context_text = "\n\n".join([chunk['content'] for chunk in context_chunks])
                full_requirement = f"{requirement_query}\n\n【知识库参考内容】\n{context_text}"
                
                logger.info(f"文档内容长度: {len(full_requirement)} 字符")
                
                # 直接生成测试用例（简化流程）
                from app.services.aitestrebort.simple_agents_service import SimpleAgentsService
                
                simple_service = SimpleAgentsService(llm_config)
                result = await simple_service.generate_test_cases(
                    requirement_text=full_requirement,
                    test_type=test_type
                )
                
                analysis_time = time.time() - analysis_start
                logger.info(f"智能体分析完成，耗时: {analysis_time:.2f}s")
                
                if result['success']:
                    # 转换为标准格式
                    test_cases = {
                        f'{test_type}_test_suite': {
                            'name': f'{test_type.title()} 测试套件',
                            'description': f'基于智能体生成的{test_type}测试用例',
                            'test_type': test_type,
                            'total_cases': result['total_cases'],
                            'test_cases': result['test_cases']
                        }
                    }
                    
                    # 简单的分析信息
                    enhanced_analysis = {
                        'modules': [],
                        'workflows': [],
                        'entities': [],
                        'test_scenarios': [],
                        'complexity': 'medium'
                    }
                    
                    # 跳过后续的RAG分析和LLM生成
                    generation_time = 0
                else:
                    logger.error(f"智能体生成失败: {result.get('message')}")
                    return {
                        'success': False,
                        'message': result.get('message', '测试用例生成失败'),
                        'test_cases': [],
                        'total_time': time.time() - start_time
                    }
            else:
                # 使用RAG增强分析
                logger.info("Using RAG enhanced analysis")
                enhanced_analysis = await self._rag_enhanced_analysis(
                    requirement_query,
                    context_chunks,
                    test_type
                )
                
                analysis_time = time.time() - analysis_start
                
                # 使用LLM生成测试用例
                generation_start = time.time()
                test_cases = await self._generate_with_llm(
                    requirement_query,
                    context_chunks,
                    test_type,
                    enhanced_analysis,
                    llm_config
                )
                generation_time = time.time() - generation_start
            
            # 4. 后处理
            processed = self._post_process(test_cases, test_type)
            
            total_time = time.time() - start_time
            
            return {
                'success': True,
                'message': f'测试用例生成成功（{mode}）',
                'query': requirement_query,
                'test_type': test_type,
                'test_cases': processed,
                'analysis': enhanced_analysis,
                'context_chunks': context_chunks,
                'retrieval_time': retrieval_time,
                'analysis_time': analysis_time,
                'generation_time': generation_time,
                'total_time': total_time,
                'statistics': self._calculate_stats(processed),
                'rag_enhanced': not use_agents,
                'agents_enhanced': use_agents and self.agents_service is not None,
                'generation_mode': mode
            }
            
        except Exception as e:
            logger.error(f"Test case generation failed: {e}", exc_info=True)
            return {
                'success': False,
                'message': f'测试用例生成失败: {str(e)}',
                'test_cases': [],
                'total_time': time.time() - start_time
            }
    
    async def _rag_enhanced_analysis(
        self,
        requirement_query: str,
        context_chunks: List[Dict],
        test_type: str
    ) -> Dict:
        """
        RAG增强分析：深度分析需求文档，提取测试相关信息
        
        这是关键步骤，不是简单地将原文档传给LLM，而是：
        1. 分析业务流程和功能点
        2. 识别测试场景（正常、异常、边界）
        3. 提取测试数据建议
        4. 识别依赖关系和前置条件
        5. 分析风险点和关注点
        """
        text = "\n".join([chunk['content'] for chunk in context_chunks])
        
        # 基础分析
        modules = self._extract_modules(text)
        workflows = self._extract_workflows(text)
        entities = self._extract_entities(text)
        
        # 测试场景识别（增强版）
        test_scenarios = self._identify_enhanced_test_scenarios(text, test_type)
        
        # 测试数据建议
        test_data_suggestions = self._extract_test_data_suggestions(text, test_type)
        
        # 边界条件识别
        boundary_conditions = self._identify_boundary_conditions(text)
        
        # 异常场景识别
        exception_scenarios = self._identify_exception_scenarios(text)
        
        # 依赖关系分析
        dependencies = self._analyze_dependencies(text)
        
        # 风险点识别
        risk_points = self._identify_risk_points(text, test_type)
        
        return {
            'modules': modules,
            'workflows': workflows,
            'entities': entities,
            'test_scenarios': test_scenarios,
            'test_data_suggestions': test_data_suggestions,
            'boundary_conditions': boundary_conditions,
            'exception_scenarios': exception_scenarios,
            'dependencies': dependencies,
            'risk_points': risk_points,
            'complexity': self._assess_complexity(text),
            'coverage_analysis': {
                'functional_coverage': len(modules),
                'scenario_coverage': len(test_scenarios),
                'data_coverage': len(test_data_suggestions),
                'exception_coverage': len(exception_scenarios)
            }
        }
    
    def _identify_enhanced_test_scenarios(self, text: str, test_type: str) -> List[Dict]:
        """识别增强的测试场景"""
        scenarios = []
        
        # 基础场景
        base_scenarios = {
            'functional': [
                {'name': '正常流程', 'priority': 'High', 'type': 'Positive'},
                {'name': '异常流程', 'priority': 'High', 'type': 'Negative'},
                {'name': '边界值', 'priority': 'Medium', 'type': 'Boundary'},
                {'name': '数据验证', 'priority': 'Medium', 'type': 'Positive'},
                {'name': '权限控制', 'priority': 'High', 'type': 'Negative'}
            ],
            'api': [
                {'name': '正常请求', 'priority': 'High', 'type': 'Positive'},
                {'name': '参数缺失', 'priority': 'High', 'type': 'Negative'},
                {'name': '参数非法', 'priority': 'High', 'type': 'Negative'},
                {'name': '认证失败', 'priority': 'High', 'type': 'Negative'},
                {'name': '并发请求', 'priority': 'Medium', 'type': 'Performance'}
            ],
            'ui': [
                {'name': '界面加载', 'priority': 'High', 'type': 'Positive'},
                {'name': '用户交互', 'priority': 'High', 'type': 'Positive'},
                {'name': '表单验证', 'priority': 'High', 'type': 'Negative'},
                {'name': '响应式布局', 'priority': 'Medium', 'type': 'Positive'},
                {'name': '浏览器兼容', 'priority': 'Medium', 'type': 'Compatibility'}
            ],
            'performance': [
                {'name': '正常负载', 'priority': 'High', 'type': 'Load'},
                {'name': '峰值负载', 'priority': 'High', 'type': 'Stress'},
                {'name': '长时间运行', 'priority': 'Medium', 'type': 'Endurance'},
                {'name': '资源限制', 'priority': 'Medium', 'type': 'Volume'}
            ]
        }
        
        scenarios.extend(base_scenarios.get(test_type, []))
        
        # 根据文本内容添加特定场景
        if '登录' in text or '认证' in text:
            scenarios.append({'name': '登录认证测试', 'priority': 'High', 'type': 'Security'})
        if '支付' in text or '交易' in text:
            scenarios.append({'name': '支付流程测试', 'priority': 'High', 'type': 'Critical'})
        if '文件' in text or '上传' in text:
            scenarios.append({'name': '文件上传测试', 'priority': 'Medium', 'type': 'Positive'})
        if '导出' in text or '下载' in text:
            scenarios.append({'name': '数据导出测试', 'priority': 'Medium', 'type': 'Positive'})
        if '权限' in text or '角色' in text:
            scenarios.append({'name': '权限控制测试', 'priority': 'High', 'type': 'Security'})
        
        return scenarios[:15]  # 限制数量
    
    def _extract_test_data_suggestions(self, text: str, test_type: str) -> List[Dict]:
        """提取测试数据建议"""
        suggestions = []
        
        # 数字类型数据
        if any(kw in text for kw in ['数量', '金额', '价格', '年龄', '数值']):
            suggestions.append({
                'category': '数值类型',
                'examples': ['正数', '负数', '零', '小数', '最大值', '最小值'],
                'description': '测试各种数值边界和特殊值'
            })
        
        # 字符串类型数据
        if any(kw in text for kw in ['名称', '标题', '描述', '内容', '文本']):
            suggestions.append({
                'category': '字符串类型',
                'examples': ['空字符串', '超长字符串', '特殊字符', 'SQL注入', 'XSS攻击'],
                'description': '测试字符串的各种边界情况和安全问题'
            })
        
        # 日期时间数据
        if any(kw in text for kw in ['日期', '时间', '开始', '结束', '期限']):
            suggestions.append({
                'category': '日期时间',
                'examples': ['当前时间', '过去时间', '未来时间', '非法格式', '时区问题'],
                'description': '测试日期时间的各种场景'
            })
        
        # 文件数据
        if any(kw in text for kw in ['文件', '上传', '附件', '图片', '文档']):
            suggestions.append({
                'category': '文件类型',
                'examples': ['空文件', '超大文件', '非法格式', '病毒文件', '损坏文件'],
                'description': '测试文件上传的各种情况'
            })
        
        # 用户数据
        if any(kw in text for kw in ['用户', '账号', '邮箱', '手机']):
            suggestions.append({
                'category': '用户信息',
                'examples': ['有效用户', '无效用户', '已删除用户', '锁定用户', '过期用户'],
                'description': '测试不同用户状态'
            })
        
        return suggestions
    
    def _identify_boundary_conditions(self, text: str) -> List[Dict]:
        """识别边界条件"""
        boundaries = []
        
        # 数值边界
        import re
        number_patterns = [
            r'(\d+)\s*[-~至到]\s*(\d+)',
            r'最[大小多少][:：]?\s*(\d+)',
            r'不[超少]过\s*(\d+)'
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    boundaries.append({
                        'type': '数值边界',
                        'condition': f"范围: {match}",
                        'test_values': ['最小值-1', '最小值', '最小值+1', '最大值-1', '最大值', '最大值+1']
                    })
        
        # 长度边界
        if any(kw in text for kw in ['长度', '字符', '位数']):
            boundaries.append({
                'type': '长度边界',
                'condition': '字符串长度限制',
                'test_values': ['空字符串', '1个字符', '正常长度', '最大长度', '超长字符串']
            })
        
        # 时间边界
        if any(kw in text for kw in ['时间', '日期', '期限']):
            boundaries.append({
                'type': '时间边界',
                'condition': '时间范围限制',
                'test_values': ['开始时间前', '开始时间', '正常时间', '结束时间', '结束时间后']
            })
        
        return boundaries[:10]
    
    def _identify_exception_scenarios(self, text: str) -> List[Dict]:
        """识别异常场景"""
        exceptions = []
        
        # 网络异常
        if any(kw in text for kw in ['网络', '连接', '请求', '接口']):
            exceptions.append({
                'category': '网络异常',
                'scenarios': ['网络超时', '连接中断', '请求失败', '响应延迟']
            })
        
        # 数据异常
        if any(kw in text for kw in ['数据', '记录', '信息']):
            exceptions.append({
                'category': '数据异常',
                'scenarios': ['数据不存在', '数据重复', '数据格式错误', '数据不一致']
            })
        
        # 权限异常
        if any(kw in text for kw in ['权限', '授权', '认证']):
            exceptions.append({
                'category': '权限异常',
                'scenarios': ['未登录', '权限不足', '登录过期', '账号被锁定']
            })
        
        # 系统异常
        exceptions.append({
            'category': '系统异常',
            'scenarios': ['服务不可用', '系统维护', '资源耗尽', '并发冲突']
        })
        
        return exceptions
    
    def _analyze_dependencies(self, text: str) -> List[Dict]:
        """分析依赖关系"""
        dependencies = []
        
        if '依赖' in text or '前置' in text:
            dependencies.append({
                'type': '功能依赖',
                'description': '需要先完成其他功能'
            })
        
        if '数据库' in text or '存储' in text:
            dependencies.append({
                'type': '数据依赖',
                'description': '需要数据库中存在特定数据'
            })
        
        if '接口' in text or 'API' in text:
            dependencies.append({
                'type': '接口依赖',
                'description': '依赖外部接口或服务'
            })
        
        return dependencies
    
    def _identify_risk_points(self, text: str, test_type: str) -> List[Dict]:
        """识别风险点"""
        risks = []
        
        # 安全风险
        if any(kw in text for kw in ['密码', '支付', '敏感', '隐私']):
            risks.append({
                'category': '安全风险',
                'level': 'High',
                'description': '涉及敏感信息，需要重点测试安全性',
                'test_focus': ['数据加密', '权限控制', '输入验证', '日志脱敏']
            })
        
        # 性能风险
        if any(kw in text for kw in ['大量', '批量', '并发', '高频']):
            risks.append({
                'category': '性能风险',
                'level': 'Medium',
                'description': '可能存在性能瓶颈',
                'test_focus': ['响应时间', '并发处理', '资源占用', '数据库性能']
            })
        
        # 数据一致性风险
        if any(kw in text for kw in ['事务', '同步', '一致性']):
            risks.append({
                'category': '数据一致性风险',
                'level': 'High',
                'description': '需要确保数据一致性',
                'test_focus': ['事务回滚', '并发更新', '数据同步', '异常恢复']
            })
        
        return risks
    
    def _extract_modules(self, text: str) -> List[str]:
        """提取功能模块"""
        patterns = [
            r'(?:功能|模块)[:：]\s*([^\n]+)',
            r'([^，。\n]+)(?:功能|模块)',
        ]
        modules = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            modules.extend([m.strip() for m in matches if m.strip()])
        return list(set([m for m in modules if 2 < len(m) < 50]))[:10]
    
    def _extract_workflows(self, text: str) -> List[Dict]:
        """提取业务流程"""
        patterns = [
            r'(?:步骤|流程)[:：]\s*([^\n]+)',
            r'(\d+[\.、])\s*([^\n]+)',
        ]
        workflows = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                step = match[-1].strip() if isinstance(match, tuple) else match.strip()
                if 5 < len(step) < 200:
                    workflows.append({'step': len(workflows) + 1, 'description': step})
        return workflows[:20]
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取数据实体"""
        patterns = [
            r'(?:用户|订单|产品|账户|角色|权限)(?:信息|数据|表)?',
            r'([A-Z][a-z]+(?:[A-Z][a-z]+)*)',
        ]
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend([m.strip() for m in matches if isinstance(m, str)])
        return list(set([e for e in entities if 2 < len(e) < 30]))[:15]
    
    def _assess_complexity(self, text: str) -> str:
        """评估复杂度"""
        word_count = len(text.split())
        if word_count < 100:
            return 'low'
        elif word_count < 500:
            return 'medium'
        return 'high'
    
    def _identify_scenarios(self, text: str, test_type: str) -> List[str]:
        """识别测试场景"""
        base_scenarios = {
            'functional': ['正常流程', '异常流程', '边界值', '数据验证', '权限控制'],
            'api': ['接口调用', '参数验证', '认证授权', '错误处理', '性能测试'],
            'ui': ['界面元素', '交互流程', '兼容性', '响应式', '可用性'],
            'performance': ['负载测试', '压力测试', '容量测试', '稳定性', '资源监控']
        }
        return base_scenarios.get(test_type, [])
    
    async def _generate_with_llm(
        self,
        query: str,
        chunks: List[Dict],
        test_type: str,
        analysis: Dict,
        llm_config: Optional[Dict] = None
    ) -> Dict:
        """使用LLM生成测试用例"""
        try:
            template = TEST_CASE_TEMPLATES.get(test_type, TEST_CASE_TEMPLATES['functional'])
            prompt = self._build_prompt(template['prompt'], query, chunks, analysis)
            
            result = await self.rag_service.query(
                query_text=prompt,
                top_k=0,
                score_threshold=0.0,
                system_prompt=template['prompt'],
                prompt_template='testing',
                llm_config=llm_config
            )
            
            if result['success']:
                return self._parse_test_cases(result['answer'], test_type)
            else:
                return self._generate_fallback(analysis, test_type)
                
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._generate_fallback(analysis, test_type)
    
    def _build_prompt(self, base: str, query: str, chunks: List[Dict], analysis: Dict) -> str:
        """
        构建增强的Prompt（基于RAG分析结果）
        
        不是简单地将原文档传给LLM，而是提供经过分析和整理的结构化信息
        """
        # 1. 原始需求文档（精简版）
        context = "\n".join([
            f"【参考文档 {i+1}】\n{chunk['content'][:500]}..." if len(chunk['content']) > 500 else f"【参考文档 {i+1}】\n{chunk['content']}"
            for i, chunk in enumerate(chunks[:3])  # 只取前3个最相关的
        ])
        
        # 2. RAG增强分析结果
        analysis_text = f"""
【RAG增强分析结果】

一、功能模块识别
{', '.join(analysis.get('modules', [])[:10])}

二、业务流程分析
{chr(10).join([f"{i+1}. {wf['description']}" for i, wf in enumerate(analysis.get('workflows', [])[:5])])}

三、测试场景识别（共{len(analysis.get('test_scenarios', []))}个）
{chr(10).join([f"- {sc['name']} (优先级: {sc['priority']}, 类型: {sc['type']})" for sc in analysis.get('test_scenarios', [])[:10]])}

四、测试数据建议
{chr(10).join([f"• {td['category']}: {', '.join(td['examples'][:3])}" for td in analysis.get('test_data_suggestions', [])[:5]])}

五、边界条件
{chr(10).join([f"• {bc['type']}: {bc['condition']}" for bc in analysis.get('boundary_conditions', [])[:5]])}

六、异常场景
{chr(10).join([f"• {ex['category']}: {', '.join(ex['scenarios'][:3])}" for ex in analysis.get('exception_scenarios', [])[:5]])}

七、风险点识别
{chr(10).join([f"• [{rp['level']}] {rp['category']}: {rp['description']}" for rp in analysis.get('risk_points', [])[:3]])}

八、覆盖度分析
- 功能覆盖: {analysis.get('coverage_analysis', {}).get('functional_coverage', 0)} 个模块
- 场景覆盖: {analysis.get('coverage_analysis', {}).get('scenario_coverage', 0)} 个场景
- 数据覆盖: {analysis.get('coverage_analysis', {}).get('data_coverage', 0)} 类数据
- 异常覆盖: {analysis.get('coverage_analysis', {}).get('exception_coverage', 0)} 类异常
"""
        
        # 3. 用户需求
        user_requirement = f"""
【用户需求】
{query}
"""
        
        # 4. 生成指导
        generation_guide = """
【生成指导】
请基于以上RAG增强分析结果，生成全面、详细的测试用例。要求：

1. **场景全面性**：覆盖所有识别的测试场景（正常、异常、边界）
2. **数据完整性**：使用建议的测试数据，包含各种边界值和特殊值
3. **步骤详细性**：每个测试步骤要清晰、可执行
4. **风险关注**：重点关注识别的风险点
5. **优先级合理**：根据场景类型和风险级别设置优先级

请确保生成的测试用例：
- 可以直接用于测试执行
- 包含明确的前置条件和预期结果
- 覆盖正常流程、异常流程和边界条件
- 包含具体的测试数据示例
"""
        
        return f"{base}\n\n{context}\n\n{analysis_text}\n\n{user_requirement}\n\n{generation_guide}"
    
    def _parse_test_cases(self, text: str, test_type: str) -> Dict:
        """解析测试用例"""
        try:
            # 提取JSON
            json_pattern = r'```json\s*(.*?)\s*```'
            matches = re.findall(json_pattern, text, re.DOTALL)
            if matches:
                return json.loads(matches[0])
            
            # 查找JSON对象
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1:
                return json.loads(text[start:end + 1])
            
            return self._parse_text(text, test_type)
            
        except Exception as e:
            logger.warning(f"JSON parsing failed: {e}")
            return self._parse_text(text, test_type)
    
    def _parse_text(self, text: str, test_type: str) -> Dict:
        """解析文本为测试用例"""
        test_cases = []
        lines = text.split('\n')
        current_case = {}
        case_id = 1
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if any(kw in line.lower() for kw in ['测试用例', 'test case']):
                if current_case:
                    test_cases.append(current_case)
                current_case = {
                    'id': f"TC{case_id:03d}",
                    'title': line,
                    'priority': 'Medium',
                    'type': 'Positive'
                }
                case_id += 1
            elif line.startswith(('步骤', '操作', 'Step')):
                if 'test_steps' not in current_case:
                    current_case['test_steps'] = []
                current_case['test_steps'].append({
                    'step': len(current_case['test_steps']) + 1,
                    'action': line,
                    'expected': '待定义'
                })
        
        if current_case:
            test_cases.append(current_case)
        
        return {
            f'{test_type}_test_suite': {
                'name': f'{test_type.title()}测试套件',
                'description': f'基于需求文档生成的测试用例',
                'test_cases': test_cases
            }
        }
    
    def _generate_fallback(self, analysis: Dict, test_type: str) -> Dict:
        """生成备用测试用例"""
        modules = analysis.get('modules', ['基础功能'])
        scenarios = analysis.get('test_scenarios', ['正常流程', '异常流程'])
        
        test_cases = []
        case_id = 1
        
        for module in modules[:3]:
            for scenario in scenarios[:2]:
                test_cases.append({
                    'id': f"TC{case_id:03d}",
                    'title': f"{module} - {scenario}",
                    'priority': 'Medium',
                    'type': 'Positive' if '正常' in scenario else 'Negative',
                    'category': module,
                    'test_steps': [{
                        'step': 1,
                        'action': f"执行{module}相关操作",
                        'expected': f"系统正确响应{scenario}"
                    }]
                })
                case_id += 1
        
        return {
            f'{test_type}_test_suite': {
                'name': f'{test_type.title()}测试套件',
                'description': '基于需求分析生成的测试用例',
                'test_cases': test_cases
            }
        }
    
    def _post_process(self, test_cases: Dict, test_type: str) -> Dict:
        """后处理测试用例"""
        try:
            suite_key = f'{test_type}_test_suite'
            if suite_key not in test_cases:
                for key in ['test_suite', 'api_test_suite', 'ui_test_suite', 'performance_test_suite']:
                    if key in test_cases:
                        suite_key = key
                        break
            
            if suite_key not in test_cases:
                return test_cases
            
            suite = test_cases[suite_key]
            cases = suite.get('test_cases', [])
            
            for i, case in enumerate(cases):
                case.setdefault('id', f"TC{i+1:03d}")
                case.setdefault('title', f"测试用例 {i+1}")
                case.setdefault('priority', 'Medium')
                case.setdefault('type', 'Positive')
                case['generated_at'] = datetime.now().isoformat()
                case['test_type'] = test_type
            
            suite['generated_at'] = datetime.now().isoformat()
            suite['test_type'] = test_type
            suite['total_cases'] = len(cases)
            
            return test_cases
            
        except Exception as e:
            logger.error(f"Post-processing failed: {e}")
            return test_cases
    
    def _calculate_stats(self, test_cases: Dict) -> Dict:
        """计算统计信息"""
        try:
            # 查找测试套件
            suite = None
            for key in test_cases:
                if 'test_suite' in key:
                    suite = test_cases[key]
                    break
            
            if not suite or 'test_cases' not in suite:
                return {
                    'total_test_cases': 0,
                    'high_priority': 0,
                    'coverage_areas': 0
                }
            
            cases = suite['test_cases']
            return {
                'total_test_cases': len(cases),
                'high_priority': len([c for c in cases if c.get('priority') == 'High']),
                'coverage_areas': len(set([c.get('category', '') for c in cases if c.get('category')]))
            }
        except Exception as e:
            logger.error(f"Stats calculation failed: {e}")
            return {
                'total_test_cases': 0,
                'high_priority': 0,
                'coverage_areas': 0
            }
    
    def _convert_agents_analysis(self, agents_analysis: Dict) -> Dict:
        """
        转换智能体分析结果为统一格式
        """
        return {
            'modules': agents_analysis.get('modules', []),
            'workflows': agents_analysis.get('workflows', []),
            'entities': agents_analysis.get('entities', []),
            'test_scenarios': self._convert_agents_scenarios(agents_analysis.get('test_scenarios', {})),
            'test_data_suggestions': self._extract_test_data_from_agents(agents_analysis.get('test_points', {})),
            'boundary_conditions': self._extract_boundary_from_agents(agents_analysis.get('test_points', {})),
            'exception_scenarios': self._extract_exceptions_from_agents(agents_analysis.get('test_points', {})),
            'dependencies': agents_analysis.get('dependencies', []),
            'risk_points': agents_analysis.get('risk_points', []),
            'complexity': agents_analysis.get('complexity', 'medium'),
            'coverage_analysis': {
                'functional_coverage': len(agents_analysis.get('modules', [])),
                'scenario_coverage': len(agents_analysis.get('test_scenarios', {})),
                'data_coverage': len(agents_analysis.get('test_points', {}).get('functional_points', [])),
                'exception_coverage': len(agents_analysis.get('test_points', {}).get('exception_points', []))
            }
        }
    
    def _convert_agents_scenarios(self, agents_scenarios: Dict) -> List[Dict]:
        """转换智能体场景为统一格式"""
        scenarios = []
        for scenario_type, scenario_list in agents_scenarios.items():
            for scenario in scenario_list:
                scenarios.append({
                    'name': scenario.get('name', ''),
                    'priority': scenario.get('priority', 'Medium'),
                    'type': scenario_type.replace('_scenarios', '').title()
                })
        return scenarios
    
    def _extract_test_data_from_agents(self, test_points: Dict) -> List[Dict]:
        """从智能体测试点提取测试数据建议"""
        suggestions = []
        for point_type, points in test_points.items():
            if points:
                suggestions.append({
                    'category': point_type.replace('_points', '').title(),
                    'examples': [p.get('name', '') for p in points[:3]],
                    'description': f'{point_type}相关的测试数据'
                })
        return suggestions
    
    def _extract_boundary_from_agents(self, test_points: Dict) -> List[Dict]:
        """从智能体测试点提取边界条件"""
        boundaries = []
        for point in test_points.get('boundary_points', []):
            boundaries.append({
                'type': '边界条件',
                'condition': point.get('description', ''),
                'test_values': ['最小值', '正常值', '最大值']
            })
        return boundaries
    
    def _extract_exceptions_from_agents(self, test_points: Dict) -> List[Dict]:
        """从智能体测试点提取异常场景"""
        exceptions = []
        for point in test_points.get('exception_points', []):
            exceptions.append({
                'category': '异常场景',
                'scenarios': [point.get('name', '')]
            })
        return exceptions
