"""
Qdrant 向量数据库管理器
提供向量存储、检索等核心功能
"""
import os
import logging
import hashlib
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    models,
)
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document as LangChainDocument
from langchain.embeddings.base import Embeddings

logger = logging.getLogger(__name__)


class QdrantManager:
    """Qdrant 向量数据库管理器"""
    
    def __init__(
        self,
        collection_name: str,
        embeddings: Embeddings,
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        vector_size: int = 1536  # OpenAI ada-002 默认维度
    ):
        """
        初始化 Qdrant 管理器
        
        Args:
            collection_name: 集合名称
            embeddings: 嵌入模型
            qdrant_url: Qdrant 服务地址（默认使用内存模式）
            qdrant_api_key: Qdrant API Key
            vector_size: 向量维度
        """
        self.collection_name = collection_name
        self.embeddings = embeddings
        self.vector_size = vector_size
        
        # 初始化 Qdrant 客户端
        if qdrant_url:
            # 使用远程 Qdrant 服务
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key,
                timeout=60
            )
            logger.info(f"Connected to Qdrant server at {qdrant_url}")
        else:
            # 使用本地内存模式（开发测试用）
            self.client = QdrantClient(":memory:")
            logger.info("Using Qdrant in-memory mode")
        
        # 确保集合存在
        self._ensure_collection()
    
    def _ensure_collection(self):
        """确保集合存在，不存在则创建"""
        try:
            # 检查集合是否存在
            collections = self.client.get_collections().collections
            collection_names = [col.name for col in collections]
            
            if self.collection_name not in collection_names:
                # 创建集合
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.collection_name}")
            else:
                logger.info(f"Collection already exists: {self.collection_name}")
                
        except Exception as e:
            logger.error(f"Failed to ensure collection: {e}")
            raise
    
    def get_vector_store(self) -> QdrantVectorStore:
        """
        获取 LangChain 的 QdrantVectorStore 实例
        
        Returns:
            QdrantVectorStore 实例
        """
        return QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings
        )
    
    def add_documents(
        self,
        documents: List[LangChainDocument],
        document_id: str,
        batch_size: int = 100
    ) -> List[str]:
        """
        添加文档到向量存储
        
        Args:
            documents: LangChain 文档列表
            document_id: 文档ID（用于元数据）
            batch_size: 批处理大小
            
        Returns:
            向量ID列表
        """
        try:
            vector_store = self.get_vector_store()
            vector_ids = []
            
            # 为每个文档添加元数据
            for doc in documents:
                if not doc.metadata:
                    doc.metadata = {}
                doc.metadata['document_id'] = document_id
            
            # 批量添加文档
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                ids = vector_store.add_documents(batch)
                vector_ids.extend(ids)
                logger.info(f"Added batch {i//batch_size + 1}: {len(batch)} documents")
            
            logger.info(f"Successfully added {len(documents)} documents to Qdrant")
            return vector_ids
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        score_threshold: float = 0.0,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        相似度搜索
        
        Args:
            query: 查询文本
            k: 返回结果数量
            score_threshold: 相似度阈值
            filter_dict: 过滤条件
            
        Returns:
            搜索结果列表
        """
        try:
            vector_store = self.get_vector_store()
            
            # 执行搜索
            if filter_dict:
                results = vector_store.similarity_search_with_score(
                    query,
                    k=k,
                    filter=filter_dict
                )
            else:
                results = vector_store.similarity_search_with_score(query, k=k)
            
            # 格式化结果
            formatted_results = []
            for doc, score in results:
                if score >= score_threshold:
                    formatted_results.append({
                        'content': doc.page_content,
                        'metadata': doc.metadata,
                        'score': float(score)
                    })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            raise
    
    def delete_by_document_id(self, document_id: str) -> bool:
        """
        删除指定文档的所有向量
        
        Args:
            document_id: 文档ID
            
        Returns:
            是否成功
        """
        try:
            # 使用过滤条件删除
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="metadata.document_id",
                                match=models.MatchValue(value=document_id)
                            )
                        ]
                    )
                )
            )
            logger.info(f"Deleted vectors for document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete vectors: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        获取集合信息
        
        Returns:
            集合信息字典
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                'name': info.config.params.vectors.size,
                'vectors_count': info.vectors_count,
                'points_count': info.points_count,
                'status': info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            return {}
    
    def clear_collection(self) -> bool:
        """
        清空集合
        
        Returns:
            是否成功
        """
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection()
            logger.info(f"Cleared collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
