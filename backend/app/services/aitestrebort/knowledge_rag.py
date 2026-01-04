"""
知识库RAG集成服务
提供知识检索增强生成功能
"""
import logging
from typing import List, Dict, Optional, Any
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage

logger = logging.getLogger(__name__)


class KnowledgeRAGService:
    """
    知识库RAG服务
    提供知识检索和问答功能
    """
    
    def __init__(self, project_id: int, user_id: int):
        """
        初始化RAG服务
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
        """
        self.project_id = project_id
        self.user_id = user_id
        self.knowledge_bases = []
    
    async def load_knowledge_bases(self):
        """
        加载项目的知识库
        """
        try:
            # TODO: 从数据库加载知识库配置
            # 这里需要根据实际的知识库模型实现
            logger.info(f"Loading knowledge bases for project {self.project_id}")
            
            # 示例：假设有知识库模型
            # from app.models.aitestrebort import aitestrebortKnowledgeBase
            # self.knowledge_bases = await aitestrebortKnowledgeBase.filter(
            #     project_id=self.project_id,
            #     is_active=True
            # ).all()
            
            logger.info(f"Loaded {len(self.knowledge_bases)} knowledge bases")
            
        except Exception as e:
            logger.error(f"Failed to load knowledge bases: {e}", exc_info=True)
    
    async def search_knowledge(
        self,
        query: str,
        top_k: int = 5,
        knowledge_base_ids: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            knowledge_base_ids: 指定的知识库ID列表（可选）
            
        Returns:
            检索结果列表
        """
        try:
            logger.info(f"Searching knowledge: query='{query}', top_k={top_k}")
            
            # TODO: 实现实际的向量检索逻辑
            # 这里需要根据实际的向量数据库实现
            
            # 示例返回格式
            results = []
            
            # 模拟检索结果
            # results = [
            #     {
            #         "content": "检索到的文档内容",
            #         "metadata": {
            #             "source": "文档来源",
            #             "score": 0.95,
            #             "knowledge_base_id": 1
            #         }
            #     }
            # ]
            
            logger.info(f"Found {len(results)} knowledge documents")
            return results
            
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}", exc_info=True)
            return []
    
    async def answer_with_knowledge(
        self,
        question: str,
        llm,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        基于知识库回答问题
        
        Args:
            question: 问题
            llm: LLM实例
            top_k: 检索文档数量
            
        Returns:
            回答结果
        """
        try:
            # 1. 检索相关知识
            knowledge_docs = await self.search_knowledge(question, top_k)
            
            if not knowledge_docs:
                return {
                    "answer": "抱歉，未找到相关知识。",
                    "sources": [],
                    "has_knowledge": False
                }
            
            # 2. 构建RAG提示
            context = "\n\n".join([
                f"文档 {i+1}:\n{doc['content']}"
                for i, doc in enumerate(knowledge_docs)
            ])
            
            rag_prompt = f"""基于以下知识库内容回答问题：

知识库内容：
{context}

问题：{question}

请基于上述知识库内容回答问题。如果知识库中没有相关信息，请明确说明。"""
            
            # 3. 调用LLM生成回答
            messages = [HumanMessage(content=rag_prompt)]
            response = await llm.ainvoke(messages)
            
            answer = response.content if hasattr(response, 'content') else str(response)
            
            # 4. 返回结果
            return {
                "answer": answer,
                "sources": [
                    {
                        "content": doc["content"][:200] + "...",
                        "metadata": doc.get("metadata", {})
                    }
                    for doc in knowledge_docs
                ],
                "has_knowledge": True,
                "knowledge_count": len(knowledge_docs)
            }
            
        except Exception as e:
            logger.error(f"RAG answer failed: {e}", exc_info=True)
            return {
                "answer": f"回答生成失败: {str(e)}",
                "sources": [],
                "has_knowledge": False
            }


class ConversationalRAGService(KnowledgeRAGService):
    """
    对话式RAG服务
    支持多轮对话的知识检索
    """
    
    def __init__(self, project_id: int, user_id: int):
        super().__init__(project_id, user_id)
        self.conversation_history = []
    
    def add_to_history(self, role: str, content: str):
        """
        添加对话历史
        
        Args:
            role: 角色（user/assistant）
            content: 内容
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        # 限制历史长度
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    async def answer_with_context(
        self,
        question: str,
        llm,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        基于对话上下文和知识库回答问题
        
        Args:
            question: 问题
            llm: LLM实例
            top_k: 检索文档数量
            
        Returns:
            回答结果
        """
        # 添加用户问题到历史
        self.add_to_history("user", question)
        
        # 使用基础RAG功能
        result = await self.answer_with_knowledge(question, llm, top_k)
        
        # 添加AI回答到历史
        if result.get("has_knowledge"):
            self.add_to_history("assistant", result["answer"])
        
        return result


def create_knowledge_tool(project_id: int, user_id: int):
    """
    创建知识检索工具（用于Agent）
    
    Args:
        project_id: 项目ID
        user_id: 用户ID
        
    Returns:
        LangChain Tool
    """
    rag_service = KnowledgeRAGService(project_id, user_id)
    
    @tool
    async def search_project_knowledge(query: str, top_k: int = 5) -> str:
        """
        搜索项目知识库
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            
        Returns:
            检索结果的文本描述
        """
        results = await rag_service.search_knowledge(query, top_k)
        
        if not results:
            return "未找到相关知识。"
        
        # 格式化结果
        formatted = []
        for i, doc in enumerate(results, 1):
            content = doc.get("content", "")
            metadata = doc.get("metadata", {})
            score = metadata.get("score", 0)
            
            formatted.append(
                f"文档 {i} (相关度: {score:.2f}):\n{content}\n"
            )
        
        return "\n".join(formatted)
    
    return search_project_knowledge


class LangGraphKnowledgeIntegration:
    """
    LangGraph知识库集成
    提供与LangGraph Agent的集成接口
    """
    
    @staticmethod
    def create_knowledge_tools(project_id: int, user_id: int) -> List:
        """
        创建知识库相关的工具列表
        
        Args:
            project_id: 项目ID
            user_id: 用户ID
            
        Returns:
            工具列表
        """
        tools = []
        
        # 添加知识检索工具
        search_tool = create_knowledge_tool(project_id, user_id)
        tools.append(search_tool)
        
        logger.info(f"Created {len(tools)} knowledge tools for project {project_id}")
        return tools
    
    @staticmethod
    async def enhance_conversation_with_knowledge(
        messages: List,
        project_id: int,
        user_id: int,
        llm,
        auto_retrieve: bool = True
    ) -> List:
        """
        使用知识库增强对话
        
        Args:
            messages: 原始消息列表
            project_id: 项目ID
            user_id: 用户ID
            llm: LLM实例
            auto_retrieve: 是否自动检索知识
            
        Returns:
            增强后的消息列表
        """
        if not auto_retrieve:
            return messages
        
        try:
            # 获取最后一条用户消息
            last_user_message = None
            for msg in reversed(messages):
                if isinstance(msg, HumanMessage):
                    last_user_message = msg
                    break
            
            if not last_user_message:
                return messages
            
            # 检索相关知识
            rag_service = KnowledgeRAGService(project_id, user_id)
            await rag_service.load_knowledge_bases()
            
            knowledge_docs = await rag_service.search_knowledge(
                last_user_message.content,
                top_k=3
            )
            
            if knowledge_docs:
                # 在消息中添加知识上下文
                knowledge_context = "\n\n".join([
                    f"[知识库参考 {i+1}]\n{doc['content']}"
                    for i, doc in enumerate(knowledge_docs)
                ])
                
                # 创建增强的消息
                enhanced_message = HumanMessage(
                    content=f"{last_user_message.content}\n\n{knowledge_context}",
                    additional_kwargs={
                        "has_knowledge": True,
                        "knowledge_count": len(knowledge_docs)
                    }
                )
                
                # 替换最后一条消息
                enhanced_messages = messages[:-1] + [enhanced_message]
                
                logger.info(f"Enhanced conversation with {len(knowledge_docs)} knowledge docs")
                return enhanced_messages
            
        except Exception as e:
            logger.error(f"Failed to enhance with knowledge: {e}", exc_info=True)
        
        return messages
