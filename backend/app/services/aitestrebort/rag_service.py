"""
RAG (Retrieval-Augmented Generation) 服务
提供基于知识库的问答功能
"""
import logging
import time
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import json

logger = logging.getLogger(__name__)


# 预定义的 Prompt 模板
PROMPT_TEMPLATES = {
    'default': """你是一个专业的AI助手，擅长根据提供的文档内容回答问题。

请遵循以下规则：
1. **仔细阅读参考文档**：认真分析提供的所有参考文档内容
2. **基于事实回答**：回答必须基于文档内容，不要编造信息
3. **结构化回答**：使用清晰的结构组织答案（如：要点列表、步骤说明等）
4. **引用来源**：在回答中适当引用文档原文，增强可信度
5. **承认不确定**：如果文档中没有相关信息，请明确说明
6. **保持专业**：使用专业、准确的语言
7. **完整回答**：确保回答完整，涵盖问题的所有方面

回答格式建议：
- 使用 **粗体** 强调重点
- 使用列表组织多个要点
- 使用代码块展示技术内容
- 必要时使用标题分段
""",
    
    'technical': """你是一个技术专家，擅长解答技术问题。

请遵循以下规则：
1. **技术准确性**：确保技术细节准确无误
2. **代码示例**：提供清晰的代码示例（如果适用）
3. **最佳实践**：推荐业界最佳实践
4. **注意事项**：指出潜在的问题和注意事项
5. **版本信息**：注明相关的版本信息
6. **参考文档**：引用官方文档或权威来源

回答格式：
- 使用代码块展示代码
- 使用列表说明步骤
- 使用标题组织内容
""",
    
    'testing': """你是一个测试专家，擅长测试用例设计和测试策略。

请遵循以下规则：
1. **测试覆盖**：确保测试覆盖所有重要场景
2. **测试步骤**：提供清晰的测试步骤
3. **预期结果**：明确说明预期结果
4. **边界条件**：考虑边界条件和异常情况
5. **测试数据**：提供合适的测试数据
6. **优先级**：标注测试用例的优先级

回答格式：
- 使用表格组织测试用例
- 使用列表说明测试步骤
- 使用标题分类测试场景
""",
    
    'concise': """你是一个简洁的AI助手，擅长提供精炼的答案。

请遵循以下规则：
1. **简洁明了**：直接回答问题，避免冗余
2. **要点突出**：突出关键信息
3. **结构清晰**：使用列表或短段落
4. **基于文档**：答案必须基于提供的文档

回答格式：
- 使用简短的段落
- 使用要点列表
- 避免过多解释
"""
}


class RAGService:
    """RAG 查询服务"""
    
    def __init__(self, knowledge_base_service):
        """
        初始化 RAG 服务
        
        Args:
            knowledge_base_service: 知识库服务实例
        """
        self.kb_service = knowledge_base_service
        self.llm_client = None
    
    async def initialize_llm(self, llm_config: Dict[str, Any]):
        """
        初始化 LLM 客户端
        
        Args:
            llm_config: LLM 配置
        """
        try:
            from langchain_openai import ChatOpenAI
            
            # 根据配置创建 LLM 客户端
            if llm_config.get('provider') == 'openai':
                self.llm_client = ChatOpenAI(
                    model=llm_config.get('model', 'gpt-3.5-turbo'),
                    api_key=llm_config.get('api_key'),
                    base_url=llm_config.get('base_url'),
                    temperature=llm_config.get('temperature', 0.7),
                    streaming=True
                )
            elif llm_config.get('provider') == 'azure':
                from langchain_openai import AzureChatOpenAI
                self.llm_client = AzureChatOpenAI(
                    azure_endpoint=llm_config.get('base_url'),
                    api_key=llm_config.get('api_key'),
                    api_version=llm_config.get('api_version', '2024-02-15-preview'),
                    deployment_name=llm_config.get('deployment_name'),
                    temperature=llm_config.get('temperature', 0.7),
                    streaming=True
                )
            else:
                # 默认使用 OpenAI 兼容接口
                self.llm_client = ChatOpenAI(
                    model=llm_config.get('model', 'gpt-3.5-turbo'),
                    api_key=llm_config.get('api_key', 'dummy'),
                    base_url=llm_config.get('base_url'),
                    temperature=llm_config.get('temperature', 0.7),
                    streaming=True
                )
            
            logger.info(f"LLM client initialized: {llm_config.get('provider', 'openai')}")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def build_prompt(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        system_prompt: Optional[str] = None,
        prompt_template: str = 'default'
    ) -> str:
        """
        构建 RAG Prompt
        
        Args:
            query: 用户查询
            context_chunks: 检索到的上下文分块
            system_prompt: 系统提示词（可选，优先级最高）
            prompt_template: Prompt 模板类型（default/technical/testing/concise）
            
        Returns:
            构建好的 Prompt
        """
        # 选择系统提示词
        if not system_prompt:
            system_prompt = PROMPT_TEMPLATES.get(prompt_template, PROMPT_TEMPLATES['default'])
        
        # 构建上下文 - 改进格式
        context_text = ""
        for i, chunk in enumerate(context_chunks, 1):
            doc_title = chunk['metadata'].get('document_title', '未知文档')
            chunk_index = chunk['metadata'].get('chunk_index', 'N/A')
            score = chunk.get('score', 0)
            
            context_text += f"\n{'='*60}\n"
            context_text += f"【参考文档 {i}】\n"
            context_text += f"来源：{doc_title} (分块 #{chunk_index})\n"
            context_text += f"相关度：{score:.2%}\n"
            context_text += f"{'-'*60}\n"
            context_text += f"{chunk['content']}\n"
        
        # 构建完整 Prompt - 使用更清晰的结构
        prompt = f"""{system_prompt}

{'='*60}
参考文档内容：
{'='*60}
{context_text}

{'='*60}
用户问题：
{'='*60}
{query}

{'='*60}
请基于以上参考文档，回答用户的问题：
{'='*60}
"""
        
        return prompt
    
    async def query(
        self,
        query_text: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        system_prompt: Optional[str] = None,
        prompt_template: str = 'default',
        llm_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行 RAG 查询（非流式）
        
        Args:
            query_text: 查询文本
            top_k: 检索结果数量
            score_threshold: 相似度阈值
            system_prompt: 系统提示词（优先级最高）
            prompt_template: Prompt 模板类型（default/technical/testing/concise）
            llm_config: LLM 配置
            
        Returns:
            查询结果
        """
        start_time = time.time()
        
        try:
            # 1. 检索相关文档
            retrieval_start = time.time()
            context_chunks = await self.kb_service.search_knowledge(
                query=query_text,
                top_k=top_k,
                score_threshold=score_threshold
            )
            retrieval_time = time.time() - retrieval_start
            
            logger.info(f"Retrieved {len(context_chunks)} chunks in {retrieval_time:.2f}s")
            
            if not context_chunks:
                return {
                    'success': False,
                    'message': '未找到相关文档',
                    'query': query_text,
                    'answer': '抱歉，我在知识库中没有找到与您问题相关的信息。',
                    'context_chunks': [],
                    'retrieval_time': retrieval_time,
                    'generation_time': 0,
                    'total_time': time.time() - start_time
                }
            
            # 2. 初始化 LLM（如果需要）
            if llm_config and not self.llm_client:
                try:
                    await self.initialize_llm(llm_config)
                except Exception as llm_init_error:
                    logger.error(f"Failed to initialize LLM: {llm_init_error}")
                    return {
                        'success': False,
                        'message': f'LLM 初始化失败: {str(llm_init_error)}',
                        'query': query_text,
                        'answer': f'LLM 服务初始化失败，但已检索到相关文档。错误：{str(llm_init_error)}',
                        'context_chunks': context_chunks,
                        'retrieval_time': retrieval_time,
                        'generation_time': 0,
                        'total_time': time.time() - start_time
                    }
            
            if not self.llm_client:
                return {
                    'success': False,
                    'message': 'LLM 未配置',
                    'query': query_text,
                    'answer': '抱歉，LLM 服务未配置，无法生成回答。但已为您检索到相关文档，请查看参考内容。',
                    'context_chunks': context_chunks,
                    'retrieval_time': retrieval_time,
                    'generation_time': 0,
                    'total_time': time.time() - start_time
                }
            
            # 3. 构建 Prompt（使用指定的模板）
            prompt = self.build_prompt(query_text, context_chunks, system_prompt, prompt_template)
            
            # 4. 调用 LLM 生成回答
            generation_start = time.time()
            response = await self.llm_client.ainvoke(prompt)
            answer = response.content
            generation_time = time.time() - generation_start
            
            logger.info(f"Generated answer in {generation_time:.2f}s using template '{prompt_template}'")
            
            # 5. 返回结果
            total_time = time.time() - start_time
            
            return {
                'success': True,
                'message': '查询成功',
                'query': query_text,
                'answer': answer,
                'context_chunks': context_chunks,
                'prompt_template': prompt_template,
                'retrieval_time': retrieval_time,
                'generation_time': generation_time,
                'total_time': total_time
            }
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}", exc_info=True)
            
            # 提供更友好的错误信息
            error_msg = str(e)
            if 'Connection error' in error_msg or 'ConnectError' in error_msg:
                error_msg = 'LLM API 连接失败，请检查：\n1. LLM API URL 是否正确\n2. LLM API Key 是否有效\n3. 网络连接是否正常\n4. LLM 服务是否正在运行'
            elif 'Unauthorized' in error_msg or '401' in error_msg:
                error_msg = 'LLM API Key 无效或已过期，请检查配置'
            elif 'timeout' in error_msg.lower():
                error_msg = 'LLM API 请求超时，请检查网络连接或增加超时时间'
            
            return {
                'success': False,
                'message': f'查询失败: {error_msg}',
                'query': query_text,
                'answer': f'抱歉，查询过程中出现错误：{error_msg}',
                'context_chunks': context_chunks if 'context_chunks' in locals() else [],
                'retrieval_time': retrieval_time if 'retrieval_time' in locals() else 0,
                'generation_time': 0,
                'total_time': time.time() - start_time
            }
    
    async def query_stream(
        self,
        query_text: str,
        top_k: int = 5,
        score_threshold: float = 0.3,
        system_prompt: Optional[str] = None,
        llm_config: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        执行 RAG 查询（流式）
        
        Args:
            query_text: 查询文本
            top_k: 检索结果数量
            score_threshold: 相似度阈值
            system_prompt: 系统提示词
            llm_config: LLM 配置
            
        Yields:
            流式响应数据（SSE 格式）
        """
        start_time = time.time()
        
        try:
            # 1. 检索相关文档
            retrieval_start = time.time()
            context_chunks = await self.kb_service.search_knowledge(
                query=query_text,
                top_k=top_k,
                score_threshold=score_threshold
            )
            retrieval_time = time.time() - retrieval_start
            
            # 发送检索结果
            yield f"data: {json.dumps({'type': 'retrieval', 'chunks': len(context_chunks), 'time': retrieval_time}, ensure_ascii=False)}\n\n"
            
            if not context_chunks:
                yield f"data: {json.dumps({'type': 'error', 'message': '未找到相关文档'}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                return
            
            # 发送上下文信息
            yield f"data: {json.dumps({'type': 'context', 'chunks': context_chunks}, ensure_ascii=False)}\n\n"
            
            # 2. 初始化 LLM
            if llm_config and not self.llm_client:
                await self.initialize_llm(llm_config)
            
            if not self.llm_client:
                yield f"data: {json.dumps({'type': 'error', 'message': 'LLM 未配置'}, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
                return
            
            # 3. 构建 Prompt
            prompt = self.build_prompt(query_text, context_chunks, system_prompt)
            
            # 4. 流式生成回答
            generation_start = time.time()
            full_answer = ""
            
            async for chunk in self.llm_client.astream(prompt):
                if chunk.content:
                    full_answer += chunk.content
                    yield f"data: {json.dumps({'type': 'token', 'content': chunk.content}, ensure_ascii=False)}\n\n"
            
            generation_time = time.time() - generation_start
            total_time = time.time() - start_time
            
            # 5. 发送完成信息
            yield f"data: {json.dumps({'type': 'done', 'generation_time': generation_time, 'total_time': total_time}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            logger.error(f"RAG stream query failed: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
    
    async def save_query_log(
        self,
        query_text: str,
        answer: str,
        context_chunks: List[Dict[str, Any]],
        retrieval_time: float,
        generation_time: float,
        total_time: float
    ) -> bool:
        """
        保存查询日志
        
        Args:
            query_text: 查询文本
            answer: 回答
            context_chunks: 上下文分块
            retrieval_time: 检索时间
            generation_time: 生成时间
            total_time: 总时间
            
        Returns:
            是否成功
        """
        try:
            from app.models.aitestrebort.knowledge import aitestrebortQueryLog
            
            # 提取相似度分数
            similarity_scores = [chunk['score'] for chunk in context_chunks]
            
            # 创建查询日志
            await aitestrebortQueryLog.create(
                knowledge_base_id=self.kb_service.knowledge_base_id,
                query=query_text,
                response=answer,
                retrieved_chunks=context_chunks,
                similarity_scores=similarity_scores,
                retrieval_time=retrieval_time,
                generation_time=generation_time,
                total_time=total_time
            )
            
            logger.info(f"Query log saved for KB: {self.kb_service.knowledge_base_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save query log: {e}")
            return False
