"""
aitestrebort 知识库管理服务
包含RAG功能
"""
import os
import time
import logging
from typing import Optional, List, Dict, Any
from fastapi import Request, Depends, UploadFile, File
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from tortoise import transactions

from app.models.aitestrebort.knowledge import (
    aitestrebortKnowledgeBase, aitestrebortDocument, aitestrebortDocumentChunk,
    aitestrebortKnowledgeQuery, aitestrebortKnowledgeConfig
)
from .vector_store import VectorStoreManager, KnowledgeBaseService, DocumentProcessor
from utils.logs.log import logger


# ==================== 全局配置管理 ====================

async def get_global_config(request: Request):
    """获取知识库全局配置"""
    try:
        config = await aitestrebortKnowledgeConfig.get_or_none(id=1)
        if not config:
            # 创建默认配置
            config = await aitestrebortKnowledgeConfig.create(
                id=1,
                embedding_service='custom',
                api_base_url='http://localhost:11434',
                model_name='text-embedding-ada-002',
                chunk_size=1000,
                chunk_overlap=200
            )
        
        # 对API Key进行脱敏处理
        config_data = {
            'id': config.id,
            'embedding_service': config.embedding_service,
            'api_base_url': config.api_base_url,
            'api_key': mask_api_key(config.api_key) if config.api_key else None,
            'model_name': config.model_name,
            'chunk_size': config.chunk_size,
            'chunk_overlap': config.chunk_overlap,
            'updated_at': config.updated_at.isoformat() if config.updated_at else None
        }
        
        return request.app.get_success(data=config_data)
        
    except Exception as e:
        logger.error(f"Failed to get global config: {e}")
        return request.app.error(msg=f"获取全局配置失败: {str(e)}")


async def update_global_config(request: Request, config_data: dict):
    """更新知识库全局配置（仅管理员可操作）"""
    try:
        # 检查权限（这里简化处理，实际应该检查用户权限）
        if not hasattr(request.state, 'user') or not request.state.user:
            return request.app.forbidden(msg="需要登录")
        
        config = await aitestrebortKnowledgeConfig.get_or_none(id=1)
        if not config:
            config = await aitestrebortKnowledgeConfig.create(id=1)
        
        # 更新配置
        for key, value in config_data.items():
            if hasattr(config, key) and value is not None:
                setattr(config, key, value)
        
        config.updated_by_id = request.state.user.id
        await config.save()
        
        # 清理缓存
        VectorStoreManager.clear_global_config_cache()
        VectorStoreManager._embeddings_cache.clear()
        
        return request.app.put_success(data={"message": "全局配置更新成功"})
        
    except Exception as e:
        logger.error(f"Failed to update global config: {e}")
        return request.app.error(msg=f"更新全局配置失败: {str(e)}")


async def test_embedding_connection(request: Request, config_data: dict):
    """测试嵌入服务连接"""
    try:
        result = await VectorStoreManager.test_embedding_connection(config_data)
        
        if result['success']:
            return request.app.get_success(data=result)
        else:
            return request.app.fail(msg=result['message'], data=result)
            
    except Exception as e:
        logger.error(f"Embedding connection test failed: {e}")
        return request.app.error(msg=f"连接测试失败: {str(e)}")


async def get_embedding_services(request: Request):
    """获取支持的嵌入服务列表"""
    services = [
        {"value": "openai", "label": "OpenAI"},
        {"value": "azure_openai", "label": "Azure OpenAI"},
        {"value": "ollama", "label": "Ollama"},
        {"value": "custom", "label": "自定义API"}
    ]
    return request.app.get_success(data={"services": services})


# ==================== 知识库管理 ====================

async def get_knowledge_bases(request: Request, project_id: int, params: dict = None):
    """获取知识库列表"""
    try:
        from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
        
        # 检查项目权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 构建查询
        query = aitestrebortKnowledgeBase.filter(project=project)
        
        # 应用过滤条件
        if params:
            if params.get('is_active') is not None:
                query = query.filter(is_active=params['is_active'])
            if params.get('search'):
                search_term = params['search']
                query = query.filter(
                    Q(name__icontains=search_term) | 
                    Q(description__icontains=search_term)
                )
        
        # 获取结果
        knowledge_bases = await query.order_by('-created_at').all()
        
        # 构建响应数据
        data = []
        for kb in knowledge_bases:
            # 统计文档数量
            doc_count = await aitestrebortDocument.filter(knowledge_base=kb).count()
            completed_count = await aitestrebortDocument.filter(
                knowledge_base=kb, status='completed'
            ).count()
            
            data.append({
                'id': str(kb.id),
                'name': kb.name,
                'description': kb.description,
                'is_active': kb.is_active,
                'chunk_size': kb.chunk_size,
                'chunk_overlap': kb.chunk_overlap,
                'document_count': doc_count,
                'processed_count': completed_count,
                'created_at': kb.created_at.isoformat(),
                'updated_at': kb.updated_at.isoformat()
            })
        
        return request.app.get_success(data=data)
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        logger.error(f"Failed to get knowledge bases: {e}")
        return request.app.error(msg=f"获取知识库列表失败: {str(e)}")


async def create_knowledge_base(request: Request, project_id: int, kb_data: dict):
    """创建知识库"""
    try:
        from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
        
        # 检查项目权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 检查名称是否重复
        existing = await aitestrebortKnowledgeBase.filter(
            project=project, name=kb_data['name']
        ).first()
        if existing:
            return request.app.fail(msg="知识库名称已存在")
        
        # 创建知识库
        kb = await aitestrebortKnowledgeBase.create(
            name=kb_data['name'],
            description=kb_data.get('description'),
            project=project,
            creator_id=request.state.user.id,
            chunk_size=kb_data.get('chunk_size', 1000),
            chunk_overlap=kb_data.get('chunk_overlap', 200)
        )
        
        return request.app.post_success(data={
            'id': str(kb.id),
            'name': kb.name,
            'description': kb.description,
            'created_at': kb.created_at.isoformat()
        })
        
    except DoesNotExist:
        return request.app.fail(msg="项目不存在")
    except Exception as e:
        logger.error(f"Failed to create knowledge base: {e}")
        return request.app.error(msg=f"创建知识库失败: {str(e)}")


async def get_knowledge_base_detail(request: Request, project_id: int, kb_id: str):
    """获取知识库详情"""
    try:
        from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
        
        # 检查项目权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取知识库
        kb = await aitestrebortKnowledgeBase.get(id=kb_id, project=project)
        
        # 统计信息
        doc_count = await aitestrebortDocument.filter(knowledge_base=kb).count()
        completed_count = await aitestrebortDocument.filter(
            knowledge_base=kb, status='completed'
        ).count()
        chunk_count = await aitestrebortDocumentChunk.filter(
            document__knowledge_base=kb
        ).count()
        
        data = {
            'id': str(kb.id),
            'name': kb.name,
            'description': kb.description,
            'is_active': kb.is_active,
            'chunk_size': kb.chunk_size,
            'chunk_overlap': kb.chunk_overlap,
            'document_count': doc_count,
            'processed_count': completed_count,
            'chunk_count': chunk_count,
            'created_at': kb.created_at.isoformat(),
            'updated_at': kb.updated_at.isoformat()
        }
        
        return request.app.get_success(data=data)
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Failed to get knowledge base detail: {e}")
        return request.app.error(msg=f"获取知识库详情失败: {str(e)}")


async def update_knowledge_base(request: Request, project_id: int, kb_id: str, kb_data: dict):
    """更新知识库"""
    try:
        from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
        
        # 检查项目权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取知识库
        kb = await aitestrebortKnowledgeBase.get(id=kb_id, project=project)
        
        # 检查名称是否重复
        if 'name' in kb_data and kb_data['name'] != kb.name:
            existing = await aitestrebortKnowledgeBase.filter(
                project=project, name=kb_data['name']
            ).exclude(id=kb.id).first()
            if existing:
                return request.app.fail(msg="知识库名称已存在")
        
        # 更新字段
        for key, value in kb_data.items():
            if hasattr(kb, key) and value is not None:
                setattr(kb, key, value)
        
        await kb.save()
        
        return request.app.put_success(data={
            'id': str(kb.id),
            'name': kb.name,
            'description': kb.description,
            'updated_at': kb.updated_at.isoformat()
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Failed to update knowledge base: {e}")
        return request.app.error(msg=f"更新知识库失败: {str(e)}")


async def delete_knowledge_base(request: Request, project_id: int, kb_id: str):
    """删除知识库"""
    try:
        from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
        
        # 检查项目权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        # 获取知识库
        kb = await aitestrebortKnowledgeBase.get(id=kb_id, project=project)
        
        # 删除知识库（级联删除文档和分块）
        await kb.delete()
        
        return request.app.delete_success(data={"message": "知识库删除成功"})
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Failed to delete knowledge base: {e}")
        return request.app.error(msg=f"删除知识库失败: {str(e)}")


# ==================== 文档管理 ====================

async def get_documents(request: Request, project_id: int, kb_id: str, params: dict = None):
    """获取文档列表"""
    try:
        from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
        
        # 检查权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        kb = await aitestrebortKnowledgeBase.get(id=kb_id, project=project)
        
        # 构建查询
        query = aitestrebortDocument.filter(knowledge_base=kb)
        
        # 应用过滤条件
        if params:
            if params.get('status'):
                query = query.filter(status=params['status'])
            if params.get('document_type'):
                query = query.filter(document_type=params['document_type'])
            if params.get('search'):
                search_term = params['search']
                query = query.filter(
                    Q(title__icontains=search_term) | 
                    Q(content__icontains=search_term)
                )
        
        # 分页
        page = params.get('page', 1) if params else 1
        page_size = params.get('page_size', 20) if params else 20
        offset = (page - 1) * page_size
        
        total = await query.count()
        documents = await query.order_by('-uploaded_at').offset(offset).limit(page_size).all()
        
        # 构建响应数据
        data = []
        for doc in documents:
            chunk_count = await aitestrebortDocumentChunk.filter(document=doc).count()
            
            data.append({
                'id': str(doc.id),
                'title': doc.title,
                'document_type': doc.document_type,
                'status': doc.status,
                'file_size': doc.file_size,
                'page_count': doc.page_count,
                'word_count': doc.word_count,
                'chunk_count': chunk_count,
                'error_message': doc.error_message,
                'uploaded_at': doc.uploaded_at.isoformat(),
                'processed_at': doc.processed_at.isoformat() if doc.processed_at else None
            })
        
        return request.app.get_success(data={
            'documents': data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Failed to get documents: {e}")
        return request.app.error(msg=f"获取文档列表失败: {str(e)}")


async def upload_document(request: Request, project_id: int, kb_id: str, file: UploadFile):
    """上传文档"""
    try:
        from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
        
        # 检查权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        kb = await aitestrebortKnowledgeBase.get(id=kb_id, project=project)
        
        # 检查文件类型
        allowed_types = ['pdf', 'docx', 'pptx', 'txt', 'md', 'html']
        file_ext = file.filename.split('.')[-1].lower() if file.filename else ''
        if file_ext not in allowed_types:
            return request.app.fail(msg=f"不支持的文件类型: {file_ext}")
        
        # 保存文件
        upload_dir = f"uploads/knowledge/{kb_id}"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 创建文档记录
        doc = await aitestrebortDocument.create(
            knowledge_base=kb,
            title=file.filename,
            document_type=file_ext,
            file_path=file_path,
            file_size=len(content),
            uploader_id=request.state.user.id,
            status='pending'
        )
        
        # 异步处理文档（这里简化为同步处理）
        kb_service = KnowledgeBaseService(str(kb.id))
        await kb_service.initialize()
        result = await kb_service.process_document(str(doc.id))
        
        return request.app.post_success(data={
            'id': str(doc.id),
            'title': doc.title,
            'status': doc.status,
            'processing_result': result
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Failed to upload document: {e}")
        return request.app.error(msg=f"上传文档失败: {str(e)}")


# ==================== RAG查询功能 ====================

async def query_knowledge_base(request: Request, project_id: int, kb_id: str, query_data: dict):
    """查询知识库（RAG功能）"""
    try:
        from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
        
        # 检查权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        kb = await aitestrebortKnowledgeBase.get(id=kb_id, project=project)
        
        query_text = query_data.get('query', '')
        top_k = query_data.get('top_k', 5)
        
        if not query_text:
            return request.app.fail(msg="查询内容不能为空")
        
        # 执行搜索
        start_time = time.time()
        
        kb_service = KnowledgeBaseService(str(kb.id))
        await kb_service.initialize()
        
        search_results = await kb_service.search_knowledge(query_text, top_k)
        
        retrieval_time = time.time() - start_time
        
        # 记录查询日志
        await aitestrebortKnowledgeQuery.create(
            knowledge_base=kb,
            user_id=request.state.user.id,
            query=query_text,
            retrieved_chunks=[r['metadata'] for r in search_results],
            similarity_scores=[r['metadata'].get('score', 0) for r in search_results],
            retrieval_time=retrieval_time,
            total_time=retrieval_time
        )
        
        return request.app.get_success(data={
            'query': query_text,
            'results': search_results,
            'retrieval_time': retrieval_time,
            'total_results': len(search_results)
        })
        
    except DoesNotExist:
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Failed to query knowledge base: {e}")
        return request.app.error(msg=f"查询知识库失败: {str(e)}")


# ==================== 辅助函数 ====================

def mask_api_key(api_key: str) -> str:
    """对API密钥进行脱敏处理"""
    if not api_key:
        return ""
    
    if len(api_key) <= 8:
        return '*' * len(api_key)
    
    return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]