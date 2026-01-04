"""
向量数据库服务
提供文档处理、向量化、检索等核心功能
"""
import os
import time
import hashlib
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# 设置完全离线模式，避免任何网络请求
os.environ['TRANSFORMERS_OFFLINE'] = '1'
os.environ['HF_DATASETS_OFFLINE'] = '1'
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['HF_HUB_DISABLE_PROGRESS_BARS'] = '1'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['HF_HUB_TIMEOUT'] = '1'
os.environ['REQUESTS_TIMEOUT'] = '1'

from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader,
    TextLoader, UnstructuredMarkdownLoader, UnstructuredHTMLLoader,
    WebBaseLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document as LangChainDocument
from langchain.embeddings.base import Embeddings
import requests
import uuid

logger = logging.getLogger(__name__)


class CustomEmbeddings(Embeddings):
    """
    自定义嵌入服务，支持多种API提供商
    """
    
    def __init__(self, api_base_url: str, api_key: str, model_name: str):
        self.api_base_url = api_base_url.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        
        # 构建完整的嵌入API端点
        if '/embeddings' not in self.api_base_url:
            self.embeddings_url = f"{self.api_base_url}/embeddings"
        else:
            self.embeddings_url = self.api_base_url
            
        logger.info(f"CustomEmbeddings initialized: {self.embeddings_url}, model: {self.model_name}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入多个文档"""
        return self._embed_texts(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        return self._embed_texts([text])[0]
    
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """调用嵌入API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": texts,
            "model": self.model_name
        }
        
        try:
            response = requests.post(
                self.embeddings_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            embeddings = [item["embedding"] for item in result["data"]]
            
            logger.info(f"Successfully embedded {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding API call failed: {e}")
            raise


class DocumentProcessor:
    """
    文档处理器
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_document(self, file_path: str, document_type: str) -> List[LangChainDocument]:
        """
        加载文档
        
        Args:
            file_path: 文件路径
            document_type: 文档类型
            
        Returns:
            LangChain文档列表
        """
        try:
            if document_type == 'pdf':
                loader = PyPDFLoader(file_path)
            elif document_type == 'docx':
                loader = Docx2txtLoader(file_path)
            elif document_type == 'pptx':
                loader = UnstructuredPowerPointLoader(file_path)
            elif document_type == 'txt':
                loader = TextLoader(file_path, encoding='utf-8')
            elif document_type == 'md':
                loader = UnstructuredMarkdownLoader(file_path)
            elif document_type == 'html':
                loader = UnstructuredHTMLLoader(file_path)
            else:
                raise ValueError(f"Unsupported document type: {document_type}")
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages from {file_path}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            raise
    
    def load_url(self, url: str) -> List[LangChainDocument]:
        """
        加载网页内容
        
        Args:
            url: 网页URL
            
        Returns:
            LangChain文档列表
        """
        try:
            loader = WebBaseLoader([url])
            documents = loader.load()
            logger.info(f"Loaded web content from {url}")
            return documents
            
        except Exception as e:
            logger.error(f"Failed to load URL {url}: {e}")
            raise
    
    def split_documents(self, documents: List[LangChainDocument]) -> List[LangChainDocument]:
        """
        分割文档
        
        Args:
            documents: 原始文档列表
            
        Returns:
            分割后的文档列表
        """
        try:
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split {len(documents)} documents into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to split documents: {e}")
            raise
    
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        提取文档元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            元数据字典
        """
        try:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            
            # 尝试读取文件内容来计算字数
            word_count = 0
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    word_count = len(content.split())
            except:
                # 如果无法读取为文本，跳过字数统计
                pass
            
            metadata = {
                'file_size': file_size,
                'word_count': word_count,
                'page_count': None  # 需要根据文档类型具体计算
            }
            
            logger.info(f"Extracted metadata for {file_path}: {metadata}")
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to extract metadata from {file_path}: {e}")
            return {}


class VectorStoreManager:
    """
    向量存储管理器
    管理嵌入模型和向量数据库操作
    """
    
    _embeddings_cache = {}
    _global_config_cache = None
    
    @classmethod
    def clear_global_config_cache(cls):
        """清理全局配置缓存"""
        cls._global_config_cache = None
        logger.info("Global config cache cleared")
    
    @classmethod
    async def get_global_config(cls):
        """获取全局配置（带缓存）"""
        if cls._global_config_cache is None:
            from app.models.aitestrebort.knowledge import aitestrebortKnowledgeConfig
            try:
                config = await aitestrebortKnowledgeConfig.get(id=1)
                cls._global_config_cache = config
            except:
                # 如果没有配置，创建默认配置
                config = await aitestrebortKnowledgeConfig.create(
                    id=1,
                    embedding_service='custom',
                    api_base_url='http://localhost:11434',
                    model_name='text-embedding-ada-002',
                    chunk_size=1000,
                    chunk_overlap=200
                )
                cls._global_config_cache = config
        
        return cls._global_config_cache
    
    @classmethod
    async def get_embeddings(cls, knowledge_base=None) -> Embeddings:
        """
        获取嵌入模型实例
        
        Args:
            knowledge_base: 知识库实例（可选，用于获取特定配置）
            
        Returns:
            嵌入模型实例
        """
        # 获取配置
        if knowledge_base:
            # 使用知识库特定配置（如果有的话）
            config = await cls.get_global_config()
        else:
            # 使用全局配置
            config = await cls.get_global_config()
        
        # 构建缓存键
        cache_key = f"{config.embedding_service}_{config.api_base_url}_{config.model_name}"
        
        if cache_key not in cls._embeddings_cache:
            if config.embedding_service == 'custom':
                embeddings = CustomEmbeddings(
                    api_base_url=config.api_base_url,
                    api_key=config.api_key or "",
                    model_name=config.model_name
                )
            else:
                # 其他嵌入服务的实现
                raise NotImplementedError(f"Embedding service {config.embedding_service} not implemented")
            
            cls._embeddings_cache[cache_key] = embeddings
            logger.info(f"Created new embeddings instance: {cache_key}")
        
        return cls._embeddings_cache[cache_key]
    
    @classmethod
    async def test_embedding_connection(cls, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试嵌入服务连接
        
        Args:
            config_data: 配置数据
            
        Returns:
            测试结果
        """
        try:
            # 创建临时嵌入实例
            embeddings = CustomEmbeddings(
                api_base_url=config_data['api_base_url'],
                api_key=config_data.get('api_key', ''),
                model_name=config_data['model_name']
            )
            
            # 测试嵌入
            start_time = time.time()
            test_embedding = embeddings.embed_query("测试文本")
            end_time = time.time()
            
            return {
                'success': True,
                'message': '连接成功',
                'embedding_dimension': len(test_embedding),
                'response_time': round(end_time - start_time, 3)
            }
            
        except Exception as e:
            logger.error(f"Embedding connection test failed: {e}")
            return {
                'success': False,
                'message': f'连接失败: {str(e)}',
                'embedding_dimension': None,
                'response_time': None
            }


class KnowledgeBaseService:
    """
    知识库服务
    提供完整的知识库管理功能
    """
    
    def __init__(self, knowledge_base_id: str):
        self.knowledge_base_id = knowledge_base_id
        self.processor = None
        self.embeddings = None
    
    async def initialize(self):
        """初始化服务"""
        from app.models.aitestrebort.knowledge import aitestrebortKnowledgeBase
        
        self.knowledge_base = await aitestrebortKnowledgeBase.get(id=self.knowledge_base_id)
        self.processor = DocumentProcessor(
            chunk_size=self.knowledge_base.chunk_size,
            chunk_overlap=self.knowledge_base.chunk_overlap
        )
        self.embeddings = await VectorStoreManager.get_embeddings(self.knowledge_base)
    
    async def process_document(self, document_id: str) -> Dict[str, Any]:
        """
        处理文档：加载、分块、向量化
        
        Args:
            document_id: 文档ID
            
        Returns:
            处理结果
        """
        from app.models.aitestrebort.knowledge import aitestrebortDocument, aitestrebortDocumentChunk
        
        try:
            # 获取文档
            document = await aitestrebortDocument.get(id=document_id)
            
            # 更新状态为处理中
            document.status = 'processing'
            await document.save()
            
            # 加载文档内容
            if document.url:
                # 网页内容
                langchain_docs = self.processor.load_url(document.url)
            elif document.file_path:
                # 文件内容
                langchain_docs = self.processor.load_document(
                    document.file_path, 
                    document.document_type
                )
            else:
                # 直接文本内容
                langchain_docs = [LangChainDocument(
                    page_content=document.content or "",
                    metadata={"source": document.title}
                )]
            
            # 分割文档
            chunks = self.processor.split_documents(langchain_docs)
            
            # 删除旧的分块
            await aitestrebortDocumentChunk.filter(document=document).delete()
            
            # 创建新的分块并向量化
            for i, chunk in enumerate(chunks):
                # 生成嵌入
                embedding = await self.embeddings.embed_query(chunk.page_content)
                embedding_hash = hashlib.md5(str(embedding).encode()).hexdigest()
                
                # 保存分块
                await aitestrebortDocumentChunk.create(
                    document=document,
                    chunk_index=i,
                    content=chunk.page_content,
                    embedding_hash=embedding_hash,
                    start_index=chunk.metadata.get('start_index'),
                    end_index=chunk.metadata.get('end_index'),
                    page_number=chunk.metadata.get('page')
                )
            
            # 更新文档状态
            document.status = 'completed'
            document.processed_at = time.time()
            document.word_count = sum(len(chunk.page_content.split()) for chunk in chunks)
            await document.save()
            
            logger.info(f"Successfully processed document {document_id}: {len(chunks)} chunks")
            
            return {
                'success': True,
                'message': '文档处理成功',
                'chunks_count': len(chunks)
            }
            
        except Exception as e:
            # 更新文档状态为失败
            try:
                document = await aitestrebortDocument.get(id=document_id)
                document.status = 'failed'
                document.error_message = str(e)
                await document.save()
            except:
                pass
            
            logger.error(f"Failed to process document {document_id}: {e}")
            return {
                'success': False,
                'message': f'文档处理失败: {str(e)}',
                'chunks_count': 0
            }
    
    async def search_knowledge(
        self, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表
        """
        try:
            from app.models.aitestrebort.knowledge import aitestrebortDocumentChunk
            
            # 生成查询向量
            query_embedding = await self.embeddings.embed_query(query)
            
            # 获取所有分块（这里简化实现，实际应该使用向量数据库）
            chunks = await aitestrebortDocumentChunk.filter(
                document__knowledge_base_id=self.knowledge_base_id
            ).prefetch_related('document').all()
            
            # 计算相似度（简化实现）
            results = []
            for chunk in chunks:
                # 这里应该计算向量相似度，简化为文本匹配
                if query.lower() in chunk.content.lower():
                    results.append({
                        'content': chunk.content,
                        'metadata': {
                            'document_title': chunk.document.title,
                            'chunk_index': chunk.chunk_index,
                            'score': 0.8  # 简化的相似度分数
                        }
                    })
            
            # 返回前top_k个结果
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Knowledge search failed: {e}")
            return []