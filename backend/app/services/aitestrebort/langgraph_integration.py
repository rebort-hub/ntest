"""
LangGraph智能编排服务
提供Agent Loop、上下文压缩、状态管理等高级功能
"""
import asyncio
import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Annotated
from datetime import datetime

from langchain_core.documents import Document as LangChainDocument
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver

from app.models.aitestrebort.knowledge import aitestrebortKnowledgeBase
from .knowledge_enhanced import KnowledgeBaseService
from .vector_store import VectorStoreManager

logger = logging.getLogger(__name__)


class RAGState(TypedDict):
    """RAG状态定义"""
    messages: Annotated[List, add_messages]
    question: str
    knowledge_base_id: str
    context: List[Dict[str, Any]]
    answer: str
    retrieval_time: float
    generation_time: float
    total_time: float
    # 新增字段
    project_id: str
    user_id: str
    thread_id: str
    use_knowledge_base: bool
    similarity_threshold: float
    top_k: int


class AgentState(TypedDict):
    """Agent状态定义"""
    messages: Annotated[List, add_messages]
    goal: str
    project_id: str
    knowledge_base_id: str
    use_knowledge_base: bool
    current_step: int
    max_steps: int
    context: Dict[str, Any]
    tool_results: List[Dict[str, Any]]
    is_final: bool
    error_message: str


class CompressionSettings:
    """压缩配置参数"""
    def __init__(self):
        self.max_context_tokens = 128000
        self.trigger_ratio = 0.75  # 达到75%时触发压缩
        self.preserve_recent_messages = 4  # 保留最近4条消息
        self.min_messages_to_compress = 2  # 至少有2条消息才能压缩
        self.summary_prefix = "对话历史摘要"
        self.reserved_tokens = 4000


class CompressionResult:
    """压缩结果"""
    def __init__(self, messages: List[BaseMessage], summary_message: Optional[SystemMessage] = None,
                 state_updates: Dict[str, Any] = None, triggered: bool = False, token_count: int = 0):
        self.messages = messages
        self.summary_message = summary_message
        self.state_updates = state_updates or {}
        self.triggered = triggered
        self.token_count = token_count


class ConversationCompressor:
    """对话上下文压缩器"""

    def __init__(self, llm, model_name: str, settings: Optional[CompressionSettings] = None):
        self.llm = llm
        self.model_name = model_name or getattr(llm, "model_name", "gpt-4o")
        self.settings = settings or CompressionSettings()

    async def prepare(
        self,
        messages: List[BaseMessage],
        summary_text: Optional[str] = None,
        summarized_count: int = 0,
    ) -> CompressionResult:
        """
        准备上下文：检查是否需要压缩，如需则执行压缩
        
        Args:
            messages: 当前完整消息历史
            summary_text: 已有的摘要文本
            summarized_count: 已被摘要覆盖的消息数量
        
        Returns:
            CompressionResult: 压缩结果
        """
        normalized_messages = list(messages or [])
        incoming_summary = summary_text or None
        incoming_count = summarized_count or 0

        # 计算可用Token空间
        available_tokens = max(
            self.settings.max_context_tokens - self.settings.reserved_tokens, 1000
        )
        
        # 计算现有摘要的Token数
        summary_tokens = (
            self._count_tokens(incoming_summary)
            if incoming_summary else 0
        )
        
        # 计算总Token数
        raw_token_count = self._estimate_token_count(normalized_messages) + summary_tokens
        trigger_tokens = int(available_tokens * self.settings.trigger_ratio)

        summary_value = incoming_summary
        new_summarized_count = incoming_count
        summary_updated = False
        
        # 计算当前使用率
        usage_ratio = raw_token_count / available_tokens if available_tokens > 0 else 0

        # 判断是否需要压缩
        if raw_token_count > trigger_tokens and len(normalized_messages) >= self.settings.min_messages_to_compress:
            # 计算需要保留的消息数量
            if usage_ratio > 0.9:
                preserve_count = max(2, self.settings.preserve_recent_messages // 2)
                logger.info(f"高使用率({usage_ratio*100:.1f}%)，激进压缩模式，保留{preserve_count}条消息")
            else:
                preserve_count = self.settings.preserve_recent_messages
            
            cutoff = max(len(normalized_messages) - preserve_count, 0)
            
            # 检查是否有新的消息需要摘要
            if cutoff > new_summarized_count:
                block = normalized_messages[new_summarized_count:cutoff]
                block_summary = await self._summarize_block(block)
                
                if block_summary:
                    summary_value = self._merge_summary(summary_value, block_summary)
                    new_summarized_count = cutoff
                    summary_updated = True
                    logger.info(
                        "对话上下文已压缩：覆盖消息#0-#%s，保留最近%s条",
                        cutoff, preserve_count
                    )
                    
                    # 检查摘要是否过长，如果是则重新压缩摘要
                    summary_tokens = self._count_tokens(summary_value)
                    max_summary_tokens = int(available_tokens * 0.3)
                    if summary_tokens > max_summary_tokens:
                        logger.info(f"摘要过长({summary_tokens} tokens)，重新压缩...")
                        summary_value = await self._recompress_summary(summary_value)
                        logger.info(f"摘要重压缩完成")

        # 构建最终消息列表
        if summary_value:
            summary_message = SystemMessage(
                content=f"【{self.settings.summary_prefix}】\n\n{summary_value}",
                additional_kwargs={"agent": "context_summary", "is_summary": True},
            )
            preserved_messages = normalized_messages[new_summarized_count:]
            context_messages: List[BaseMessage] = [summary_message] + list(preserved_messages)
        else:
            summary_message = None
            context_messages = normalized_messages

        # 计算最终Token数
        final_token_count = self._estimate_token_count(context_messages)
        
        # 构建状态更新
        state_updates: Dict[str, Any] = {"context_token_count": final_token_count}
        if summary_value != incoming_summary:
            state_updates["context_summary"] = summary_value
        if new_summarized_count != incoming_count:
            state_updates["summarized_message_count"] = new_summarized_count

        return CompressionResult(
            messages=context_messages,
            summary_message=summary_message,
            state_updates=state_updates,
            triggered=summary_updated,
            token_count=final_token_count,
        )

    def _message_to_text(self, message: BaseMessage) -> str:
        """将消息转换为文本"""
        role = getattr(message, "type", message.__class__.__name__)
        agent = getattr(message, "additional_kwargs", {}).get("agent")
        label = agent or role
        body = self._normalize_content(getattr(message, "content", ""))
        return f"[{label}] {body}".strip()

    def _normalize_content(self, content) -> str:
        """标准化消息内容"""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = [self._normalize_content(item) for item in content if item]
            return "\n".join([part for part in parts if part])
        if isinstance(content, dict):
            try:
                return json.dumps(content, ensure_ascii=False)
            except TypeError:
                return str(content)
        return str(content or "")

    def _estimate_token_count(self, messages: List[BaseMessage]) -> int:
        """估算消息列表的Token总数"""
        total = 0
        for msg in messages:
            text = self._message_to_text(msg)
            if text:
                total += self._count_tokens(text)
        return total

    def _count_tokens(self, text: str) -> int:
        """简单的Token计数估算"""
        if not text:
            return 0
        # 简单估算：中文按字符数，英文按单词数*1.3
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.replace('\n', ' ').split()) - chinese_chars
        return chinese_chars + int(english_words * 1.3)

    def _merge_summary(self, existing: Optional[str], new_block: str) -> str:
        """合并摘要"""
        if existing:
            return f"{existing}\n\n---\n\n{new_block}"
        return new_block

    async def _recompress_summary(self, long_summary: str) -> str:
        """当摘要本身过长时，重新生成更简洁的摘要"""
        try:
            prompt = f"""以下是一段对话历史的摘要，请将其压缩为更简洁的版本，只保留最关键的信息：

{long_summary}

请生成一个更简洁的摘要，保留核心上下文信息。"""

            response = await self.llm.ainvoke([
                SystemMessage(content="你是一个专业的摘要压缩助手，擅长提炼关键信息。"),
                HumanMessage(content=prompt)
            ])
            
            return response.content.strip() if hasattr(response, 'content') else str(response).strip()
        except Exception as e:
            logger.error("摘要重压缩失败: %s", e)
            # 回退：截取前半部分
            return long_summary[:len(long_summary)//2] + "\n[历史摘要已截断]"

    async def _summarize_block(self, block: List[BaseMessage]) -> str:
        """对消息块生成结构化摘要"""
        if not block:
            return ""

        try:
            # 合并文档内容
            combined_content = "\n\n".join([self._message_to_text(msg) for msg in block])
            
            # 使用结构化提示词生成摘要
            summary_prompt = f"""请将以下对话内容压缩成简洁的摘要，保留关键信息。

对话内容：
{combined_content}

请按以下格式生成摘要：
1. 已完成事项：（列出已讨论或完成的要点）
2. 当前状态：（当前讨论到的位置或状态）
3. 待处理事项：（如有提到需要后续处理的事项）

请用简洁的语言概括，保持专业性。"""

            # 直接调用 LLM 生成摘要
            response = await self.llm.ainvoke([
                SystemMessage(content="你是一个专业的对话摘要助手，擅长提取对话中的关键信息。"),
                HumanMessage(content=summary_prompt)
            ])
            
            return response.content.strip() if hasattr(response, 'content') else str(response).strip()
            
        except Exception as e:
            logger.error("摘要生成失败: %s", e, exc_info=True)
            # 回退：简单截断
            combined = "\n".join([self._message_to_text(msg) for msg in block[:3]])
            return f"[摘要生成失败，保留前3条消息概要]\n{combined[:500]}..."


class KnowledgeRAGService:
    """知识库RAG服务"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.graph = self._build_rag_graph()

    def _build_rag_graph(self) -> StateGraph:
        """构建RAG图"""
        graph_builder = StateGraph(RAGState)

        # 添加节点
        graph_builder.add_node("retrieve", self._retrieve_node)
        graph_builder.add_node("generate", self._generate_node)

        # 设置边
        graph_builder.add_edge(START, "retrieve")
        graph_builder.add_edge("retrieve", "generate")
        graph_builder.add_edge("generate", END)

        return graph_builder.compile()

    async def _retrieve_node(self, state: RAGState) -> Dict[str, Any]:
        """检索节点"""
        start_time = time.time()

        try:
            # 检查是否需要使用知识库
            if not state.get("use_knowledge_base", True):
                logger.info("跳过知识库检索")
                return {
                    "context": [],
                    "retrieval_time": time.time() - start_time
                }

            # 获取知识库
            knowledge_base_id = state.get("knowledge_base_id")
            if not knowledge_base_id:
                logger.warning("未提供知识库ID")
                return {
                    "context": [],
                    "retrieval_time": time.time() - start_time
                }

            # 获取检索参数
            top_k = state.get("top_k", 5)
            similarity_threshold = state.get("similarity_threshold", 0.7)

            # 执行检索
            kb_service = KnowledgeBaseService(knowledge_base_id)
            await kb_service.initialize()
            
            search_results = await kb_service.search_knowledge(
                state["question"], top_k
            )

            retrieval_time = time.time() - start_time

            logger.info(f"检索完成: 找到 {len(search_results)} 个相关片段，耗时 {retrieval_time:.3f}s")

            return {
                "context": search_results,
                "retrieval_time": retrieval_time
            }

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return {
                "context": [],
                "retrieval_time": time.time() - start_time
            }

    async def _generate_node(self, state: RAGState) -> Dict[str, Any]:
        """生成节点"""
        start_time = time.time()

        try:
            # 构建上下文
            context_sources = state.get("context", [])
            context_text = ""

            if context_sources:
                # 构建详细的上下文信息
                context_parts = []
                for i, result in enumerate(context_sources[:3], 1):
                    content = result.get("content", "")
                    score = result.get("similarity_score", 0.0)
                    metadata = result.get("metadata", {})
                    source = metadata.get("source", "未知来源")

                    context_parts.append(f"[来源{i}: {source} (相似度: {score:.2f})]\n{content}")

                context_text = "\n\n".join(context_parts)

            # 构建提示
            if context_text:
                system_prompt = """你是一个智能助手，请基于提供的上下文信息回答用户的问题。

请遵循以下原则：
1. 优先使用上下文信息中的内容回答问题
2. 如果上下文信息不足以完整回答问题，请明确说明
3. 保持回答准确、简洁且有帮助
4. 可以适当引用来源信息
5. 如果问题与上下文完全无关，请说明并提供一般性建议

上下文信息：
{context}"""

                messages = [
                    SystemMessage(content=system_prompt.format(context=context_text)),
                    HumanMessage(content=state["question"])
                ]

                logger.info(f"使用知识库上下文生成回答，上下文长度: {len(context_text)}")
            else:
                system_prompt = """你是一个智能助手，请回答用户的问题。
由于没有找到相关的知识库信息，请基于你的一般知识回答，并明确说明这不是基于特定文档的回答。"""

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=state["question"])
                ]

                logger.info("未找到相关上下文，使用一般知识回答")

            # 生成回答
            response = await self.llm.ainvoke(messages)
            generation_time = time.time() - start_time

            logger.info(f"回答生成完成，耗时 {generation_time:.3f}s")

            return {
                "answer": response.content,
                "generation_time": generation_time,
                "messages": [AIMessage(content=response.content)]
            }

        except Exception as e:
            logger.error(f"生成回答失败: {e}")
            error_message = "抱歉，生成回答时出现错误。请稍后重试。"
            return {
                "answer": error_message,
                "generation_time": time.time() - start_time,
                "messages": [AIMessage(content=error_message)]
            }

    async def query(self, question: str, knowledge_base_id: str = None, user=None,
                   project_id: str = None, thread_id: str = None,
                   use_knowledge_base: bool = True, similarity_threshold: float = 0.7,
                   top_k: int = 5) -> Dict[str, Any]:
        """执行RAG查询"""
        start_time = time.time()

        initial_state = {
            "messages": [HumanMessage(content=question)],
            "question": question,
            "knowledge_base_id": knowledge_base_id or "",
            "context": [],
            "answer": "",
            "retrieval_time": 0.0,
            "generation_time": 0.0,
            "total_time": 0.0,
            # 新增参数
            "project_id": project_id or "",
            "user_id": str(user.id) if user else "",
            "thread_id": thread_id or "",
            "use_knowledge_base": use_knowledge_base,
            "similarity_threshold": similarity_threshold,
            "top_k": top_k
        }

        try:
            logger.info(f"开始RAG查询: {question[:50]}...")
            logger.info(f"知识库ID: {knowledge_base_id}, 使用知识库: {use_knowledge_base}")

            # 执行图
            final_state = await self.graph.ainvoke(initial_state)

            # 计算总时间
            total_time = time.time() - start_time
            final_state["total_time"] = total_time

            logger.info(f"RAG查询完成，总耗时: {total_time:.3f}s")

            return final_state

        except Exception as e:
            logger.error(f"RAG查询失败: {e}")
            error_response = {
                "question": question,
                "answer": "抱歉，查询过程中出现错误。",
                "context": [],
                "retrieval_time": 0.0,
                "generation_time": 0.0,
                "total_time": time.time() - start_time
            }
            return error_response


class LangGraphKnowledgeIntegration:
    """LangGraph对话系统的知识库集成"""

    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.rag_service = KnowledgeRAGService(llm)
        self.compressor = ConversationCompressor(llm, getattr(llm, 'model_name', 'gpt-4o'))

    def create_knowledge_enhanced_agent(self, project_id: str, knowledge_base_id: str = None):
        """创建知识库增强的对话代理"""
        
        def should_use_knowledge_base(state: AgentState) -> str:
            """判断是否需要使用知识库"""
            if not state.get("use_knowledge_base", True):
                return "chat_only"

            if not state.get("knowledge_base_id"):
                return "chat_only"

            # 获取最新的用户消息
            user_messages = [msg for msg in state["messages"]
                           if hasattr(msg, 'type') and msg.type == 'human']

            if not user_messages:
                return "chat_only"

            latest_message = user_messages[-1].content

            # 简单的关键词检测，判断是否需要知识库
            knowledge_keywords = [
                "什么是", "如何", "怎么", "为什么", "解释", "定义",
                "原理", "方法", "步骤", "流程", "文档", "资料"
            ]

            if any(keyword in latest_message for keyword in knowledge_keywords):
                return "rag_chat"
            else:
                return "chat_only"

        async def rag_chat_node(state: AgentState) -> AgentState:
            """RAG增强的对话节点"""
            try:
                # 获取最新的用户消息
                user_messages = [msg for msg in state["messages"]
                               if hasattr(msg, 'type') and msg.type == 'human']

                if not user_messages:
                    return state

                latest_message = user_messages[-1].content

                # 执行RAG查询
                rag_result = await self.rag_service.query(
                    question=latest_message,
                    knowledge_base_id=state.get("knowledge_base_id"),
                    use_knowledge_base=True,
                    similarity_threshold=0.6,
                    top_k=3
                )

                # 更新消息
                new_messages = rag_result.get("messages", [])
                return {
                    "messages": new_messages
                }

            except Exception as e:
                logger.error(f"RAG对话节点失败: {e}")
                # 降级到普通对话
                return await chat_only_node(state)

        async def chat_only_node(state: AgentState) -> AgentState:
            """纯对话节点"""
            try:
                response = await self.llm.ainvoke(state["messages"])
                return {
                    "messages": [response]
                }
            except Exception as e:
                logger.error(f"对话节点失败: {e}")
                error_msg = AIMessage(content="抱歉，我遇到了一些问题，请稍后重试。")
                return {
                    "messages": [error_msg]
                }

        # 构建图
        graph_builder = StateGraph(AgentState)

        # 添加节点
        graph_builder.add_node("rag_chat", rag_chat_node)
        graph_builder.add_node("chat_only", chat_only_node)

        # 设置条件边
        graph_builder.add_conditional_edges(
            START,
            should_use_knowledge_base,
            {
                "rag_chat": "rag_chat",
                "chat_only": "chat_only"
            }
        )

        # 设置结束边
        graph_builder.add_edge("rag_chat", END)
        graph_builder.add_edge("chat_only", END)

        return graph_builder.compile()

    async def get_project_knowledge_bases(self, project_id: str) -> List[Dict[str, Any]]:
        """获取项目的知识库列表"""
        try:
            # 直接通过project_id查询知识库，不需要先获取项目对象
            knowledge_bases = await aitestrebortKnowledgeBase.filter(
                project_id=int(project_id), is_active=True
            ).all()

            return [{
                "id": str(kb.id),
                "name": kb.name,
                "description": kb.description or "",
                "document_count": 0,  # TODO: 计算文档数量
                "created_at": kb.created_at.isoformat()
            } for kb in knowledge_bases]

        except Exception as e:
            logger.error(f"获取项目知识库失败: {e}")
            return []


def create_knowledge_tool(knowledge_base_id: str, user, similarity_threshold: float = 0.5, top_k: int = 5):
    """创建知识库工具，用于Agent调用"""
    from langchain_core.tools import tool

    @tool
    async def knowledge_search(query: str) -> str:
        """
        搜索知识库获取相关信息

        Args:
            query: 搜索查询字符串

        Returns:
            str: 搜索结果，包含相关文档内容
        """
        try:
            logger.info(f"知识库工具被调用: {query[:50]}...")

            # 获取知识库服务
            kb_service = KnowledgeBaseService(knowledge_base_id)
            await kb_service.initialize()

            # 执行检索
            search_results = await kb_service.search_knowledge(query, top_k)

            if not search_results:
                return "未找到相关信息。"

            # 格式化结果
            formatted_results = []
            for i, result in enumerate(search_results[:3], 1):
                content = result.get("content", "")
                score = result.get("similarity_score", 0.0)
                metadata = result.get("metadata", {})
                source = metadata.get("source", "未知来源")

                # 将相似度转换为百分比显示
                similarity_percentage = score * 100
                formatted_results.append(
                    f"[结果{i}] (相似度: {similarity_percentage:.1f}%, 来源: {source})\n{content}"
                )

            result_text = "\n\n".join(formatted_results)
            logger.info(f"知识库工具返回 {len(search_results)} 个结果")

            return result_text

        except Exception as e:
            logger.error(f"知识库工具调用失败: {e}")
            return f"知识库搜索失败: {str(e)}"

    # 设置工具的名称和描述
    knowledge_search.name = "knowledge_search"
    knowledge_search.description = f"搜索知识库 {knowledge_base_id} 获取相关信息。当用户询问特定知识、文档内容或需要查找资料时使用此工具。"

    return knowledge_search