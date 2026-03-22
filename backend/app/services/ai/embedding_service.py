"""
嵌入服务
支持多种嵌入模型的统一接口
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional, Union
import numpy as np
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class EmbeddingService:
    """嵌入服务类"""
    
    def __init__(self, provider: str, config: Dict[str, Any]):
        self.provider = provider
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """初始化客户端"""
        try:
            if self.provider == "openai":
                self._init_openai_client()
            elif self.provider == "azure_openai":
                self._init_azure_openai_client()
            elif self.provider == "ollama":
                self._init_ollama_client()
            elif self.provider == "custom":
                self._init_custom_client()
            else:
                raise ValueError(f"Unsupported embedding provider: {self.provider}")
        except Exception as e:
            logger.error(f"Failed to initialize embedding client: {e}")
            raise
    
    def _init_openai_client(self):
        """初始化OpenAI客户端"""
        try:
            import openai
            self.client = openai.AsyncOpenAI(
                api_key=self.config.get("api_key"),
                base_url=self.config.get("base_url", "https://api.openai.com/v1")
            )
        except ImportError:
            logger.error("OpenAI package not installed")
            raise
    
    def _init_azure_openai_client(self):
        """初始化Azure OpenAI客户端"""
        try:
            import openai
            self.client = openai.AsyncAzureOpenAI(
                api_key=self.config.get("api_key"),
                azure_endpoint=self.config.get("azure_endpoint"),
                api_version=self.config.get("api_version", "2024-02-15-preview")
            )
        except ImportError:
            logger.error("OpenAI package not installed")
            raise
    
    def _init_ollama_client(self):
        """初始化Ollama客户端"""
        self.client = httpx.AsyncClient(
            base_url=self.config.get("base_url", "http://localhost:11434"),
            timeout=self.config.get("timeout", 60.0)
        )
    
    def _init_custom_client(self):
        """初始化自定义客户端"""
        self.client = httpx.AsyncClient(
            base_url=self.config.get("base_url"),
            headers=self.config.get("headers", {}),
            timeout=self.config.get("timeout", 60.0)
        )
    
    async def create_embeddings(
        self,
        texts: Union[str, List[str]],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """创建文本嵌入"""
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            model = model or self.config.get("model", "text-embedding-ada-002")
            
            if self.provider in ["openai", "azure_openai"]:
                return await self._openai_embeddings(texts, model)
            elif self.provider == "ollama":
                return await self._ollama_embeddings(texts, model)
            elif self.provider == "custom":
                return await self._custom_embeddings(texts, model)
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Create embeddings failed: {e}")
            raise
    
    async def _openai_embeddings(self, texts: List[str], model: str) -> List[List[float]]:
        """OpenAI嵌入"""
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=texts
            )
            
            embeddings = []
            for data in response.data:
                embeddings.append(data.embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI embeddings failed: {e}")
            raise
    
    async def _ollama_embeddings(self, texts: List[str], model: str) -> List[List[float]]:
        """Ollama嵌入"""
        try:
            embeddings = []
            
            for text in texts:
                payload = {
                    "model": model,
                    "prompt": text
                }
                
                response = await self.client.post("/api/embeddings", json=payload)
                response.raise_for_status()
                
                result = response.json()
                embedding = result.get("embedding", [])
                embeddings.append(embedding)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Ollama embeddings failed: {e}")
            raise
    
    async def _custom_embeddings(self, texts: List[str], model: str) -> List[List[float]]:
        """自定义API嵌入"""
        try:
            payload = {
                "model": model,
                "input": texts
            }
            
            response = await self.client.post(
                self.config.get("embeddings_endpoint", "/embeddings"),
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 尝试解析不同的响应格式
            if "data" in result:
                # OpenAI兼容格式
                embeddings = [item["embedding"] for item in result["data"]]
            elif "embeddings" in result:
                # 简单格式
                embeddings = result["embeddings"]
            else:
                # 假设直接返回嵌入列表
                embeddings = result
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Custom embeddings failed: {e}")
            raise
    
    async def similarity_search(
        self,
        query_embedding: List[float],
        document_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """相似度搜索"""
        try:
            # 计算余弦相似度
            similarities = []
            query_norm = np.linalg.norm(query_embedding)
            
            for i, doc_embedding in enumerate(document_embeddings):
                doc_norm = np.linalg.norm(doc_embedding)
                if query_norm == 0 or doc_norm == 0:
                    similarity = 0.0
                else:
                    similarity = np.dot(query_embedding, doc_embedding) / (query_norm * doc_norm)
                
                similarities.append({
                    "index": i,
                    "similarity": float(similarity)
                })
            
            # 按相似度排序并返回top_k
            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise
    
    async def chunk_text(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Dict[str, Any]]:
        """文本分块"""
        try:
            chunks = []
            text_length = len(text)
            
            start = 0
            chunk_id = 0
            
            while start < text_length:
                end = min(start + chunk_size, text_length)
                
                # 尝试在句号、换行符等位置分割
                if end < text_length:
                    # 向后查找合适的分割点
                    for i in range(end, max(start + chunk_size // 2, end - 100), -1):
                        if text[i] in '.。\n':
                            end = i + 1
                            break
                
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "id": chunk_id,
                        "text": chunk_text,
                        "start_index": start,
                        "end_index": end,
                        "length": len(chunk_text)
                    })
                    chunk_id += 1
                
                # 计算下一个块的起始位置
                start = max(start + 1, end - chunk_overlap)
            
            return chunks
            
        except Exception as e:
            logger.error(f"Text chunking failed: {e}")
            raise
    
    async def process_document(
        self,
        text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """处理文档：分块并生成嵌入"""
        try:
            # 分块
            chunks = await self.chunk_text(text, chunk_size, chunk_overlap)
            
            if not chunks:
                return []
            
            # 提取文本内容
            chunk_texts = [chunk["text"] for chunk in chunks]
            
            # 生成嵌入
            embeddings = await self.create_embeddings(chunk_texts, model)
            
            # 组合结果
            for i, chunk in enumerate(chunks):
                chunk["embedding"] = embeddings[i] if i < len(embeddings) else []
                chunk["embedding_model"] = model or self.config.get("model")
                chunk["created_at"] = datetime.now().isoformat()
            
            return chunks
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise
    
    async def close(self):
        """关闭客户端连接"""
        if hasattr(self.client, 'aclose'):
            await self.client.aclose()


# 全局嵌入服务实例管理
_embedding_services: Dict[str, EmbeddingService] = {}


async def get_embedding_service(config_name: str = "default") -> EmbeddingService:
    """获取嵌入服务实例"""
    if config_name not in _embedding_services:
        # TODO: 从配置中加载嵌入配置
        # 这里使用默认配置
        default_config = {
            "provider": "custom",
            "base_url": "http://localhost:11434",
            "model": "bge-m3:latest",
            "timeout": 60.0
        }
        
        _embedding_services[config_name] = EmbeddingService(
            provider="custom",
            config=default_config
        )
    
    return _embedding_services[config_name]


async def cleanup_embedding_services():
    """清理所有嵌入服务实例"""
    for service in _embedding_services.values():
        await service.close()
    _embedding_services.clear()