"""
agents-testcase 智能体服务
基于需求文档分析，智能生成测试用例
"""
import logging
from typing import Dict, Any, List, Optional
import json
import re

logger = logging.getLogger(__name__)


class AgentsTestCaseService:
    """agents-testcase 智能体服务"""
    
    def __init__(self, kb_service, rag_service, llm_config: Dict[str, Any]):
        """
        初始化智能体
        Args:
            kb_service: 知识库服务（复用现有）
            rag_service: RAG服务（复用现有）
            llm_config: LLM配置（使用全局配置）
        """
        self.kb_service = kb_service
        self.rag_service = rag_service
        self.llm_config = llm_config
        self.llm_client = None
        
    async def _initialize_llm(self):
        """初始化LLM客户端"""
        if self.llm_client:
            logger.info("LLM客户端已存在，跳过初始化")
            return
        
        if not self.llm_config:
            logger.error("LLM配置为空，无法初始化LLM客户端")
            raise ValueError("LLM配置为空")
            
        try:
            from langchain_openai import ChatOpenAI
            
            logger.info(f"开始初始化LLM客户端...")
            logger.info(f"Provider: {self.llm_config.get('provider', 'unknown')}")
            logger.info(f"Model: {self.llm_config.get('model_name', 'unknown')}")
            logger.info(f"Base URL: {self.llm_config.get('base_url', 'unknown')}")
            logger.info(f"Has API Key: {bool(self.llm_config.get('api_key'))}")
            
            if self.llm_config.get('provider') == 'openai':
                self.llm_client = ChatOpenAI(
                    model=self.llm_config.get('model_name', 'gpt-3.5-turbo'),
                    api_key=self.llm_config.get('api_key'),
                    base_url=self.llm_config.get('base_url'),
                    temperature=self.llm_config.get('temperature', 0.7),
                    max_tokens=self.llm_config.get('max_tokens', 2000)
                )
            else:
                # 默认使用OpenAI兼容接口
                self.llm_client = ChatOpenAI(
                    model=self.llm_config.get('model_name', 'gpt-3.5-turbo'),
                    api_key=self.llm_config.get('api_key', 'dummy'),
                    base_url=self.llm_config.get('base_url'),
                    temperature=self.llm_config.get('temperature', 0.7),
                    max_tokens=self.llm_config.get('max_tokens', 2000)
                )
            
            logger.info("✅ LLM客户端初始化成功")
        except Exception as e:
            logger.error(f"❌ LLM客户端初始化失败: {e}", exc_info=True)
            raise
        
    async def analyze_requirement(
        self,
        requirement_text: str,
        document_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        深度分析需求文档
        
        Args:
            requirement_text: 需求文本
            document_id: 文档ID（可选，用于从知识库获取更多上下文）
            
        Returns:
            {
                'modules': List[str],          # 功能模块
                'workflows': List[Dict],       # 业务流程
                'test_points': List[Dict],     # 测试点
                'test_scenarios': List[Dict],  # 测试场景
                'risk_points': List[Dict],     # 风险点
                'dependencies': List[Dict],    # 依赖关系
                'complexity': str              # 复杂度评估
            }
        """
        logger.info("开始深度分析需求文档")
        
        # 1. 基础分析
        modules = self._extract_modules(requirement_text)
        workflows = self._extract_workflows(requirement_text)
        entities = self._extract_entities(requirement_text)
        
        # 2. 测试点识别
        test_points = await self.extract_test_points(requirement_text)
        
        # 3. 测试场景生成
        test_scenarios = await self.generate_test_scenarios(test_points)
        
        # 4. 风险点识别
        risk_points = self._identify_risk_points(requirement_text)
        
        # 5. 依赖关系分析
        dependencies = self._analyze_dependencies(requirement_text)
        
        # 6. 复杂度评估
        complexity = self._assess_complexity(requirement_text)
        
        return {
            'modules': modules,
            'workflows': workflows,
            'entities': entities,
            'test_points': test_points,
            'test_scenarios': test_scenarios,
            'risk_points': risk_points,
            'dependencies': dependencies,
            'complexity': complexity,
            'summary': self._generate_summary(modules, test_points, risk_points)
        }
    
    async def extract_test_points(self, requirement_text: str) -> Dict[str, List[Dict]]:
        """
        提取测试点
        
        Returns:
            {
                'functional_points': [],    # 功能测试点
                'boundary_points': [],      # 边界测试点
                'exception_points': [],     # 异常测试点
                'performance_points': [],   # 性能测试点
                'security_points': []       # 安全测试点
            }
        """
        logger.info("提取测试点")
        
        # 使用LLM进行智能提取
        prompt = self._build_test_point_extraction_prompt(requirement_text)
        
        try:
            # 初始化LLM
            logger.info("初始化LLM客户端...")
            await self._initialize_llm()
            logger.info("LLM客户端初始化成功")
            
            # 直接调用LLM（不需要检索知识库）
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content=self._get_test_point_system_prompt()),
                HumanMessage(content=prompt)
            ]
            
            logger.info("调用LLM提取测试点...")
            response = await self.llm_client.ainvoke(messages)
            answer = response.content
            logger.info(f"LLM响应长度: {len(answer)} 字符")
            
            # 解析LLM响应
            test_points = self._parse_test_points(answer)
            logger.info(f"成功提取测试点: {sum(len(points) for points in test_points.values())} 个")
            return test_points
                
        except Exception as e:
            logger.error(f"测试点提取失败: {e}", exc_info=True)
            logger.warning("使用规则提取作为回退方案")
            return self._rule_based_test_point_extraction(requirement_text)
    
    async def generate_test_scenarios(
        self,
        test_points: Dict[str, List[Dict]]
    ) -> Dict[str, List[Dict]]:
        """
        生成测试场景
        
        Returns:
            {
                'positive_scenarios': [],   # 正向场景
                'negative_scenarios': [],   # 负向场景
                'boundary_scenarios': [],   # 边界场景
                'integration_scenarios': [] # 集成场景
            }
        """
        logger.info("生成测试场景")
        
        scenarios = {
            'positive_scenarios': [],
            'negative_scenarios': [],
            'boundary_scenarios': [],
            'integration_scenarios': []
        }
        
        # 从功能测试点生成正向场景
        for point in test_points.get('functional_points', []):
            scenarios['positive_scenarios'].append({
                'id': f"PS{len(scenarios['positive_scenarios']) + 1:03d}",
                'name': f"{point['name']} - 正常流程",
                'description': point['description'],
                'priority': point.get('priority', 'Medium'),
                'type': 'Positive',
                'test_point': point
            })
        
        # 从异常测试点生成负向场景
        for point in test_points.get('exception_points', []):
            scenarios['negative_scenarios'].append({
                'id': f"NS{len(scenarios['negative_scenarios']) + 1:03d}",
                'name': f"{point['name']} - 异常处理",
                'description': point['description'],
                'priority': 'High',
                'type': 'Negative',
                'test_point': point
            })
        
        # 从边界测试点生成边界场景
        for point in test_points.get('boundary_points', []):
            scenarios['boundary_scenarios'].append({
                'id': f"BS{len(scenarios['boundary_scenarios']) + 1:03d}",
                'name': f"{point['name']} - 边界值",
                'description': point['description'],
                'priority': 'Medium',
                'type': 'Boundary',
                'test_point': point
            })
        
        logger.info(f"生成了 {sum(len(s) for s in scenarios.values())} 个测试场景")
        return scenarios
    
    async def generate_test_cases(
        self,
        scenarios: Dict[str, List[Dict]],
        test_type: str = 'functional'
    ) -> Dict[str, Any]:
        """
        生成详细测试用例
        
        Returns:
            {
                'test_suite': {
                    'name': '',
                    'description': '',
                    'test_cases': [
                        {
                            'id': '',
                            'title': '',
                            'priority': '',
                            'type': '',
                            'preconditions': [],
                            'test_steps': [],
                            'test_data': {},
                            'expected_results': [],
                            'postconditions': []
                        }
                    ]
                }
            }
        """
        logger.info(f"生成{test_type}测试用例")
        
        test_cases = []
        case_id = 1
        
        # 处理所有场景
        all_scenarios = []
        for scenario_type, scenario_list in scenarios.items():
            all_scenarios.extend(scenario_list)
        
        logger.info(f"共有 {len(all_scenarios)} 个场景需要生成测试用例")
        
        for scenario in all_scenarios:
            # 使用LLM生成详细测试用例
            test_case = await self._generate_single_test_case(
                scenario,
                case_id,
                test_type
            )
            test_cases.append(test_case)
            case_id += 1
        
        logger.info(f"成功生成 {len(test_cases)} 个测试用例")
        
        return {
            f'{test_type}_test_suite': {
                'name': f'{test_type.title()} 测试套件',
                'description': f'基于智能体分析生成的{test_type}测试用例',
                'test_type': test_type,
                'total_cases': len(test_cases),
                'test_cases': test_cases
            }
        }
    
    async def _generate_single_test_case(
        self,
        scenario: Dict,
        case_id: int,
        test_type: str
    ) -> Dict[str, Any]:
        """生成单个测试用例"""
        
        # 构建详细的测试用例生成提示
        test_point = scenario.get('test_point', {})
        
        if test_type == 'api':
            # API测试用例的详细提示
            prompt = f"""
基于以下测试场景，生成详细的API测试用例：

【场景信息】
- 场景ID: {scenario['id']}
- 场景名称: {scenario['name']}
- 场景描述: {scenario['description']}
- 优先级: {scenario['priority']}
- 类型: {scenario.get('type', 'Positive')}

【测试点】
- 名称: {test_point.get('name', '未指定')}
- 描述: {test_point.get('description', '未指定')}

请生成包含以下内容的API测试用例（JSON格式）：

1. **前置条件** (preconditions): 列出测试前需要满足的条件
2. **测试步骤** (test_steps): 详细的API调用步骤，每步包含：
   - 请求方法 (GET/POST/PUT/DELETE)
   - 请求URL
   - 请求参数/Body
   - 预期响应状态码
   - 预期响应内容
3. **测试数据** (test_data): 具体的测试数据示例
4. **预期结果** (expected_results): 明确的验证点
5. **后置条件** (postconditions): 测试后的状态

输出格式：
```json
{{
  "preconditions": ["前置条件1", "前置条件2"],
  "test_steps": [
    {{
      "step": 1,
      "method": "POST",
      "url": "/api/xxx",
      "action": "发送登录请求",
      "request_data": {{"username": "test", "password": "123"}},
      "expected": "返回200状态码，包含token"
    }}
  ],
  "test_data": {{
    "valid_user": {{"username": "test", "password": "123"}},
    "invalid_user": {{"username": "wrong", "password": "wrong"}}
  }},
  "expected_results": ["验证点1", "验证点2"],
  "postconditions": ["后置条件1"]
}}
```
"""
        else:
            # 功能测试用例的详细提示
            prompt = f"""
基于以下测试场景，生成详细的功能测试用例：

【场景信息】
- 场景ID: {scenario['id']}
- 场景名称: {scenario['name']}
- 场景描述: {scenario['description']}
- 优先级: {scenario['priority']}
- 类型: {scenario.get('type', 'Positive')}

【测试点】
- 名称: {test_point.get('name', '未指定')}
- 描述: {test_point.get('description', '未指定')}

请生成包含以下内容的测试用例（JSON格式）：

1. **前置条件** (preconditions): 测试前需要满足的条件
2. **测试步骤** (test_steps): 详细的操作步骤，每步包含操作和预期结果
3. **测试数据** (test_data): 具体的测试数据
4. **预期结果** (expected_results): 明确的验证点
5. **后置条件** (postconditions): 测试后的状态

输出JSON格式。
"""
        
        try:
            # 初始化LLM
            logger.info(f"为场景 {scenario.get('id', 'unknown')} 生成测试用例...")
            await self._initialize_llm()
            
            # 直接调用LLM（不需要检索知识库）
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content="你是一个专业的测试工程师，擅长编写详细的测试用例。请严格按照要求输出JSON格式。"),
                HumanMessage(content=prompt)
            ]
            
            logger.info("调用LLM生成测试用例...")
            response = await self.llm_client.ainvoke(messages)
            answer = response.content
            logger.info(f"LLM响应长度: {len(answer)} 字符")
            
            # 解析LLM响应
            test_case = self._parse_test_case(answer, case_id, scenario)
            logger.info(f"成功生成测试用例 {test_case.get('id', 'unknown')}")
            return test_case
                
        except Exception as e:
            logger.error(f"测试用例生成失败: {e}", exc_info=True)
            logger.warning(f"使用模板生成测试用例 TC{case_id:03d}")
            return self._template_test_case(case_id, scenario, test_type)
    
    def _template_test_case(
        self,
        case_id: int,
        scenario: Dict,
        test_type: str
    ) -> Dict[str, Any]:
        """使用模板生成测试用例（基于场景信息生成更真实的内容）"""
        
        test_point = scenario.get('test_point', {})
        point_name = test_point.get('name', scenario['name'])
        point_desc = test_point.get('description', scenario['description'])
        
        # 根据测试类型生成不同的测试用例
        if test_type == 'api':
            # API测试用例模板
            return {
                'id': f"TC{case_id:03d}",
                'title': scenario['name'],
                'description': point_desc,
                'priority': scenario['priority'],
                'type': scenario.get('type', 'Positive'),
                'test_type': test_type,
                'preconditions': [
                    "API服务已启动",
                    "测试环境已配置",
                    "认证token已获取"
                ],
                'test_steps': [
                    {
                        'step': 1,
                        'method': 'POST' if 'create' in point_name.lower() or '创建' in point_name else 'GET',
                        'url': f"/api/{point_name.lower().replace(' ', '-')}",
                        'action': f"调用{point_name}接口",
                        'request_data': {"param1": "value1", "param2": "value2"},
                        'expected': "返回200状态码，响应数据格式正确"
                    },
                    {
                        'step': 2,
                        'action': "验证响应数据",
                        'expected': "数据字段完整，值符合预期"
                    },
                    {
                        'step': 3,
                        'action': "验证数据库状态",
                        'expected': "数据已正确保存到数据库"
                    }
                ],
                'test_data': {
                    'valid_request': {
                        "param1": "valid_value",
                        "param2": "valid_value"
                    },
                    'invalid_request': {
                        "param1": "",
                        "param2": None
                    }
                },
                'expected_results': [
                    "API调用成功",
                    "返回正确的状态码",
                    "响应数据格式正确",
                    "数据持久化成功"
                ],
                'postconditions': [
                    "系统状态正常",
                    "数据一致性保持",
                    "日志已记录"
                ]
            }
        else:
            # 功能测试用例模板
            return {
                'id': f"TC{case_id:03d}",
                'title': scenario['name'],
                'description': point_desc,
                'priority': scenario['priority'],
                'type': scenario.get('type', 'Positive'),
                'test_type': test_type,
                'preconditions': [
                    "系统已正常启动",
                    "用户已登录系统",
                    "测试数据已准备"
                ],
                'test_steps': [
                    {
                        'step': 1,
                        'action': f"打开{point_name}功能页面",
                        'expected': "页面正常加载，元素显示正确"
                    },
                    {
                        'step': 2,
                        'action': f"执行{point_name}操作",
                        'expected': "操作执行成功，无错误提示"
                    },
                    {
                        'step': 3,
                        'action': "验证操作结果",
                        'expected': "结果符合预期，数据正确"
                    }
                ],
                'test_data': {
                    'input': f'{point_name}测试输入数据',
                    'expected_output': f'{point_name}预期输出数据'
                },
                'expected_results': [
                    f"{point_name}操作成功完成",
                    "数据正确保存",
                    "界面正确显示结果"
                ],
                'postconditions': [
                    "系统状态正常",
                    "数据一致性保持"
                ]
            }
    
    # ========== 辅助方法 ==========
    
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
                    workflows.append({
                        'step': len(workflows) + 1,
                        'description': step
                    })
        return workflows[:20]
    
    def _extract_entities(self, text: str) -> List[str]:
        """提取数据实体"""
        patterns = [
            r'(?:用户|订单|产品|账户|角色|权限)(?:信息|数据|表)?',
        ]
        entities = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            entities.extend([m.strip() for m in matches if isinstance(m, str)])
        return list(set([e for e in entities if 2 < len(e) < 30]))[:15]
    
    def _identify_risk_points(self, text: str) -> List[Dict]:
        """识别风险点"""
        risks = []
        
        # 安全风险
        if any(kw in text for kw in ['密码', '支付', '敏感', '隐私', '加密']):
            risks.append({
                'category': '安全风险',
                'level': 'High',
                'description': '涉及敏感信息，需要重点测试安全性',
                'test_focus': ['数据加密', '权限控制', '输入验证', '日志脱敏']
            })
        
        # 性能风险
        if any(kw in text for kw in ['大量', '批量', '并发', '高频', '性能']):
            risks.append({
                'category': '性能风险',
                'level': 'Medium',
                'description': '可能存在性能瓶颈',
                'test_focus': ['响应时间', '并发处理', '资源占用', '数据库性能']
            })
        
        # 数据一致性风险
        if any(kw in text for kw in ['事务', '同步', '一致性', '数据库']):
            risks.append({
                'category': '数据一致性风险',
                'level': 'High',
                'description': '需要确保数据一致性',
                'test_focus': ['事务回滚', '并发更新', '数据同步', '异常恢复']
            })
        
        return risks
    
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
    
    def _assess_complexity(self, text: str) -> str:
        """评估复杂度"""
        word_count = len(text.split())
        if word_count < 100:
            return 'low'
        elif word_count < 500:
            return 'medium'
        return 'high'
    
    def _generate_summary(
        self,
        modules: List[str],
        test_points: Dict,
        risk_points: List[Dict]
    ) -> str:
        """生成分析摘要"""
        total_points = sum(len(points) for points in test_points.values())
        high_risks = len([r for r in risk_points if r['level'] == 'High'])
        
        return f"识别到 {len(modules)} 个功能模块，{total_points} 个测试点，{high_risks} 个高风险点。"
    
    def _build_test_point_extraction_prompt(self, requirement_text: str) -> str:
        """构建测试点提取提示"""
        return f"""
请分析以下需求文档，提取所有测试点，并按类别分类。

需求文档：
{requirement_text}

请提取以下类别的测试点：
1. 功能测试点（functional_points）：核心功能和业务逻辑
2. 边界测试点（boundary_points）：边界值、极限情况
3. 异常测试点（exception_points）：错误处理、异常场景
4. 性能测试点（performance_points）：性能要求、响应时间
5. 安全测试点（security_points）：安全性、权限控制

**重要：请严格按照以下JSON格式输出，不要有任何额外的逗号或格式错误：**

```json
{{
  "functional_points": [
    {{"name": "测试点名称", "description": "测试点描述", "priority": "High"}}
  ],
  "boundary_points": [
    {{"name": "测试点名称", "description": "测试点描述", "priority": "Medium"}}
  ],
  "exception_points": [
    {{"name": "测试点名称", "description": "测试点描述", "priority": "High"}}
  ],
  "performance_points": [],
  "security_points": []
}}
```

注意：
- 每个测试点必须包含name、description、priority三个字段
- priority只能是High、Medium或Low
- 数组最后一个元素后面不要有逗号
- 如果某个类别没有测试点，使用空数组[]
"""
    
    def _get_test_point_system_prompt(self) -> str:
        """获取测试点提取的系统提示"""
        return """你是一个专业的测试分析专家，擅长从需求文档中识别测试点。
你需要全面、细致地分析需求，识别所有可能的测试场景，包括正常流程、异常流程、边界条件等。
请以结构化的JSON格式输出测试点。"""
    
    def _fix_json_string(self, json_str: str) -> str:
        """修复常见的JSON格式错误"""
        # 移除尾部逗号
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        
        # 修复单引号为双引号
        # json_str = json_str.replace("'", '"')
        
        # 移除注释
        json_str = re.sub(r'//.*?\n', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
        
        return json_str
    
    def _parse_test_points(self, llm_response: str) -> Dict[str, List[Dict]]:
        """解析LLM返回的测试点"""
        try:
            logger.info(f"开始解析测试点，响应长度: {len(llm_response)}")
            
            # 尝试提取JSON代码块
            json_pattern = r'```json\s*(.*?)\s*```'
            matches = re.findall(json_pattern, llm_response, re.DOTALL)
            if matches:
                logger.info("找到JSON代码块，尝试解析...")
                json_str = self._fix_json_string(matches[0])
                try:
                    result = json.loads(json_str)
                    logger.info(f"✅ JSON解析成功，包含 {len(result)} 个类别")
                    return result
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON代码块解析失败: {e}")
                    logger.debug(f"JSON内容: {json_str[:200]}...")
            
            # 尝试直接查找JSON对象
            start = llm_response.find('{')
            end = llm_response.rfind('}')
            if start != -1 and end != -1:
                json_str = llm_response[start:end + 1]
                json_str = self._fix_json_string(json_str)
                logger.info("找到JSON对象，尝试解析...")
                try:
                    result = json.loads(json_str)
                    logger.info(f"✅ JSON解析成功，包含 {len(result)} 个类别")
                    return result
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON对象解析失败: {e}")
                    logger.debug(f"JSON内容: {json_str[:200]}...")
            
            # 如果都失败了，记录响应内容并回退到规则提取
            logger.warning("无法解析LLM响应为JSON格式，使用规则提取")
            logger.debug(f"LLM响应内容: {llm_response[:500]}...")
            return self._rule_based_test_point_extraction(llm_response)
            
        except Exception as e:
            logger.error(f"测试点解析失败: {e}", exc_info=True)
            return self._rule_based_test_point_extraction(llm_response)
    
    def _rule_based_test_point_extraction(self, text: str) -> Dict[str, List[Dict]]:
        """基于规则的测试点提取（回退方案）"""
        return {
            'functional_points': [
                {'name': '基础功能测试', 'description': '验证核心功能', 'priority': 'High'}
            ],
            'boundary_points': [
                {'name': '边界值测试', 'description': '验证边界条件', 'priority': 'Medium'}
            ],
            'exception_points': [
                {'name': '异常处理测试', 'description': '验证异常场景', 'priority': 'High'}
            ],
            'performance_points': [],
            'security_points': []
        }
    
    def _parse_test_case(
        self,
        llm_response: str,
        case_id: int,
        scenario: Dict
    ) -> Dict[str, Any]:
        """解析LLM返回的测试用例"""
        try:
            logger.info(f"开始解析测试用例，响应长度: {len(llm_response)}")
            
            # 尝试提取JSON代码块
            json_pattern = r'```json\s*(.*?)\s*```'
            matches = re.findall(json_pattern, llm_response, re.DOTALL)
            if matches:
                logger.info("找到JSON代码块，尝试解析...")
                json_str = self._fix_json_string(matches[0])
                try:
                    test_case = json.loads(json_str)
                    test_case['id'] = f"TC{case_id:03d}"
                    logger.info(f"✅ 测试用例JSON解析成功")
                    return test_case
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON代码块解析失败: {e}")
                    logger.debug(f"JSON内容: {json_str[:200]}...")
            
            # 尝试直接查找JSON对象
            start = llm_response.find('{')
            end = llm_response.rfind('}')
            if start != -1 and end != -1:
                json_str = llm_response[start:end + 1]
                json_str = self._fix_json_string(json_str)
                logger.info("找到JSON对象，尝试解析...")
                try:
                    test_case = json.loads(json_str)
                    test_case['id'] = f"TC{case_id:03d}"
                    logger.info(f"✅ 测试用例JSON解析成功")
                    return test_case
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON对象解析失败: {e}")
                    logger.debug(f"JSON内容: {json_str[:200]}...")
            
            # 回退到模板
            logger.warning("无法解析LLM响应为JSON格式，使用模板")
            logger.debug(f"LLM响应内容: {llm_response[:500]}...")
            return self._template_test_case(case_id, scenario, 'functional')
            
        except Exception as e:
            logger.error(f"测试用例解析失败: {e}", exc_info=True)
            return self._template_test_case(case_id, scenario, 'functional')


# 导出
__all__ = ['AgentsTestCaseService']
