"""
知识库管理服务
"""
from fastapi import Request, UploadFile
from tortoise.exceptions import DoesNotExist
from typing import Optional
import time
from loguru import logger

from app.models.aitestrebort.project import aitestrebortProject, aitestrebortProjectMember
from app.models.aitestrebort.knowledge import (
    aitestrebortKnowledgeBase,
    aitestrebortDocument,
    aitestrebortDocumentChunk,
    aitestrebortKnowledgeQuery,
    aitestrebortKnowledgeConfig
)
from app.services.aitestrebort.knowledge_rag import KnowledgeRAGService


# 知识库管理
async def get_knowledge_bases(
    request: Request,
    project_id: Optional[int] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取知识库列表"""
    try:
        # 构建查询
        query = aitestrebortKnowledgeBase.all()
        
        if project_id:
            query = query.filter(project_id=project_id)
        
        if search:
            query = query.filter(name__icontains=search)
        
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        # 获取总数
        total = await query.count()
        
        # 分页
        offset = (page - 1) * page_size
        knowledge_bases = await query.offset(offset).limit(page_size).prefetch_related('project', 'creator')
        
        # 格式化响应
        items = []
        for kb in knowledge_bases:
            # 获取实时统计数据
            document_count = await aitestrebortDocument.filter(knowledge_base_id=kb.id).count()
            chunk_count = await aitestrebortDocumentChunk.filter(document__knowledge_base_id=kb.id).count()
            
            items.append({
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "project_id": kb.project_id,
                "project_name": kb.project.name if kb.project else None,
                "creator_id": kb.creator_id,
                "creator_name": kb.creator.name if kb.creator else None,
                "is_active": kb.is_active,
                "chunk_size": kb.chunk_size,
                "chunk_overlap": kb.chunk_overlap,
                "document_count": document_count,
                "chunk_count": chunk_count,
                "created_at": kb.created_at.isoformat(),
                "updated_at": kb.updated_at.isoformat()
            })
        
        return request.app.get_success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except Exception as e:
        logger.error(f"Error getting knowledge bases: {e}", exc_info=True)
        return request.app.error(msg=f"获取知识库列表失败: {str(e)}")


async def create_knowledge_base(request: Request, kb_data: dict):
    """创建知识库"""
    try:
        project_id = kb_data.get('project_id')
        
        # 检查项目权限
        try:
            project = await aitestrebortProject.get(id=project_id)
        except DoesNotExist:
            return request.app.fail(msg="项目不存在")
        
        is_member = await aitestrebortProjectMember.filter(
            project=project,
            user_id=request.state.user.id
        ).exists()
        
        if not is_member and not request.state.user.is_superuser:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 创建知识库
        kb = await aitestrebortKnowledgeBase.create(
            name=kb_data['name'],
            description=kb_data.get('description'),
            project_id=project_id,
            creator_id=request.state.user.id,
            chunk_size=kb_data.get('chunk_size', 1000),
            chunk_overlap=kb_data.get('chunk_overlap', 200),
            is_active=kb_data.get('is_active', True)
        )
        
        await kb.fetch_related('project', 'creator')
        
        return request.app.post_success(data={
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "project_id": kb.project_id,
            "project_name": kb.project.name,
            "creator_id": kb.creator_id,
            "creator_name": kb.creator.name if kb.creator else None,
            "is_active": kb.is_active,
            "chunk_size": kb.chunk_size,
            "chunk_overlap": kb.chunk_overlap,
            "document_count": 0,  # 新创建的知识库文档数为0
            "chunk_count": 0,     # 新创建的知识库分块数为0
            "created_at": kb.created_at.isoformat(),
            "updated_at": kb.updated_at.isoformat()
        })
        
    except Exception as e:
        error_msg = str(e)
        if "Duplicate entry" in error_msg and "unique_project_name" in error_msg:
            return request.app.fail(msg="该项目中已存在同名的知识库，请使用其他名称")
        logger.error(f"Error creating knowledge base: {e}", exc_info=True)
        return request.app.error(msg=f"创建知识库失败: {str(e)}")


async def get_knowledge_base(request: Request, kb_id: str):
    """获取知识库详情"""
    try:
        kb = await aitestrebortKnowledgeBase.get(id=kb_id).prefetch_related('project', 'creator')
        
        # 获取实时统计数据
        document_count = await aitestrebortDocument.filter(knowledge_base_id=kb_id).count()
        chunk_count = await aitestrebortDocumentChunk.filter(document__knowledge_base_id=kb_id).count()
        
        return request.app.get_success(data={
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "project_id": kb.project_id,
            "project_name": kb.project.name,
            "creator_id": kb.creator_id,
            "creator_name": kb.creator.name if kb.creator else None,
            "is_active": kb.is_active,
            "chunk_size": kb.chunk_size,
            "chunk_overlap": kb.chunk_overlap,
            "document_count": document_count,
            "chunk_count": chunk_count,
            "created_at": kb.created_at.isoformat(),
            "updated_at": kb.updated_at.isoformat()
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Error getting knowledge base: {e}", exc_info=True)
        return request.app.error(msg=f"获取知识库失败: {str(e)}")


async def update_knowledge_base(request: Request, kb_id: str, kb_data: dict):
    """更新知识库"""
    try:
        kb = await aitestrebortKnowledgeBase.get(id=kb_id)
        
        # 更新字段
        if 'name' in kb_data:
            kb.name = kb_data['name']
        if 'description' in kb_data:
            kb.description = kb_data['description']
        if 'chunk_size' in kb_data:
            kb.chunk_size = kb_data['chunk_size']
        if 'chunk_overlap' in kb_data:
            kb.chunk_overlap = kb_data['chunk_overlap']
        if 'is_active' in kb_data:
            kb.is_active = kb_data['is_active']
        
        await kb.save()
        await kb.fetch_related('project', 'creator')
        
        return request.app.put_success(data={
            "id": kb.id,
            "name": kb.name,
            "description": kb.description,
            "project_id": kb.project_id,
            "project_name": kb.project.name,
            "is_active": kb.is_active,
            "chunk_size": kb.chunk_size,
            "chunk_overlap": kb.chunk_overlap,
            "updated_at": kb.updated_at.isoformat()
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Error updating knowledge base: {e}", exc_info=True)
        return request.app.error(msg=f"更新知识库失败: {str(e)}")


async def delete_knowledge_base(request: Request, kb_id: str):
    """删除知识库"""
    try:
        kb = await aitestrebortKnowledgeBase.get(id=kb_id)
        await kb.delete()
        
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Error deleting knowledge base: {e}", exc_info=True)
        return request.app.error(msg=f"删除知识库失败: {str(e)}")


# 知识库查询
async def query_knowledge(request: Request, query_data: dict):
    """查询知识库"""
    try:
        start_time = time.time()
        
        kb_id = query_data['knowledge_base_id']
        query_text = query_data['query']
        top_k = query_data.get('top_k', 5)
        
        # 检查知识库是否存在
        kb = await aitestrebortKnowledgeBase.get(id=kb_id)
        
        # 使用RAG服务进行检索
        rag_service = KnowledgeRAGService(kb.project_id, request.state.user.id)
        results = await rag_service.search_knowledge(query_text, top_k, [kb_id])
        
        retrieval_time = time.time() - start_time
        
        # 记录查询
        await aitestrebortKnowledgeQuery.create(
            knowledge_base_id=kb_id,
            user_id=request.state.user.id,
            query_text=query_text,
            top_k=top_k,
            result_count=len(results),
            retrieval_time=retrieval_time,
            total_time=retrieval_time
        )
        
        return request.app.get_success(data={
            "query": query_text,
            "sources": results,
            "retrieval_time": retrieval_time,
            "total_time": retrieval_time
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Error querying knowledge: {e}", exc_info=True)
        return request.app.error(msg=f"查询知识库失败: {str(e)}")


# 系统状态
async def get_system_status(request: Request):
    """获取系统状态"""
    try:
        # TODO: 实现实际的系统状态检查
        return request.app.get_success(data={
            "embedding_service": {
                "status": "ready",
                "model": "text-embedding-ada-002"
            },
            "vector_store": {
                "status": "ready",
                "type": "qdrant"
            },
            "dependencies": {
                "langchain": "installed",
                "qdrant_client": "installed"
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}", exc_info=True)
        return request.app.error(msg=f"获取系统状态失败: {str(e)}")


# 文档管理
async def get_documents(
    request: Request,
    kb_id: str,
    search: Optional[str] = None,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取文档列表"""
    try:
        # 检查知识库是否存在
        kb = await aitestrebortKnowledgeBase.get(id=kb_id)
        
        # 构建查询
        query = aitestrebortDocument.filter(knowledge_base_id=kb_id)
        
        if search:
            query = query.filter(title__icontains=search)
        
        if document_type:
            query = query.filter(document_type=document_type)
        
        if status:
            query = query.filter(status=status)
        
        # 获取总数
        total = await query.count()
        
        # 分页
        offset = (page - 1) * page_size
        documents = await query.offset(offset).limit(page_size).prefetch_related('uploader')
        
        # 格式化响应
        items = []
        for doc in documents:
            items.append({
                "id": doc.id,
                "title": doc.title,
                "document_type": doc.document_type,
                "status": doc.status,
                "file_path": doc.file_path,
                "url": doc.url,
                "file_size": doc.file_size,
                "page_count": doc.page_count,
                "word_count": doc.word_count,
                "chunk_count": doc.chunk_count,
                "uploader_id": doc.uploader_id,
                "uploader_name": doc.uploader.name if doc.uploader else None,
                "error_message": doc.error_message,
                "uploaded_at": doc.uploaded_at.isoformat(),
                "processed_at": doc.processed_at.isoformat() if doc.processed_at else None
            })
        
        return request.app.get_success(data={
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Error getting documents: {e}", exc_info=True)
        return request.app.error(msg=f"获取文档列表失败: {str(e)}")


async def upload_document(
    request: Request,
    kb_id: str,
    title: str,
    document_type: str,
    file: Optional[UploadFile] = None,
    url: Optional[str] = None,
    content: Optional[str] = None
):
    """上传文档"""
    try:
        import os
        from pathlib import Path
        
        # 检查知识库是否存在
        kb = await aitestrebortKnowledgeBase.get(id=kb_id)
        
        # 验证输入
        if not any([file, url, content]):
            return request.app.fail(msg="必须提供文件、URL或文本内容之一")
        
        # 创建文档记录
        doc_data = {
            "knowledge_base_id": kb_id,
            "title": title,
            "document_type": document_type,
            "uploader_id": request.state.user.id,
            "status": "pending"
        }
        
        # 处理文件上传
        if file:
            # 创建上传目录
            upload_dir = Path(f"uploads/knowledge_bases/{kb_id}/documents")
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            file_path = upload_dir / file.filename
            with open(file_path, "wb") as f:
                content_bytes = await file.read()
                f.write(content_bytes)
            
            doc_data["file_path"] = str(file_path)
            doc_data["file_size"] = len(content_bytes)
        
        if url:
            doc_data["url"] = url
        
        if content:
            doc_data["content"] = content
            doc_data["word_count"] = len(content.split())
        
        # 创建文档
        doc = await aitestrebortDocument.create(**doc_data)
        
        # TODO: 启动后台任务处理文档（向量化）
        # 这里应该使用Celery或其他任务队列
        logger.info(f"Document {doc.id} created, processing should be triggered")
        
        await doc.fetch_related('uploader')
        
        return request.app.post_success(data={
            "id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "status": doc.status,
            "file_path": doc.file_path,
            "url": doc.url,
            "uploader_id": doc.uploader_id,
            "uploader_name": doc.uploader.name if doc.uploader else None,
            "uploaded_at": doc.uploaded_at.isoformat()
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Error uploading document: {e}", exc_info=True)
        return request.app.error(msg=f"上传文档失败: {str(e)}")


async def get_document(request: Request, doc_id: str):
    """获取文档详情"""
    try:
        doc = await aitestrebortDocument.get(id=doc_id).prefetch_related('knowledge_base', 'uploader')
        
        return request.app.get_success(data={
            "id": doc.id,
            "title": doc.title,
            "document_type": doc.document_type,
            "status": doc.status,
            "file_path": doc.file_path,
            "url": doc.url,
            "content": doc.content,
            "file_size": doc.file_size,
            "page_count": doc.page_count,
            "word_count": doc.word_count,
            "chunk_count": doc.chunk_count,
            "knowledge_base_id": doc.knowledge_base_id,
            "knowledge_base_name": doc.knowledge_base.name,
            "uploader_id": doc.uploader_id,
            "uploader_name": doc.uploader.name if doc.uploader else None,
            "error_message": doc.error_message,
            "uploaded_at": doc.uploaded_at.isoformat(),
            "processed_at": doc.processed_at.isoformat() if doc.processed_at else None
        })
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Error getting document: {e}", exc_info=True)
        return request.app.error(msg=f"获取文档失败: {str(e)}")


async def delete_document(request: Request, doc_id: str):
    """删除文档"""
    try:
        import os
        
        doc = await aitestrebortDocument.get(id=doc_id)
        
        # 删除文件
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        
        # TODO: 从向量存储中删除
        
        # 删除数据库记录（会级联删除分块）
        await doc.delete()
        
        return request.app.delete_success()
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Error deleting document: {e}", exc_info=True)
        return request.app.error(msg=f"删除文档失败: {str(e)}")


async def reprocess_document(request: Request, doc_id: str):
    """重新处理文档"""
    try:
        doc = await aitestrebortDocument.get(id=doc_id)
        
        # 重置状态
        doc.status = "pending"
        doc.error_message = None
        await doc.save()
        
        # TODO: 启动后台任务重新处理文档
        logger.info(f"Document {doc.id} marked for reprocessing")
        
        return request.app.post_success(msg="文档已标记为待处理，将在后台重新处理")
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Error reprocessing document: {e}", exc_info=True)
        return request.app.error(msg=f"重新处理文档失败: {str(e)}")


# 配置管理
async def get_config(request: Request):
    """获取全局配置"""
    try:
        # 获取或创建配置
        config = await aitestrebortKnowledgeConfig.first()
        if not config:
            config = await aitestrebortKnowledgeConfig.create(
                embedding_service="custom",
                model_name="text-embedding-ada-002",
                chunk_size=1000,
                chunk_overlap=200
            )
        
        # 对API Key进行脱敏
        api_key = config.api_key
        if api_key and len(api_key) > 8:
            api_key = api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]
        elif api_key:
            api_key = '*' * len(api_key)
        
        return request.app.get_success(data={
            "id": config.id,
            "embedding_service": config.embedding_service,
            "api_base_url": config.api_base_url,
            "api_key": api_key,
            "model_name": config.model_name,
            "chunk_size": config.chunk_size,
            "chunk_overlap": config.chunk_overlap,
            "updated_at": config.updated_at.isoformat() if config.updated_at else None
        })
        
    except Exception as e:
        logger.error(f"Error getting config: {e}", exc_info=True)
        return request.app.error(msg=f"获取配置失败: {str(e)}")


async def update_config(request: Request, config_data: dict):
    """更新全局配置（仅管理员）"""
    try:
        # 检查管理员权限
        if not request.state.user.is_superuser:
            return request.app.forbidden(msg="只有管理员可以修改全局配置")
        
        # 获取或创建配置
        config = await aitestrebortKnowledgeConfig.first()
        if not config:
            config = await aitestrebortKnowledgeConfig.create()
        
        # 更新字段
        if 'embedding_service' in config_data:
            config.embedding_service = config_data['embedding_service']
        if 'api_base_url' in config_data:
            config.api_base_url = config_data['api_base_url']
        if 'api_key' in config_data:
            config.api_key = config_data['api_key']
        if 'model_name' in config_data:
            config.model_name = config_data['model_name']
        if 'chunk_size' in config_data:
            config.chunk_size = config_data['chunk_size']
        if 'chunk_overlap' in config_data:
            config.chunk_overlap = config_data['chunk_overlap']
        
        config.updated_by_id = request.state.user.id
        await config.save()
        
        # TODO: 清理缓存，使新配置立即生效
        
        return request.app.put_success(msg="配置更新成功")
        
    except Exception as e:
        logger.error(f"Error updating config: {e}", exc_info=True)
        return request.app.error(msg=f"更新配置失败: {str(e)}")


async def test_embedding_connection(request: Request, test_data: dict):
    """测试嵌入服务连接"""
    try:
        import httpx
        
        embedding_service = test_data.get('embedding_service')
        api_base_url = test_data.get('api_base_url', '').rstrip('/')
        api_key = test_data.get('api_key', '')
        model_name = test_data.get('model_name', '')
        
        if not all([embedding_service, api_base_url, model_name]):
            return request.app.fail(msg="请提供完整的配置信息")
        
        test_text = 'This is a test embedding request.'
        
        # 根据不同服务构建请求
        if embedding_service == 'openai':
            test_url = f'{api_base_url}/embeddings'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            }
            request_body = {
                'input': test_text,
                'model': model_name
            }
        elif embedding_service == 'azure_openai':
            test_url = f'{api_base_url}/openai/deployments/{model_name}/embeddings?api-version=2024-02-15-preview'
            headers = {
                'Content-Type': 'application/json',
                'api-key': api_key
            }
            request_body = {
                'input': test_text
            }
        elif embedding_service == 'ollama':
            test_url = f'{api_base_url}/api/embeddings'
            headers = {
                'Content-Type': 'application/json'
            }
            request_body = {
                'model': model_name,
                'prompt': test_text
            }
        elif embedding_service == 'custom':
            test_url = api_base_url
            headers = {
                'Content-Type': 'application/json'
            }
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            request_body = {
                'input': test_text,
                'model': model_name
            }
        else:
            return request.app.fail(msg=f"不支持的嵌入服务类型: {embedding_service}")
        
        # 发送测试请求
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(test_url, json=request_body, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # 验证返回数据
                has_embedding = False
                if embedding_service == 'ollama':
                    has_embedding = data.get('embedding') and isinstance(data['embedding'], list)
                else:
                    has_embedding = (
                        data.get('data') and 
                        isinstance(data['data'], list) and 
                        len(data['data']) > 0 and 
                        data['data'][0].get('embedding')
                    )
                
                if has_embedding:
                    return request.app.get_success(msg="嵌入模型测试成功！服务运行正常")
                else:
                    return request.app.fail(msg="服务响应成功但数据格式异常，请检查配置")
            else:
                return request.app.fail(msg=f"嵌入模型测试失败: HTTP {response.status_code}")
        
    except httpx.TimeoutException:
        return request.app.fail(msg="请求超时，请检查服务是否正常运行")
    except httpx.ConnectError as e:
        return request.app.fail(msg=f"无法连接到服务，请检查URL和网络: {str(e)}")
    except Exception as e:
        logger.error(f"Error testing embedding connection: {e}", exc_info=True)
        return request.app.error(msg=f"测试连接失败: {str(e)}")


async def get_embedding_services(request: Request):
    """获取可用的嵌入服务选项"""
    services = [
        {"value": "openai", "label": "OpenAI"},
        {"value": "azure_openai", "label": "Azure OpenAI"},
        {"value": "ollama", "label": "Ollama"},
        {"value": "custom", "label": "自定义API"}
    ]
    
    return request.app.get_success(data={"services": services})

# 知识库统计和内容查看
async def get_knowledge_base_statistics(request: Request, kb_id: str):
    """获取知识库统计信息"""
    try:
        kb = await aitestrebortKnowledgeBase.get(id=kb_id)
        
        # 统计信息
        document_count = await aitestrebortDocument.filter(knowledge_base_id=kb_id).count()
        chunk_count = await aitestrebortDocumentChunk.filter(document__knowledge_base_id=kb_id).count()
        query_count = await aitestrebortKnowledgeQuery.filter(knowledge_base_id=kb_id).count()
        
        # 文档状态分布
        status_distribution = {}
        documents = await aitestrebortDocument.filter(knowledge_base_id=kb_id).all()
        for doc in documents:
            status_distribution[doc.status] = status_distribution.get(doc.status, 0) + 1
        
        # 最近查询
        recent_queries = await aitestrebortKnowledgeQuery.filter(
            knowledge_base_id=kb_id
        ).order_by('-created_at').limit(5).all()
        
        recent_queries_data = []
        for query in recent_queries:
            recent_queries_data.append({
                'query': query.query,
                'total_time': query.total_time,
                'created_at': query.created_at.isoformat()
            })
        
        stats = {
            'document_count': document_count,
            'chunk_count': chunk_count,
            'query_count': query_count,
            'document_status_distribution': status_distribution,
            'recent_queries': recent_queries_data
        }
        
        return request.app.get_success(data=stats)
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Error getting knowledge base statistics: {e}", exc_info=True)
        return request.app.error(msg=f"获取统计信息失败: {str(e)}")


async def get_knowledge_base_content(
    request: Request,
    kb_id: str,
    search: Optional[str] = None,
    document_type: Optional[str] = None,
    status: str = 'completed',
    page: int = 1,
    page_size: int = 20
):
    """查看知识库内容"""
    try:
        kb = await aitestrebortKnowledgeBase.get(id=kb_id)
        
        # 构建查询
        query = aitestrebortDocument.filter(knowledge_base_id=kb_id, status=status)
        
        if search:
            query = query.filter(title__icontains=search)
        
        if document_type:
            query = query.filter(document_type=document_type)
        
        # 获取总数
        total_count = await query.count()
        
        # 分页
        offset = (page - 1) * page_size
        documents = await query.offset(offset).limit(page_size).prefetch_related('uploader')
        
        # 格式化文档数据
        content_data = []
        for doc in documents:
            chunk_count = await aitestrebortDocumentChunk.filter(document_id=doc.id).count()
            
            doc_data = {
                'id': doc.id,
                'title': doc.title,
                'document_type': doc.document_type,
                'status': doc.status,
                'uploader_name': doc.uploader.name if doc.uploader else None,
                'uploaded_at': doc.uploaded_at.isoformat(),
                'chunk_count': chunk_count,
                'content_preview': doc.content[:500] if doc.content else None,
                'file_size': doc.file_size,
                'page_count': doc.page_count,
                'word_count': doc.word_count,
            }
            
            if doc.file_path:
                doc_data['file_name'] = doc.file_path.split('/')[-1]
                doc_data['file_url'] = doc.file_path
            
            if doc.url:
                doc_data['url'] = doc.url
            
            content_data.append(doc_data)
        
        return request.app.get_success(data={
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size,
            'documents': content_data,
            'knowledge_base': {
                'id': kb.id,
                'name': kb.name,
                'description': kb.description,
            }
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Error getting knowledge base content: {e}", exc_info=True)
        return request.app.error(msg=f"获取知识库内容失败: {str(e)}")


async def get_document_status(request: Request, doc_id: str):
    """获取文档处理状态"""
    try:
        doc = await aitestrebortDocument.get(id=doc_id)
        
        chunk_count = await aitestrebortDocumentChunk.filter(document_id=doc_id).count()
        
        return request.app.get_success(data={
            'id': doc.id,
            'status': doc.status,
            'error_message': doc.error_message,
            'chunk_count': chunk_count,
            'processed_at': doc.processed_at.isoformat() if doc.processed_at else None
        })
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Error getting document status: {e}", exc_info=True)
        return request.app.error(msg=f"获取文档状态失败: {str(e)}")


async def get_document_content(
    request: Request,
    doc_id: str,
    include_chunks: bool = False,
    chunk_page: int = 1,
    chunk_page_size: int = 10
):
    """获取文档完整内容"""
    try:
        doc = await aitestrebortDocument.get(id=doc_id).prefetch_related('knowledge_base', 'uploader')
        
        if doc.status != 'completed':
            return request.app.fail(msg="文档尚未处理完成或处理失败")
        
        # 基础文档信息
        content_data = {
            'id': doc.id,
            'title': doc.title,
            'document_type': doc.document_type,
            'status': doc.status,
            'content': doc.content,
            'uploader_name': doc.uploader.name if doc.uploader else None,
            'uploaded_at': doc.uploaded_at.isoformat(),
            'processed_at': doc.processed_at.isoformat() if doc.processed_at else None,
            'file_size': doc.file_size,
            'page_count': doc.page_count,
            'word_count': doc.word_count,
            'knowledge_base': {
                'id': doc.knowledge_base.id,
                'name': doc.knowledge_base.name,
            }
        }
        
        if doc.file_path:
            content_data['file_name'] = doc.file_path.split('/')[-1]
            content_data['file_url'] = doc.file_path
        
        if doc.url:
            content_data['url'] = doc.url
        
        # 如果需要包含分块信息
        if include_chunks:
            chunks_query = aitestrebortDocumentChunk.filter(document_id=doc_id).order_by('chunk_index')
            total_chunks = await chunks_query.count()
            
            # 分页处理分块
            start = (chunk_page - 1) * chunk_page_size
            chunk_list = await chunks_query.offset(start).limit(chunk_page_size).all()
            
            content_data['chunks'] = {
                'total_count': total_chunks,
                'page': chunk_page,
                'page_size': chunk_page_size,
                'total_pages': (total_chunks + chunk_page_size - 1) // chunk_page_size,
                'items': [
                    {
                        'id': chunk.id,
                        'chunk_index': chunk.chunk_index,
                        'content': chunk.content,
                        'start_index': chunk.start_index,
                        'end_index': chunk.end_index,
                        'page_number': chunk.page_number,
                    }
                    for chunk in chunk_list
                ]
            }
        else:
            chunk_count = await aitestrebortDocumentChunk.filter(document_id=doc_id).count()
            content_data['chunk_count'] = chunk_count
        
        return request.app.get_success(data=content_data)
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Error getting document content: {e}", exc_info=True)
        return request.app.error(msg=f"获取文档内容失败: {str(e)}")