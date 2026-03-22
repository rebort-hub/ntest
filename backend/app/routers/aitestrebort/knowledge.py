"""
知识库管理路由
"""
from app.routers.base_view import APIRouter
from app.services.aitestrebort import knowledge_enhanced as knowledge_service
from app.schemas.aitestrebort.knowledge import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    QueryRequest,
    KnowledgeBaseQueryForm,
    DocumentQueryForm
)

router = APIRouter(prefix="/aitestrebort/knowledge", tags=["aitestrebort - 知识库管理"])

# 全局配置管理
router.add_get_route("/global-config", knowledge_service.get_global_config, summary="获取全局配置")
router.add_put_route("/global-config", knowledge_service.update_global_config, summary="更新全局配置")
router.add_post_route("/test-embedding-connection", knowledge_service.test_embedding_connection, summary="测试嵌入服务连接")
router.add_get_route("/embedding-services", knowledge_service.get_embedding_services, summary="获取可用的嵌入服务")

# 项目级别的知识库管理
router.add_get_route("/projects/{project_id}/knowledge-bases", knowledge_service.get_knowledge_bases, summary="获取知识库列表")
router.add_post_route("/projects/{project_id}/knowledge-bases", knowledge_service.create_knowledge_base, summary="创建知识库")
router.add_get_route("/projects/{project_id}/knowledge-bases/{kb_id}", knowledge_service.get_knowledge_base_detail, summary="获取知识库详情")
router.add_put_route("/projects/{project_id}/knowledge-bases/{kb_id}", knowledge_service.update_knowledge_base, summary="更新知识库")
router.add_delete_route("/projects/{project_id}/knowledge-bases/{kb_id}", knowledge_service.delete_knowledge_base, summary="删除知识库")

# 知识库扩展功能
router.add_get_route("/projects/{project_id}/knowledge-bases/{kb_id}/statistics", knowledge_service.get_knowledge_base_detail, summary="获取知识库统计信息")

# 文档管理
router.add_get_route("/projects/{project_id}/knowledge-bases/{kb_id}/documents", knowledge_service.get_documents, summary="获取文档列表")
router.add_post_route("/projects/{project_id}/knowledge-bases/{kb_id}/documents", knowledge_service.upload_document, summary="上传文档")
router.add_get_route("/projects/{project_id}/knowledge-bases/{kb_id}/documents/{doc_id}", knowledge_service.get_document_detail, summary="获取文档详情")
router.add_get_route("/projects/{project_id}/knowledge-bases/{kb_id}/documents/{doc_id}/content", knowledge_service.get_document_content, summary="获取文档内容")
router.add_get_route("/projects/{project_id}/knowledge-bases/{kb_id}/documents/{doc_id}/chunks", knowledge_service.get_document_chunks, summary="获取文档分块")
router.add_delete_route("/projects/{project_id}/knowledge-bases/{kb_id}/documents/{doc_id}", knowledge_service.delete_document, summary="删除文档")
router.add_post_route("/projects/{project_id}/knowledge-bases/{kb_id}/documents/{doc_id}/process", knowledge_service.reprocess_document, summary="重新处理文档")

# RAG查询功能
router.add_post_route("/projects/{project_id}/knowledge-bases/{kb_id}/query", knowledge_service.query_knowledge_base, summary="查询知识库")
router.add_post_route("/projects/{project_id}/knowledge-bases/{kb_id}/query-stream", knowledge_service.query_knowledge_base_stream, summary="查询知识库（流式）")

# 系统状态
router.add_get_route("/system-status", knowledge_service.get_system_status, summary="获取系统状态")
