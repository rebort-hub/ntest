/**
 * 智能测试用例管理模块路由
 */
import Layout from '@/layout/index.vue'

export default [
    // AI聊天助手 - 独立的一级菜单
    {
        path: '/ai-chat',
        component: Layout,
        redirect: '/ai-chat/index',
        name: 'aiChat',
        meta: {
            title: 'AI聊天助手',
            icon: 'ChatLineSquare',
            cache: false
        },
        children: [
            {
                path: 'index',
                name: 'aiChatIndex',
                component: () => import('@/views/aitestrebort/conversations/websocket-chat.vue'),
                meta: {
                    title: 'AI聊天助手',
                    icon: 'ChatLineSquare',
                    cache: true
                }
            }
        ]
    },
    {
        path: '/aitestrebort',
        component: Layout,
        redirect: '/aitestrebort/project',
        name: 'aitestrebort',
        meta: {
            title: 'AI工作空间',
            icon: 'Suitcase',
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
            // 新的项目详情布局
            {
                path: 'project/:projectId',
                name: 'aitestrebortProjectDetail',
                component: () => import('@/views/aitestrebort/project/detail.vue'),
                meta: {
                    title: '项目详情',
                    icon: 'FolderOpened',
                    cache: false,
                    hideMenu: true,
                    hidden: true
                },
                props: true,
                children: [
                    {
                        path: '',
                        redirect: 'overview'
                    },
                    {
                        path: 'overview',
                        name: 'aitestrebortProjectOverview',
                        component: () => import('@/views/aitestrebort/project/overview.vue'),
                        meta: {
                            title: '项目概览',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'testcase',
                        name: 'aitestrebortTestCase',
                        component: () => import('@/views/aitestrebort/testcase/index.vue'),
                        meta: {
                            title: '测试用例',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'testcase/preview',
                        name: 'aitestrebortTestCasePreview',
                        component: () => import('@/views/aitestrebort/testcase/preview.vue'),
                        meta: {
                            title: '预览测试用例',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'automation',
                        name: 'aitestrebortAutomation',
                        component: () => import('@/views/aitestrebort/automation/index.vue'),
                        meta: {
                            title: '自动化脚本',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'test-suite',
                        name: 'aitestrebortTestSuite',
                        component: () => import('@/views/aitestrebort/test-suite/index.vue'),
                        meta: {
                            title: '测试套件管理',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'test-execution',
                        name: 'aitestrebortTestExecution',
                        component: () => import('@/views/aitestrebort/test-execution/index.vue'),
                        meta: {
                            title: '测试执行历史',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'test-execution/:executionId/report',
                        name: 'aitestrebortTestExecutionReport',
                        component: () => import('@/views/aitestrebort/test-execution/report.vue'),
                        meta: {
                            title: '执行报告',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'ai-generator',
                        name: 'aitestrebortAIGenerator',
                        component: () => import('@/views/aitestrebort/ai-generator/index.vue'),
                        meta: {
                            title: 'AI 生成',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'knowledge',
                        name: 'aitestrebortKnowledge',
                        component: () => import('@/views/aitestrebort/knowledge/index.vue'),
                        meta: {
                            title: '知识库管理',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'requirements',
                        name: 'aitestrebortRequirements',
                        component: () => import('@/views/aitestrebort/requirements/index.vue'),
                        meta: {
                            title: '需求管理',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        }
                    },
                    {
                        path: 'requirements/:id',
                        name: 'aitestrebortRequirementDetail',
                        component: () => import('@/views/aitestrebort/requirements/document-detail.vue'),
                        meta: {
                            title: '需求文档详情',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        }
                    },
                    // 高级功能路由
                    {
                        path: 'langgraph-orchestration',
                        name: 'aitestrebortLangGraphOrchestration',
                        component: () => import('@/views/aitestrebort/langgraph-orchestration/index.vue'),
                        meta: {
                            title: 'RAG检索',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'agent-execution',
                        name: 'aitestrebortAgentExecution',
                        component: () => import('@/views/aitestrebort/agent-execution/index.vue'),
                        meta: {
                            title: 'Agent智能执行',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'script-generation',
                        name: 'aitestrebortScriptGeneration',
                        component: () => import('@/views/aitestrebort/script-generation/index.vue'),
                        meta: {
                            title: 'AI脚本生成',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'requirement-retrieval',
                        name: 'aitestrebortRequirementRetrieval',
                        component: () => import('@/views/aitestrebort/requirement-retrieval/index.vue'),
                        meta: {
                            title: 'AI需求检索',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'quality-assessment',
                        name: 'aitestrebortQualityAssessment',
                        component: () => import('@/views/aitestrebort/quality-assessment/index.vue'),
                        meta: {
                            title: 'AI质量评估',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'requirement-review',
                        name: 'aitestrebortRequirementReview',
                        component: () => import('@/views/aitestrebort/requirement-review/index.vue'),
                        meta: {
                            title: 'AI需求评审',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    },
                    {
                        path: 'ai-diagram',
                        name: 'aitestrebortAIDiagram',
                        component: () => import('@/views/aitestrebort/ai-diagram/index.vue'),
                        meta: {
                            title: 'AI图表生成',
                            cache: false,
                            hideMenu: true,
                            hidden: true
                        },
                        props: true
                    }
                ]
            },
            {
                path: 'llm-config',
                name: 'aitestrebortLLMConfig',
                component: () => import('@/views/aitestrebort/llm-config/index.vue'),
                meta: {
                    title: 'LLM配置',
                    icon: 'Connection',
                    cache: true
                }
            },
            {
                path: 'mcp-config',
                name: 'aitestrebortMCPConfig',
                component: () => import('@/views/aitestrebort/mcp-config/index.vue'),
                meta: {
                    title: 'MCP配置',
                    icon: 'Box',
                    cache: true
                }
            },
            {
                path: 'api-keys',
                name: 'aitestrebortAPIKeys',
                component: () => import('@/views/aitestrebort/api-keys/index.vue'),
                meta: {
                    title: 'API密钥管理',
                    icon: 'Link',
                    cache: true
                }
            },
            {
                path: 'conversations',
                name: 'aitestrebortConversations',
                component: () => import('@/views/aitestrebort/conversations/index.vue'),
                meta: {
                    title: 'LLM对话管理',
                    icon: 'Microphone',
                    cache: true
                }
            },
            {
                path: 'stream-chat',
                name: 'aitestrebortStreamChat',
                component: () => import('@/views/aitestrebort/conversations/stream-chat.vue'),
                meta: {
                    title: '聊天(备用)',
                    icon: 'ChatLineRound',
                    cache: true,
                    hideMenu: true  // 隐藏备用页面
                }
            },
            {
                path: 'prompts',
                name: 'aitestrebortPrompts',
                component: () => import('@/views/aitestrebort/prompts/index.vue'),
                meta: {
                    title: '提示词管理',
                    icon: 'Share',
                    cache: true
                }
            }
        ]
    }
]