/**
 * aitestrebort 智能测试用例管理模块路由
 */
import Layout from '@/layout/index.vue'

export default [
    {
        path: '/aitestrebort',
        component: Layout,
        redirect: '/aitestrebort/project',
        name: 'aitestrebort',
        meta: {
            title: 'AI驱动生成管理',
            icon: 'Microphone',
            cache: false
        },
        children: [
            {
                path: 'project',
                name: 'aitestrebortProject',
                component: () => import('@/views/aitestrebort/project/index.vue'),
                meta: {
                    title: '项目管理',
                    icon: 'FolderOpened',
                    cache: true
                }
            },
            {
                path: 'project/:projectId/testcase',
                name: 'aitestrebortTestCase',
                component: () => import('@/views/aitestrebort/testcase/index.vue'),
                meta: {
                    title: '测试用例',
                    icon: 'Document',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'project/:projectId/testcase/preview',
                name: 'aitestrebortTestCasePreview',
                component: () => import('@/views/aitestrebort/testcase/preview.vue'),
                meta: {
                    title: '测试用例预览',
                    icon: 'View',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'project/:projectId/automation',
                name: 'aitestrebortAutomation',
                component: () => import('@/views/aitestrebort/automation/index.vue'),
                meta: {
                    title: '自动化脚本',
                    icon: 'Document',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'project/:projectId/ai-generator',
                name: 'aitestrebortAIGenerator',
                component: () => import('@/views/aitestrebort/ai-generator/index.vue'),
                meta: {
                    title: 'AI 生成',
                    icon: 'MagicStick',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'project/:projectId/knowledge',
                name: 'aitestrebortKnowledge',
                component: () => import('@/views/aitestrebort/knowledge/index.vue'),
                meta: {
                    title: '知识库管理',
                    icon: 'Collection',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'llm-config',
                name: 'aitestrebortLLMConfig',
                component: () => import('@/views/aitestrebort/llm-config/index.vue'),
                meta: {
                    title: 'LLM 厂商配置',
                    icon: 'Refrigerator',
                    cache: true
                }
            },
            {
                path: 'mcp-config',
                name: 'aitestrebortMCPConfig',
                component: () => import('@/views/aitestrebort/mcp-config/index.vue'),
                meta: {
                    title: 'MCP 配置管理',
                    icon: 'Link',
                    cache: true
                }
            },
            {
                path: 'api-keys',
                name: 'aitestrebortAPIKeys',
                component: () => import('@/views/aitestrebort/api-keys/index.vue'),
                meta: {
                    title: 'API 密钥管理',
                    icon: 'Key',
                    cache: true
                }
            },
            {
                path: 'conversations',
                name: 'aitestrebortConversations',
                component: () => import('@/views/aitestrebort/conversations/index.vue'),
                meta: {
                    title: 'NT-聊天服务',
                    icon: 'Microphone',
                    cache: true
                }
            },

            {
                path: 'prompts',
                name: 'aitestrebortPrompts',
                component: () => import('@/views/aitestrebort/prompts/index.vue'),
                meta: {
                    title: '提示词管理',
                    icon: 'Document',
                    cache: true
                }
            },
            // 测试路由
            {
                path: 'project/:projectId/test-advanced',
                name: 'aitestrebortTestAdvanced',
                component: () => import('@/views/aitestrebort/test-advanced/index.vue'),
                meta: {
                    title: '高级功能测试',
                    icon: 'Test',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            // 高级功能路由
            {
                path: 'project/:projectId/langgraph-orchestration',
                name: 'aitestrebortLangGraphOrchestration',
                component: () => import('@/views/aitestrebort/langgraph-orchestration/index.vue'),
                meta: {
                    title: 'LangGraph智能编排',
                    icon: 'Connection',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'project/:projectId/agent-execution',
                name: 'aitestrebortAgentExecution',
                component: () => import('@/views/aitestrebort/agent-execution/index.vue'),
                meta: {
                    title: 'Agent智能执行',
                    icon: 'Cpu',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'project/:projectId/script-generation',
                name: 'aitestrebortScriptGeneration',
                component: () => import('@/views/aitestrebort/script-generation/index.vue'),
                meta: {
                    title: '智能脚本生成',
                    icon: 'DocumentAdd',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'project/:projectId/requirement-retrieval',
                name: 'aitestrebortRequirementRetrieval',
                component: () => import('@/views/aitestrebort/requirement-retrieval/index.vue'),
                meta: {
                    title: '智能需求检索',
                    icon: 'Search',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'project/:projectId/quality-assessment',
                name: 'aitestrebortQualityAssessment',
                component: () => import('@/views/aitestrebort/quality-assessment/index.vue'),
                meta: {
                    title: '质量评估系统',
                    icon: 'Medal',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            // 需求管理路由
            {
                path: 'project/:projectId/requirements',
                name: 'aitestrebortRequirements',
                component: () => import('@/views/aitestrebort/requirements/index.vue'),
                meta: {
                    title: '需求管理',
                    icon: 'Document',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            {
                path: 'project/:projectId/requirements/:documentId',
                name: 'aitestrebortRequirementDetail',
                component: () => import('@/views/aitestrebort/requirements/document-detail.vue'),
                meta: {
                    title: '需求文档详情',
                    icon: 'View',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            // AI图表生成路由
            {
                path: 'project/:projectId/ai-diagram',
                name: 'aitestrebortAIDiagram',
                component: () => import('@/views/aitestrebort/ai-diagram/index.vue'),
                meta: {
                    title: 'AI图表生成',
                    icon: 'PieChart',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            // 测试套件管理路由
            {
                path: 'project/:projectId/test-suite',
                name: 'aitestrebortTestSuite',
                component: () => import('@/views/aitestrebort/test-suite/index.vue'),
                meta: {
                    title: '测试套件管理',
                    icon: 'Collection',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            // 测试执行历史路由
            {
                path: 'project/:projectId/test-execution',
                name: 'aitestrebortTestExecution',
                component: () => import('@/views/aitestrebort/test-execution/index.vue'),
                meta: {
                    title: '测试执行历史',
                    icon: 'Timer',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            },
            // 测试执行报告页面
            {
                path: 'project/:projectId/test-execution/:executionId/report',
                name: 'aitestrebortExecutionReport',
                component: () => import('@/views/aitestrebort/test-execution/report.vue'),
                meta: {
                    title: '执行报告',
                    icon: 'Document',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true
            }
        ]
    }
]