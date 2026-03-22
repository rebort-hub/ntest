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
        # 检查API密钥是否被脱敏
        api_key = config_data.get('api_key', '')
        
        # 如果API密钥包含星号，说明是脱敏的，需要从数据库获取真实密钥
        if api_key and '*' in api_key:
            logger.info("Detected masked API key, fetching real key from database")
            config = await aitestrebortKnowledgeConfig.get_or_none(id=1)
            if config and config.api_key:
                api_key = config.api_key
                logger.info("Using real API key from database")
            else:
                return request.app.fail(msg="无法获取真实的API密钥，请重新输入完整的API密钥")
        
        # 更新config_data中的api_key
        config_data['api_key'] = api_key
        
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
        from app.models.system.user import User
        
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
            # 状态筛选
            is_active = params.get('is_active')
            if is_active is not None:
                # 处理字符串类型的布尔值
                if isinstance(is_active, str):
                    is_active = is_active.lower() in ('true', '1', 'yes')
                query = query.filter(is_active=is_active)
            
            # 搜索
            if params.get('search'):
                search_term = params['search']
                query = query.filter(
                    Q(name__icontains=search_term) | 
                    Q(description__icontains=search_term)
                )
        
        # 获取总数（在分页前）
        total_count = await query.count()
        
        # 应用分页
        page = int(params.get('page', 1)) if params and params.get('page') else 1
        page_size = int(params.get('page_size', 10)) if params and params.get('page_size') else 10
        offset = (page - 1) * page_size
        
        logger.info(f"Pagination: page={page}, page_size={page_size}, offset={offset}, total={total_count}")
        
        # 获取分页结果
        knowledge_bases = await query.order_by('-created_at').offset(offset).limit(page_size).all()
        
        # 构建响应数据
        data = []
        for kb in knowledge_bases:
            # 统计文档数量
            doc_count = await aitestrebortDocument.filter(knowledge_base=kb).count()
            completed_count = await aitestrebortDocument.filter(
                knowledge_base=kb, status='completed'
            ).count()
            
            # 统计分块数量
            chunk_count = await aitestrebortDocumentChunk.filter(
                document__knowledge_base=kb
            ).count()
            
            # 获取创建者信息
            creator_name = "未知"
            if kb.creator_id:
                try:
                    creator = await User.get(id=kb.creator_id)
                    creator_name = creator.name
                except Exception as e:
                    logger.warning(f"Failed to get creator for KB {kb.id}: {e}")
            
            data.append({
                'id': str(kb.id),
                'name': kb.name,
                'description': kb.description,
                'is_active': kb.is_active,
                'chunk_size': kb.chunk_size,
                'chunk_overlap': kb.chunk_overlap,
                'document_count': doc_count,
                'processed_count': completed_count,
                'chunk_count': chunk_count,
                'creator_id': kb.creator_id,
                'creator_name': creator_name,
                'created_at': kb.created_at.isoformat(),
                'updated_at': kb.updated_at.isoformat()
            })
        
        return request.app.get_success(data={
            'items': data,
            'total': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
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
            
            # 获取上传者信息
            uploader_name = "未知"  # 默认值
            if doc.uploader_id:
                from app.models.system.user import User
                try:
                    uploader = await User.get(id=doc.uploader_id)
                    uploader_name = uploader.name  # 注意：User模型使用的是name字段，不是username
                    logger.debug(f"Found uploader for doc {doc.id}: {uploader_name}")
                except Exception as e:
                    logger.warning(f"Failed to get uploader for doc {doc.id}, uploader_id={doc.uploader_id}: {e}")
                    # 保持默认值"未知"
            else:
                logger.debug(f"Doc {doc.id} has no uploader_id")
            
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
                'uploader_name': uploader_name,
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


async def upload_document(request: Request, project_id: int, kb_id: str):
    """上传文档"""
    try:
        from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
        from fastapi import Form
        
        # 检查权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        kb = await aitestrebortKnowledgeBase.get(id=kb_id, project=project)
        
        # 解析表单数据
        form = await request.form()
        title = form.get('title')
        document_type = form.get('document_type')
        file = form.get('file')
        content = form.get('content')
        url = form.get('url')
        
        if not title:
            return request.app.fail(msg="文档标题不能为空")
        
        if not document_type:
            return request.app.fail(msg="文档类型不能为空")
        
        # 根据上传方式处理
        doc = None
        file_path = None
        file_size = 0
        
        if file and hasattr(file, 'filename'):
            # 文件上传
            # 检查文件类型
            allowed_types = ['pdf', 'docx', 'pptx', 'txt', 'md', 'html', 'htm', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
            file_ext = file.filename.split('.')[-1].lower() if file.filename else ''
            if file_ext not in allowed_types:
                return request.app.fail(msg=f"不支持的文件类型: {file_ext}")
            
            # 保存文件
            upload_dir = f"uploads/knowledge/{kb_id}"
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, file.filename)
            file_content = await file.read()
            with open(file_path, "wb") as buffer:
                buffer.write(file_content)
            
            file_size = len(file_content)
            
            # 创建文档记录
            doc = await aitestrebortDocument.create(
                knowledge_base=kb,
                title=title,
                document_type=document_type,
                file_path=file_path,
                file_size=file_size,
                uploader_id=request.state.user.id,
                status='pending'
            )
            
        elif content:
            # 文本内容上传
            doc = await aitestrebortDocument.create(
                knowledge_base=kb,
                title=title,
                document_type='txt',
                content=content,
                file_size=len(content.encode('utf-8')),
                uploader_id=request.state.user.id,
                status='pending'
            )
            
        elif url:
            # URL上传
            doc = await aitestrebortDocument.create(
                knowledge_base=kb,
                title=title,
                document_type='url',
                url=url,
                uploader_id=request.state.user.id,
                status='pending'
            )
        else:
            return request.app.fail(msg="请提供文件、文本内容或URL")
        
        # 异步处理文档
        processing_error = None
        try:
            logger.info(f"Starting document processing for document {doc.id}")
            kb_service = KnowledgeBaseService(str(kb.id))
            
            logger.info(f"Initializing knowledge base service for KB {kb.id}")
            await kb_service.initialize()
            
            logger.info(f"Processing document {doc.id}")
            result = await kb_service.process_document(str(doc.id))
            
            logger.info(f"Document processing result: {result}")
            
            if not result['success']:
                processing_error = result.get('message', '处理失败')
                logger.error(f"Document processing failed: {processing_error}")
                # 更新文档状态为失败
                doc.status = 'failed'
                doc.error_message = processing_error
                await doc.save()
                
        except Exception as e:
            processing_error = str(e)
            logger.error(f"Document processing failed with exception: {e}", exc_info=True)
            # 更新文档状态为失败
            try:
                doc.status = 'failed'
                doc.error_message = processing_error
                await doc.save()
            except:
                pass
        
        # 返回结果，包含处理状态
        response_data = {
            'id': str(doc.id),
            'title': doc.title,
            'status': doc.status,
        }
        
        if processing_error:
            response_data['message'] = f'文档上传成功，但处理失败: {processing_error}'
            response_data['error'] = processing_error
        else:
            response_data['message'] = '文档上传并处理成功'
        
        return request.app.post_success(data=response_data)
        
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
        from app.services.aitestrebort.rag_service import RAGService
        
        logger.info(f"Query knowledge base: project_id={project_id}, kb_id={kb_id}, query={query_data.get('query', '')[:50]}")
        
        # 检查权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            return request.app.forbidden(msg="无权限访问此项目")
        
        kb = await aitestrebortKnowledgeBase.get(id=kb_id, project=project)
        logger.info(f"Knowledge base found: {kb.name}")
        
        query_text = query_data.get('query', '')
        top_k = query_data.get('top_k', 5)
        score_threshold = query_data.get('score_threshold', 0.3)
        use_rag = query_data.get('use_rag', False)  # 是否使用 RAG 生成回答
        
        if not query_text:
            return request.app.fail(msg="查询内容不能为空")
        
        # 检查知识库是否有文档
        doc_count = await aitestrebortDocument.filter(knowledge_base=kb, status='completed').count()
        if doc_count == 0:
            logger.warning(f"Knowledge base {kb_id} has no completed documents")
            return request.app.get_success(data={
                'query': query_text,
                'results': [],
                'retrieval_time': 0,
                'total_results': 0,
                'message': '知识库中还没有已处理的文档'
            })
        
        logger.info(f"Knowledge base has {doc_count} completed documents")
        
        # 初始化知识库服务
        logger.info("Initializing knowledge base service...")
        kb_service = KnowledgeBaseService(str(kb.id))
        await kb_service.initialize()
        logger.info("Knowledge base service initialized")
        
        if use_rag:
            # 使用 RAG 生成回答
            logger.info("Using RAG mode")
            
            # 初始化 RAG 服务
            rag_service = RAGService(kb_service)
            
            # 获取 LLM 配置
            # 优先使用请求中的配置，否则使用全局默认配置
            llm_config = None
            
            if query_data.get('llm_api_key'):
                # 使用请求中提供的配置
                llm_config = {
                    'provider': query_data.get('llm_provider', 'openai'),
                    'model': query_data.get('llm_model', 'gpt-3.5-turbo'),
                    'api_key': query_data.get('llm_api_key'),
                    'base_url': query_data.get('llm_base_url'),
                    'temperature': query_data.get('temperature', 0.7)
                }
            else:
                # 尝试获取全局默认 LLM 配置
                try:
                    from app.models.aitestrebort.project import aitestrebortLLMConfig
                    
                    # 优先获取全局默认配置（project_id 为 None 且 is_default=True）
                    global_llm = await aitestrebortLLMConfig.filter(
                        project_id=None,
                        is_default=True,
                        is_active=True
                    ).first()
                    
                    if not global_llm:
                        # 如果没有全局默认配置，获取项目的默认配置
                        global_llm = await aitestrebortLLMConfig.filter(
                            project_id=project_id,
                            is_default=True,
                            is_active=True
                        ).first()
                    
                    if not global_llm:
                        # 如果还是没有，获取任意一个全局配置
                        global_llm = await aitestrebortLLMConfig.filter(
                            project_id=None,
                            is_active=True
                        ).first()
                    
                    if not global_llm:
                        # 最后尝试获取项目的任意配置
                        global_llm = await aitestrebortLLMConfig.filter(
                            project_id=project_id,
                            is_active=True
                        ).first()
                    
                    if global_llm:
                        logger.info(f"Using LLM config: {global_llm.config_name or global_llm.name} (ID: {global_llm.id})")
                        llm_config = {
                            'provider': global_llm.provider,
                            'model': global_llm.model_name or global_llm.name,
                            'api_key': global_llm.api_key,
                            'base_url': global_llm.base_url,
                            'temperature': global_llm.temperature
                        }
                    else:
                        logger.warning("No LLM config found")
                        
                except Exception as e:
                    logger.error(f"Failed to get LLM config: {e}")
            
            if not llm_config or not llm_config.get('api_key'):
                # 没有可用的 LLM 配置
                return request.app.fail(msg="未配置 LLM，请在全局配置中设置默认 LLM 或在查询时提供 LLM 配置")
            
            # 执行 RAG 查询
            result = await rag_service.query(
                query_text=query_text,
                top_k=top_k,
                score_threshold=score_threshold,
                system_prompt=query_data.get('system_prompt'),
                prompt_template=query_data.get('prompt_template', 'default'),
                llm_config=llm_config
            )
            
            # 保存查询日志
            if result['success']:
                await rag_service.save_query_log(
                    query_text=query_text,
                    answer=result['answer'],
                    context_chunks=result.get('context_chunks', []),
                    retrieval_time=result['retrieval_time'],
                    generation_time=result['generation_time'],
                    total_time=result['total_time']
                )
            
            # 格式化返回数据，确保前端可以正确显示
            response_data = {
                'success': result['success'],
                'message': result.get('message', ''),
                'query': result['query'],
                'answer': result.get('answer', ''),
                'sources': result.get('context_chunks', []),  # 前端期望的字段名
                'context_chunks': result.get('context_chunks', []),  # 保留兼容性
                'retrieval_time': result.get('retrieval_time', 0),
                'generation_time': result.get('generation_time', 0),
                'total_time': result.get('total_time', 0)
            }
            
            return request.app.get_success(data=response_data)
        
        else:
            # 仅检索，不生成回答
            logger.info("Using retrieval-only mode")
            start_time = time.time()
            
            search_results = await kb_service.search_knowledge(
                query=query_text,
                top_k=top_k,
                score_threshold=score_threshold
            )
            logger.info(f"Search completed, found {len(search_results)} results")
            
            retrieval_time = time.time() - start_time
            
            # 记录查询日志
            try:
                await aitestrebortKnowledgeQuery.create(
                    knowledge_base=kb,
                    user_id=request.state.user.id,
                    query=query_text,
                    retrieved_chunks=[r['metadata'] for r in search_results],
                    similarity_scores=[r.get('score', 0) for r in search_results],
                    retrieval_time=retrieval_time,
                    total_time=retrieval_time
                )
                logger.info("Query log saved")
            except Exception as log_error:
                logger.error(f"Failed to save query log: {log_error}")
            
            return request.app.get_success(data={
                'query': query_text,
                'sources': search_results,
                'results': search_results,
                'retrieval_time': retrieval_time,
                'total_results': len(search_results)
            })
        
    except DoesNotExist:
        logger.error(f"Knowledge base not found: {kb_id}")
        return request.app.fail(msg="知识库不存在")
    except Exception as e:
        logger.error(f"Failed to query knowledge base: {e}", exc_info=True)
        return request.app.error(msg=f"查询知识库失败: {str(e)}")


async def query_knowledge_base_stream(request: Request, project_id: int, kb_id: str, query_data: dict):
    """查询知识库（RAG功能 - 流式响应）"""
    from fastapi.responses import StreamingResponse
    from app.models.aitestrebort import aitestrebortProject, aitestrebortProjectMember
    from app.services.aitestrebort.rag_service import RAGService
    
    try:
        # 检查权限
        project = await aitestrebortProject.get(id=project_id)
        member = await aitestrebortProjectMember.filter(
            project=project, user_id=request.state.user.id
        ).first()
        if not member:
            # 返回错误的 SSE 流
            async def error_stream():
                yield f"data: {{'type': 'error', 'message': '无权限访问此项目'}}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(error_stream(), media_type="text/event-stream")
        
        kb = await aitestrebortKnowledgeBase.get(id=kb_id, project=project)
        
        query_text = query_data.get('query', '')
        top_k = query_data.get('top_k', 5)
        score_threshold = query_data.get('score_threshold', 0.3)
        
        if not query_text:
            async def error_stream():
                yield f"data: {{'type': 'error', 'message': '查询内容不能为空'}}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(error_stream(), media_type="text/event-stream")
        
        # 初始化服务
        kb_service = KnowledgeBaseService(str(kb.id))
        await kb_service.initialize()
        
        rag_service = RAGService(kb_service)
        
        # 获取 LLM 配置
        llm_config = {
            'provider': query_data.get('llm_provider', 'openai'),
            'model': query_data.get('llm_model', 'gpt-3.5-turbo'),
            'api_key': query_data.get('llm_api_key'),
            'base_url': query_data.get('llm_base_url'),
            'temperature': query_data.get('temperature', 0.7)
        }
        
        # 返回流式响应
        return StreamingResponse(
            rag_service.query_stream(
                query_text=query_text,
                top_k=top_k,
                score_threshold=score_threshold,
                system_prompt=query_data.get('system_prompt'),
                llm_config=llm_config
            ),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        logger.error(f"Failed to stream query: {e}", exc_info=True)
        async def error_stream():
            yield f"data: {{'type': 'error', 'message': '{str(e)}'}}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")


# ==================== 辅助函数 ====================

def mask_api_key(api_key: str) -> str:
    """对API密钥进行脱敏处理"""
    if not api_key:
        return ""
    
    if len(api_key) <= 8:
        return '*' * len(api_key)
    
    return api_key[:4] + '*' * (len(api_key) - 8) + api_key[-4:]


# ==================== 文档详情和操作 ====================

async def get_document_detail(request: Request, project_id: int, kb_id: str, doc_id: str):
    """获取文档详情"""
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
        doc = await aitestrebortDocument.get(id=doc_id, knowledge_base=kb)
        
        # 获取分块数量
        chunk_count = await aitestrebortDocumentChunk.filter(document=doc).count()
        
        data = {
            'id': str(doc.id),
            'title': doc.title,
            'document_type': doc.document_type,
            'status': doc.status,
            'file_path': doc.file_path,
            'url': doc.url,
            'content': doc.content,
            'file_size': doc.file_size,
            'page_count': doc.page_count,
            'word_count': doc.word_count,
            'chunk_count': chunk_count,
            'error_message': doc.error_message,
            'uploaded_at': doc.uploaded_at.isoformat(),
            'processed_at': doc.processed_at.isoformat() if doc.processed_at else None
        }
        
        return request.app.get_success(data=data)
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Failed to get document detail: {e}")
        return request.app.error(msg=f"获取文档详情失败: {str(e)}")


async def get_document_content(request: Request, project_id: int, kb_id: str, doc_id: str):
    """获取文档内容（用于详情弹窗）"""
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
        doc = await aitestrebortDocument.get(id=doc_id, knowledge_base=kb)
        
        # 获取分块数量
        chunk_count = await aitestrebortDocumentChunk.filter(document=doc).count()
        
        # 获取上传者信息
        uploader_name = "未知"
        if doc.uploader_id:
            from app.models.system.user import User
            try:
                uploader = await User.get(id=doc.uploader_id)
                uploader_name = uploader.name
            except Exception as e:
                logger.warning(f"Failed to get uploader for doc {doc.id}: {e}")
        
        data = {
            'id': str(doc.id),
            'title': doc.title,
            'document_type': doc.document_type,
            'status': doc.status,
            'file_size': doc.file_size,
            'page_count': doc.page_count,
            'word_count': doc.word_count,
            'chunk_count': chunk_count,
            'error_message': doc.error_message,
            'uploader_name': uploader_name,
            'uploaded_at': doc.uploaded_at.isoformat(),
            'processed_at': doc.processed_at.isoformat() if doc.processed_at else None,
            'content': doc.content or '',
            'url': doc.url or '',
            'file_path': doc.file_path or ''
        }
        
        return request.app.get_success(data=data)
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Failed to get document content: {e}")
        return request.app.error(msg=f"获取文档内容失败: {str(e)}")


async def get_document_chunks(request: Request, project_id: int, kb_id: str, doc_id: str, params: dict = None):
    """获取文档分块列表"""
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
        doc = await aitestrebortDocument.get(id=doc_id, knowledge_base=kb)
        
        # 获取分块
        chunks = await aitestrebortDocumentChunk.filter(document=doc).order_by('chunk_index').all()
        
        data = []
        for chunk in chunks:
            data.append({
                'id': str(chunk.id),
                'chunk_index': chunk.chunk_index,
                'content': chunk.content,
                'start_index': chunk.start_index,
                'end_index': chunk.end_index,
                'page_number': chunk.page_number,
                'created_at': chunk.created_at.isoformat()
            })
        
        return request.app.get_success(data={'chunks': data})
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Failed to get document chunks: {e}")
        return request.app.error(msg=f"获取文档分块失败: {str(e)}")


async def delete_document(request: Request, project_id: int, kb_id: str, doc_id: str):
    """删除文档"""
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
        doc = await aitestrebortDocument.get(id=doc_id, knowledge_base=kb)
        
        # 删除文件
        if doc.file_path and os.path.exists(doc.file_path):
            os.remove(doc.file_path)
        
        # TODO: 从向量存储中删除
        
        # 删除数据库记录（会级联删除分块）
        await doc.delete()
        
        return request.app.delete_success(data={"message": "文档删除成功"})
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        return request.app.error(msg=f"删除文档失败: {str(e)}")


async def reprocess_document(request: Request, project_id: int, kb_id: str, doc_id: str):
    """重新处理文档"""
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
        doc = await aitestrebortDocument.get(id=doc_id, knowledge_base=kb)
        
        # 重置状态
        doc.status = 'pending'
        doc.error_message = None
        await doc.save()
        
        # 重新处理文档
        kb_service = KnowledgeBaseService(str(kb.id))
        await kb_service.initialize()
        result = await kb_service.process_document(str(doc.id))
        
        return request.app.post_success(data={
            'message': '文档重新处理已开始',
            'result': result
        })
        
    except DoesNotExist:
        return request.app.fail(msg="文档不存在")
    except Exception as e:
        logger.error(f"Failed to reprocess document: {e}")
        return request.app.error(msg=f"重新处理文档失败: {str(e)}")


# ==================== 系统状态 ====================

async def get_system_status(request: Request):
    """获取系统状态"""
    try:
        # 统计所有知识库
        total_kb = await aitestrebortKnowledgeBase.all().count()
        
        # 统计所有文档
        total_docs = await aitestrebortDocument.all().count()
        processing_docs = await aitestrebortDocument.filter(status='processing').count()
        
        # 统计所有分块
        total_chunks = await aitestrebortDocumentChunk.all().count()
        
        # 检查向量模型连接状态
        system_status = 'healthy'
        status_message = None
        
        try:
            # 直接从数据库获取配置
            config = await aitestrebortKnowledgeConfig.get_or_none(id=1)
            
            if config and config.embedding_service:
                # 构建嵌入配置
                embedding_config = {
                    'base_url': config.api_base_url,
                    'api_key': config.api_key,
                    'model': config.model_name,
                    'timeout': 30.0
                }
                
                # 根据服务类型添加headers
                if config.api_key:
                    embedding_config['headers'] = {
                        'Authorization': f'Bearer {config.api_key}',
                        'Content-Type': 'application/json'
                    }
                
                # 导入并创建嵌入服务实例
                from app.services.ai.embedding_service import EmbeddingService
                
                # 根据服务类型创建实例
                provider = config.embedding_service
                if provider == 'openai':
                    provider = 'openai'
                elif provider == 'azure':
                    provider = 'azure_openai'
                elif provider == 'ollama':
                    provider = 'ollama'
                else:
                    provider = 'custom'
                
                embedding_service = EmbeddingService(provider=provider, config=embedding_config)
                
                # 测试嵌入服务
                test_text = "系统健康检查测试"
                await embedding_service.create_embeddings(test_text)
                
                logger.info("向量模型连接正常")
            else:
                system_status = 'warning'
                status_message = '未配置嵌入服务'
                logger.warning("未配置嵌入服务")
                
        except Exception as embed_error:
            system_status = 'error'
            status_message = f'向量模型连接异常: {str(embed_error)}'
            logger.error(f"向量模型连接检查失败: {embed_error}")
        
        data = {
            'total_knowledge_bases': total_kb,
            'total_documents': total_docs,
            'processing_documents': processing_docs,
            'total_chunks': total_chunks,
            'system_status': system_status,
            'status_message': status_message
        }
        
        return request.app.get_success(data=data)
        
    except Exception as e:
        logger.error(f"Failed to get system status: {e}")
        return request.app.error(msg=f"获取系统状态失败: {str(e)}")


async def get_knowledge_base_service(kb_id: str):
    """
    获取知识库服务实例
    Args:
        kb_id: 知识库ID
    Returns:
        KnowledgeBaseService实例或None
    """
    try:
        # 检查知识库是否存在
        kb = await aitestrebortKnowledgeBase.get_or_none(id=kb_id)
        if not kb:
            logger.warning(f"Knowledge base not found: {kb_id}")
            return None
        
        # 创建并初始化服务
        kb_service = KnowledgeBaseService(kb_id)
        await kb_service.initialize()
        
        logger.info(f"Knowledge base service initialized: {kb_id}")
        return kb_service
        
    except Exception as e:
        logger.error(f"Failed to get knowledge base service: {e}", exc_info=True)
        return None
