"""
向量数据库服务
提供文档处理、向量化、检索等核心功能
"""
import os
import time
import hashlib
import logging
import json
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

from .qdrant_manager import QdrantManager

logger = logging.getLogger(__name__)


class DashScopeEmbeddings(Embeddings):
    """
    阿里云百炼（DashScope）嵌入服务
    """
    
    def __init__(self, api_key: str, model: str = "text-embedding-v1"):
        self.api_key = api_key
        self.model = model
        
        # DashScope API端点
        self.embeddings_url = "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding"
        
        logger.info(f"DashScopeEmbeddings initialized: model: {self.model}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入多个文档"""
        return self._embed_texts(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        return self._embed_texts([text])[0]
    
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """调用DashScope嵌入API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "input": {
                "texts": texts
            }
        }
        
        try:
            logger.info(f"Calling DashScope embedding API: {self.embeddings_url}")
            logger.info(f"Model: {self.model}, Texts count: {len(texts)}")
            
            response = requests.post(
                self.embeddings_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 404:
                error_msg = (
                    f"DashScope嵌入API端点不存在\n"
                    f"可能的原因：\n"
                    f"1. API端点已更新，请检查最新文档\n"
                    f"2. 模型名称不正确\n"
                    f"3. 请访问: https://help.aliyun.com/zh/dashscope/"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            if response.status_code == 401:
                error_msg = "API密钥无效或过期，请检查您的阿里云API密钥"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            response.raise_for_status()
            
            result = response.json()
            
            # DashScope返回格式: {"output": {"embeddings": [{"embedding": [...], "text_index": 0}]}}
            if "output" not in result or "embeddings" not in result["output"]:
                logger.error(f"Invalid response format: {result}")
                raise ValueError(f"DashScope API响应格式不正确: {result}")
            
            embeddings_data = result["output"]["embeddings"]
            # 按text_index排序并提取embedding
            embeddings_data.sort(key=lambda x: x.get("text_index", 0))
            embeddings = [item["embedding"] for item in embeddings_data]
            
            logger.info(f"Successfully embedded {len(texts)} texts, dimension: {len(embeddings[0]) if embeddings else 0}")
            return embeddings
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response content: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            raise
        except Exception as e:
            logger.error(f"DashScope embedding API call failed: {e}")
            raise


class OllamaEmbeddings(Embeddings):
    """
    Ollama嵌入服务,支持本地运行的BGE-M3等模型
    """
    
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.model = model
        
        # 构建嵌入API端点
        # Ollama使用 /api/embeddings 端点
        if '/api/embeddings' not in self.base_url:
            self.embeddings_url = f"{self.base_url}/api/embeddings"
        else:
            self.embeddings_url = self.base_url
            
        logger.info(f"OllamaEmbeddings initialized: {self.embeddings_url}, model: {self.model}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入多个文档"""
        return [self.embed_query(text) for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        return self._embed_text(text)
    
    def _embed_text(self, text: str) -> List[float]:
        """调用Ollama嵌入API"""
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        try:
            logger.info(f"Calling Ollama embedding API: {self.embeddings_url}")
            logger.info(f"Model: {self.model}")
            
            response = requests.post(
                self.embeddings_url,
                json=payload,
                timeout=30
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code == 404:
                error_msg = (
                    f"Ollama嵌入API端点不存在: {self.embeddings_url}\n"
                    f"可能的原因：\n"
                    f"1. Ollama服务未启动\n"
                    f"2. 模型 '{self.model}' 未安装\n"
                    f"3. 请运行: ollama pull {self.model}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            response.raise_for_status()
            
            result = response.json()
            
            # Ollama返回格式: {"embedding": [0.1, 0.2, ...]}
            if "embedding" not in result:
                logger.error(f"Invalid response format: {result}")
                raise ValueError(f"Ollama API响应格式不正确，缺少'embedding'字段")
            
            embedding = result["embedding"]
            
            logger.info(f"Successfully embedded text, dimension: {len(embedding)}")
            return embedding
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response content: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            raise
        except Exception as e:
            logger.error(f"Ollama embedding API call failed: {e}")
            raise


class CustomEmbeddings(Embeddings):
    """
    自定义嵌入服务，支持多种API提供商
    """
    
    def __init__(self, api_base_url: str, api_key: str, model_name: str):
        # 清理API密钥，移除可能的Bearer前缀
        if api_key and api_key.startswith("Bearer "):
            api_key = api_key[7:].strip()
        
        self.api_key = api_key
        self.model_name = model_name
        
        # 清理base_url，移除可能的端点路径
        base_url = api_base_url.rstrip('/')
        
        # 移除常见的端点路径（如果用户错误地包含了）
        endpoints_to_remove = ['/embeddings', '/v1/embeddings', '/api/embeddings']
        for endpoint in endpoints_to_remove:
            if base_url.endswith(endpoint):
                base_url = base_url[:-len(endpoint)]
                logger.info(f"Removed endpoint '{endpoint}' from base_url")
                break
        
        # 移除可能的/api路径（某些服务使用/api作为前缀）
        if base_url.endswith('/api'):
            base_url = base_url[:-4]
            logger.info(f"Removed /api from base_url")
        
        # 确保base_url以/v1结尾（OpenAI兼容API标准）
        if not base_url.endswith('/v1'):
            # 检查是否已经包含/v1在路径中
            if '/v1' not in base_url:
                base_url = base_url + '/v1'
                logger.info(f"Added /v1 to base_url: {base_url}")
        
        # 构建完整的嵌入API端点
        self.api_base_url = base_url
        self.embeddings_url = f"{base_url}/embeddings"
        
        logger.info(f"CustomEmbeddings initialized: {self.embeddings_url}, model: {self.model_name}")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入多个文档"""
        return self._embed_texts(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """嵌入单个查询"""
        return self._embed_texts([text])[0]
    
    def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """调用嵌入API"""
        # 检测是否是阿里云DashScope API
        is_dashscope = 'dashscope.aliyuncs.com' in self.embeddings_url
        
        # 构建请求头
        headers = {
            "Content-Type": "application/json"
        }
        
        # 阿里云可能支持两种认证方式
        if is_dashscope:
            # 尝试两种认证头
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-DashScope-API-Key"] = self.api_key
            logger.info("Detected DashScope API, using dual authentication headers")
        else:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "input": texts,
            "model": self.model_name
        }
        
        try:
            logger.info(f"Calling embedding API: {self.embeddings_url}")
            logger.info(f"Model: {self.model_name}, Texts count: {len(texts)}")
            logger.info(f"API Key (masked): {self.api_key[:10]}...{self.api_key[-4:] if len(self.api_key) > 14 else '****'}")
            
            response = requests.post(
                self.embeddings_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # 记录响应状态
            logger.info(f"Response status: {response.status_code}")
            
            # 如果是401，提供更详细的错误信息
            if response.status_code == 401:
                error_detail = ""
                try:
                    error_json = response.json()
                    error_detail = json.dumps(error_json, ensure_ascii=False)
                except:
                    error_detail = response.text
                
                error_msg = (
                    f"API认证失败 (401 Unauthorized)\n"
                    f"端点: {self.embeddings_url}\n"
                    f"可能的原因：\n"
                    f"1. API密钥不正确或已过期\n"
                    f"2. API密钥格式错误（应该是 sk-xxxxxxxx）\n"
                    f"3. 账户未开通该服务或余额不足\n"
                    f"4. API密钥权限不足\n"
                    f"\n服务器响应: {error_detail[:200]}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            # 如果是404，提供更详细的错误信息
            if response.status_code == 404:
                error_msg = (
                    f"嵌入API端点不存在: {self.embeddings_url}\n"
                    f"可能的原因：\n"
                    f"1. 该API服务不支持标准的OpenAI嵌入端点\n"
                    f"2. 端点路径可能不是 /v1/embeddings\n"
                    f"3. 请检查API文档确认正确的嵌入端点路径\n"
                    f"提示：如果使用通义千问等国内模型，可能需要使用专用的SDK或不同的端点路径"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            response.raise_for_status()
            
            result = response.json()
            
            # 检查响应格式
            if "data" not in result:
                logger.error(f"Invalid response format: {result}")
                raise ValueError(f"API响应格式不正确，缺少'data'字段: {result}")
            
            embeddings = [item["embedding"] for item in result["data"]]
            
            logger.info(f"Successfully embedded {len(texts)} texts, dimension: {len(embeddings[0]) if embeddings else 0}")
            return embeddings
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response content: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            raise
        except Exception as e:
            logger.error(f"Embedding API call failed: {e}")
            raise
            
            # 记录响应状态
            logger.info(f"Response status: {response.status_code}")
            
            # 如果是404，提供更详细的错误信息
            if response.status_code == 404:
                error_msg = (
                    f"嵌入API端点不存在: {self.embeddings_url}\n"
                    f"可能的原因：\n"
                    f"1. 该API服务不支持标准的OpenAI嵌入端点\n"
                    f"2. 端点路径可能不是 /v1/embeddings\n"
                    f"3. 请检查API文档确认正确的嵌入端点路径\n"
                    f"提示：如果使用通义千问等国内模型，可能需要使用专用的SDK或不同的端点路径"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            response.raise_for_status()
            
            result = response.json()
            
            # 检查响应格式
            if "data" not in result:
                logger.error(f"Invalid response format: {result}")
                raise ValueError(f"API响应格式不正确，缺少'data'字段: {result}")
            
            embeddings = [item["embedding"] for item in result["data"]]
            
            logger.info(f"Successfully embedded {len(texts)} texts, dimension: {len(embeddings[0]) if embeddings else 0}")
            return embeddings
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error: {e}")
            logger.error(f"Response content: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            raise
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
            elif document_type in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                # 图片文件，使用UnstructuredImageLoader
                from langchain_community.document_loaders import UnstructuredImageLoader
                loader = UnstructuredImageLoader(file_path)
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
            knowledge_base: 知识库实例
            
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
            if config.embedding_service == 'ollama':
                # Ollama嵌入服务（支持BGE-M3等本地模型）
                embeddings = OllamaEmbeddings(
                    base_url=config.api_base_url or "http://localhost:11434",
                    model=config.model_name or "bge-m3"
                )
            elif config.embedding_service == 'custom' or config.embedding_service == 'openai':
                # OpenAI兼容的API服务
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
            embedding_service = config_data.get('embedding_service', 'custom')
            
            # 根据服务类型创建临时嵌入实例
            if embedding_service == 'ollama':
                embeddings = OllamaEmbeddings(
                    base_url=config_data.get('api_base_url', 'http://localhost:11434'),
                    model=config_data.get('model_name', 'bge-m3')
                )
            else:
                # OpenAI兼容的API服务
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
    """
    
    def __init__(self, knowledge_base_id: str):
        self.knowledge_base_id = knowledge_base_id
        self.processor = None
        self.embeddings = None
        self.qdrant_manager = None
    
    async def initialize(self):
        """初始化服务"""
        from app.models.aitestrebort.knowledge import aitestrebortKnowledgeBase, aitestrebortKnowledgeConfig
        
        self.knowledge_base = await aitestrebortKnowledgeBase.get(id=self.knowledge_base_id)
        self.processor = DocumentProcessor(
            chunk_size=self.knowledge_base.chunk_size,
            chunk_overlap=self.knowledge_base.chunk_overlap
        )
        self.embeddings = await VectorStoreManager.get_embeddings(self.knowledge_base)
        
        # 初始化 Qdrant 管理器
        try:
            # 获取全局配置
            global_config = await aitestrebortKnowledgeConfig.first()
            
            # Qdrant 配置（从环境变量或全局配置获取）
            qdrant_url = os.getenv('QDRANT_URL', None)
            qdrant_api_key = os.getenv('QDRANT_API_KEY', None)
            
            # 集合名称使用知识库ID
            collection_name = f"kb_{self.knowledge_base_id}"
            
            # 自动检测向量维度
            try:
                # 生成一个测试嵌入来获取实际维度
                test_embedding = self.embeddings.embed_query("test")
                vector_size = len(test_embedding)
                logger.info(f"Detected embedding dimension: {vector_size}")
            except Exception as e:
                logger.warning(f"Failed to detect embedding dimension: {e}")
                # 回退到默认值
                vector_size = 1536  # 默认 OpenAI ada-002
                if global_config:
                    if 'bge' in global_config.model_name.lower():
                        vector_size = 768  # BGE 模型
                    elif 'ollama' in global_config.embedding_service:
                        vector_size = 768  # Ollama 默认
                    elif 'nomic' in global_config.model_name.lower():
                        vector_size = 768  # Nomic Embed
                    elif 'mxbai' in global_config.model_name.lower():
                        vector_size = 1024  # mxbai-embed-large
            
            self.qdrant_manager = QdrantManager(
                collection_name=collection_name,
                embeddings=self.embeddings,
                qdrant_url=qdrant_url,
                qdrant_api_key=qdrant_api_key,
                vector_size=vector_size
            )
            logger.info(f"Qdrant manager initialized for KB: {self.knowledge_base_id}, vector_size: {vector_size}")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Qdrant manager: {e}")
            logger.warning("Vector storage will not be available")
            self.qdrant_manager = None
    
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
            logger.info(f"Getting document {document_id}")
            document = await aitestrebortDocument.get(id=document_id)
            logger.info(f"Document found: {document.title}, type: {document.document_type}, status: {document.status}")
            
            # 更新状态为处理中
            document.status = 'processing'
            await document.save()
            logger.info(f"Document status updated to 'processing'")
            
            # 加载文档内容
            logger.info(f"Loading document content...")
            if document.url:
                # 网页内容
                logger.info(f"Loading from URL: {document.url}")
                langchain_docs = self.processor.load_url(document.url)
            elif document.file_path:
                # 文件内容
                logger.info(f"Loading from file: {document.file_path}")
                logger.info(f"Document type: {document.document_type}")
                
                # 检查文件是否存在
                if not os.path.exists(document.file_path):
                    raise FileNotFoundError(f"文件不存在: {document.file_path}")
                
                try:
                    langchain_docs = self.processor.load_document(
                        document.file_path, 
                        document.document_type
                    )
                except ModuleNotFoundError as e:
                    # 提供更友好的错误信息
                    module_name = str(e).split("'")[1] if "'" in str(e) else "unknown"
                    error_msg = f"缺少必需的依赖包: {module_name}\n"
                    
                    if module_name == "markdown":
                        error_msg += "请运行: pip install markdown"
                    elif module_name == "pptx" or "python-pptx" in module_name:
                        error_msg += "请运行: pip install python-pptx"
                    elif "pypdf" in module_name:
                        error_msg += "请运行: pip install pypdf"
                    else:
                        error_msg += f"请运行: pip install {module_name}"
                    
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            else:
                # 直接文本内容
                logger.info(f"Using direct text content, length: {len(document.content or '')}")
                langchain_docs = [LangChainDocument(
                    page_content=document.content or "",
                    metadata={"source": document.title}
                )]
            
            logger.info(f"Loaded {len(langchain_docs)} document(s)")
            
            # 提取并保存完整文档内容
            full_content = "\n\n".join([doc.page_content for doc in langchain_docs])
            document.content = full_content
            document.page_count = len(langchain_docs)  # 更新页数
            await document.save()
            logger.info(f"Saved full document content, length: {len(full_content)}, pages: {len(langchain_docs)}")
            
            # 分割文档
            logger.info(f"Splitting documents into chunks...")
            chunks = self.processor.split_documents(langchain_docs)
            logger.info(f"Created {len(chunks)} chunks")
            
            # 删除旧的分块
            old_chunks = await aitestrebortDocumentChunk.filter(document=document).count()
            if old_chunks > 0:
                logger.info(f"Deleting {old_chunks} old chunks")
                await aitestrebortDocumentChunk.filter(document=document).delete()
            
            # 创建新的分块并向量化
            logger.info(f"Creating and embedding {len(chunks)} chunks...")
            for i, chunk in enumerate(chunks):
                if i % 10 == 0:
                    logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                
                # 生成嵌入（embed_query是同步方法，不需要await）
                embedding = self.embeddings.embed_query(chunk.page_content)
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
            
            logger.info(f"All chunks created and embedded successfully")
            
            # 存储到 Qdrant 向量数据库
            if self.qdrant_manager:
                try:
                    logger.info("Storing vectors to Qdrant...")
                    vector_ids = self.qdrant_manager.add_documents(
                        documents=chunks,
                        document_id=str(document.id)
                    )
                    logger.info(f"Successfully stored {len(vector_ids)} vectors to Qdrant")
                except Exception as e:
                    logger.error(f"Failed to store vectors to Qdrant: {e}")
                    # 不影响文档处理流程，继续执行
            
            # 更新文档状态
            from datetime import datetime
            document.status = 'completed'
            document.processed_at = datetime.now()
            document.word_count = sum(len(chunk.page_content.split()) for chunk in chunks)
            await document.save()
            
            logger.info(f"Successfully processed document {document_id}: {len(chunks)} chunks, status: completed")
            
            return {
                'success': True,
                'message': '文档处理成功',
                'chunks_count': len(chunks)
            }
            
        except Exception as e:
            # 更新文档状态为失败
            logger.error(f"Failed to process document {document_id}: {e}", exc_info=True)
            try:
                document = await aitestrebortDocument.get(id=document_id)
                document.status = 'failed'
                document.error_message = str(e)
                await document.save()
                logger.info(f"Document status updated to 'failed'")
            except Exception as save_error:
                logger.error(f"Failed to update document status: {save_error}")
            
            return {
                'success': False,
                'message': f'文档处理失败: {str(e)}',
                'chunks_count': 0
            }
    
    async def search_knowledge(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        搜索知识库（使用 Qdrant 向量检索）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            
        Returns:
            搜索结果列表
        """
        import asyncio
        
        try:
            if not self.qdrant_manager:
                logger.warning("Qdrant manager not initialized, falling back to database search")
                return await self._fallback_search(query, top_k, score_threshold)
            
            logger.info(f"开始Qdrant向量检索，query: {query[:50]}...")
            
            # 使用 asyncio.to_thread 避免阻塞事件循环
            try:
                results = await asyncio.to_thread(
                    self.qdrant_manager.similarity_search,
                    query=query,
                    k=top_k,
                    score_threshold=score_threshold
                )
                logger.info(f"Qdrant检索完成，找到 {len(results)} 个结果")
                return results
            except Exception as search_error:
                logger.error(f"Qdrant检索失败: {search_error}")
                # 降级到数据库搜索
                return await self._fallback_search(query, top_k, score_threshold)
            
        except Exception as e:
            logger.error(f"Failed to search knowledge: {e}", exc_info=True)
            # 降级到数据库搜索
            return await self._fallback_search(query, top_k, score_threshold)
    
    async def _fallback_search(
        self,
        query: str,
        top_k: int,
        score_threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        降级搜索（使用数据库文本匹配）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            score_threshold: 相似度阈值
            
        Returns:
            搜索结果列表
        """
        from app.models.aitestrebort.knowledge import aitestrebortDocumentChunk
        
        try:
            # 获取所有分块
            chunks = await aitestrebortDocumentChunk.filter(
                document__knowledge_base_id=self.knowledge_base_id,
                document__status='completed'
            ).prefetch_related('document').all()
            
            logger.info(f"Found {len(chunks)} chunks to search")
            
            if not chunks:
                logger.warning("No chunks found in knowledge base")
                return []
            
            # 改进的文本匹配（支持分词）
            logger.info("Performing improved text matching")
            results = []
            
            # 分词查询
            import re
            query_lower = query.lower()
            # 提取中文字符和英文单词
            chinese_chars = re.findall(r'[\u4e00-\u9fff]+', query)
            english_words = re.findall(r'[a-zA-Z]+', query_lower)
            
            query_terms = chinese_chars + english_words
            if not query_terms:
                query_terms = [query_lower]
            
            logger.info(f"Query terms: {query_terms}, score_threshold: {score_threshold}")
            
            matched_count = 0
            for chunk in chunks:
                content_lower = chunk.content.lower()
                
                # 计算匹配度
                match_count = 0
                total_match_length = 0
                for term in query_terms:
                    term_lower = term.lower()
                    if term_lower in content_lower:
                        match_count += 1
                        # 计算匹配长度占比
                        total_match_length += len(term)
                
                # 如果至少匹配一个词，就加入结果
                if match_count > 0:
                    # 改进的评分算法：考虑匹配词数和匹配长度
                    term_match_score = match_count / len(query_terms)
                    length_match_score = total_match_length / len(query)
                    score = (term_match_score * 0.7 + length_match_score * 0.3)
                    
                    matched_count += 1
                    
                    # 应用相似度阈值
                    if score >= score_threshold:
                        results.append({
                            'content': chunk.content,
                            'score': score,
                            'metadata': {
                                'document_id': str(chunk.document.id),
                                'document_title': chunk.document.title,
                                'chunk_index': chunk.chunk_index
                            }
                        })
                    else:
                        logger.debug(f"Chunk score {score:.2f} below threshold {score_threshold}")
            
            logger.info(f"Matched {matched_count} chunks, {len(results)} passed threshold")
            
            # 按分数排序
            results.sort(key=lambda x: x['score'], reverse=True)
            
            logger.info(f"Search completed, found {len(results)} matching chunks")
            
            # 返回前top_k个结果
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Fallback search failed: {e}")
            return []
