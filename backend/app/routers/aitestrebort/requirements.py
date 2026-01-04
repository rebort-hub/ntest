"""
需求管理API路由
"""
from typing import List, Optional
from fastapi import HTTPException, UploadFile, File, Form, Request
import uuid
import logging

from app.routers.base_view import APIRouter
from app.services.aitestrebort.requirements_service import RequirementService
from app.schemas.aitestrebort.requirements import (
    RequirementDocumentCreate, RequirementDocumentUpdate, RequirementDocumentResponse,
    RequirementDocumentDetail, RequirementDocumentListResponse,
    RequirementCreate, RequirementUpdate, RequirementResponse,
    RequirementListResponse, RequirementSearchRequest,
    RequirementStatistics, ProjectStatistics,
    RequirementUploadRequest, DocumentSplitRequest,
    ReviewRequest, ReviewReportResponse, ReviewProgressResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aitestrebort/requirements", tags=["aitestrebort - 需求管理"])


def get_requirement_service() -> RequirementService:
    """获取需求管理服务实例"""
    return RequirementService()


# ==================== 需求文档管理 ====================

@router.post("/projects/{project_id}/documents")
async def create_requirement_document(
    request: Request,
    project_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    document_type: str = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """
    创建需求文档
    支持文件上传和手动创建
    """
    try:
        service = get_requirement_service()
        document_data = RequirementDocumentCreate(
            project_id=project_id,
            title=title,
            description=description,
            document_type=document_type
        )
        
        document = await service.create_requirement_document(
            project_id=project_id,
            document_data=document_data,
            file=file,
            user_id=1  # TODO: 从认证中获取用户ID
        )
        
        result = RequirementDocumentResponse.model_validate(document.__dict__)
        return request.app.post_success(data=result.model_dump())
        
    except Exception as e:
        logger.error(f"创建需求文档失败: {e}")
        return request.app.error(msg=f"创建需求文档失败: {str(e)}")


@router.get("/projects/{project_id}/documents")
async def get_requirement_documents(
    request: Request,
    project_id: int,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取需求文档列表"""
    try:
        service = get_requirement_service()
        
        # 首先尝试从数据库获取
        documents, total = await service.get_requirement_documents(
            project_id=project_id,
            search=search,
            status=status,
            page=page,
            page_size=page_size
        )
        
        # 如果数据库中没有数据，尝试从文件系统读取
        if total == 0:
            logger.info(f"数据库中没有找到项目 {project_id} 的需求文档，尝试从文件系统读取")
            documents, total = await service.get_documents_from_filesystem(
                project_id=project_id,
                search=search,
                page=page,
                page_size=page_size
            )
        
        items = []
        for doc in documents:
            # 确保返回的数据格式正确
            doc_dict = doc.__dict__ if hasattr(doc, '__dict__') else {
                'id': getattr(doc, 'id', ''),
                'title': getattr(doc, 'title', ''),
                'description': getattr(doc, 'description', ''),
                'document_type': getattr(doc, 'document_type', ''),
                'content': getattr(doc, 'content', ''),
                'status': getattr(doc, 'status', ''),
                'created_at': getattr(doc, 'uploaded_at', None),
                'updated_at': getattr(doc, 'updated_at', None),
                'project_id': getattr(doc, 'project_id', project_id),
                'word_count': getattr(doc, 'word_count', 0),
                'page_count': getattr(doc, 'page_count', 0),
                'file_path': getattr(doc, 'file_path', ''),
                'uploader_id': getattr(doc, 'uploader_id', None),
                'uploaded_at': getattr(doc, 'uploaded_at', None)
            }
            
            # 格式化时间字段
            if doc_dict.get('uploaded_at'):
                doc_dict['uploaded_at'] = doc_dict['uploaded_at'].isoformat() if hasattr(doc_dict['uploaded_at'], 'isoformat') else str(doc_dict['uploaded_at'])
            if doc_dict.get('updated_at'):
                doc_dict['updated_at'] = doc_dict['updated_at'].isoformat() if hasattr(doc_dict['updated_at'], 'isoformat') else str(doc_dict['updated_at'])
            
            items.append(doc_dict)
        
        pages = (total + page_size - 1) // page_size
        
        result = {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": pages
        }
        
        return request.app.get_success(data=result)
        
    except Exception as e:
        logger.error(f"获取需求文档列表失败: {e}")
        return request.app.error(msg=f"获取需求文档列表失败: {str(e)}")


@router.get("/projects/{project_id}/requirements-for-diagram")
async def get_requirements_for_diagram(
    request: Request,
    project_id: int,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取需求数据用于AI图表生成"""
    try:
        service = get_requirement_service()
        
        # 获取需求数据
        from app.schemas.aitestrebort.requirements import RequirementSearchRequest
        search_params = RequirementSearchRequest(
            keyword=search,
            type=None,
            priority=None,
            status=None,
            page=page,
            page_size=page_size
        )
        
        requirements, total = await service.get_requirements(project_id, search_params)
        
        # 将需求数据转换为图表生成所需的格式
        items = []
        for req in requirements:
            doc_item = {
                "id": str(req.id),
                "title": req.title,
                "description": req.description,
                "document_type": "requirement",
                "content": req.description,
                "status": req.status,
                "created_at": req.created_at.isoformat() if req.created_at else None,
                "updated_at": req.updated_at.isoformat() if req.updated_at else None,
                "project_id": req.project_id
            }
            items.append(doc_item)
        
        pages = (total + page_size - 1) // page_size
        
        result = {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": pages
        }
        
        return request.app.get_success(data=result)
        
    except Exception as e:
        logger.error(f"获取需求数据失败: {e}")
        return request.app.error(msg=f"获取需求数据失败: {str(e)}")


@router.get("/projects/{project_id}/documents/{document_id}")
async def get_requirement_document(
    request: Request,
    project_id: int,
    document_id: uuid.UUID
):
    """获取需求文档详情"""
    try:
        service = get_requirement_service()
        document = await service.get_requirement_document(document_id)
        
        # 检查项目权限
        if document.project_id != project_id:
            return request.app.error(msg="无权限访问此文档", code=403)
        
        result = RequirementDocumentDetail.model_validate(document.__dict__)
        return request.app.get_success(data=result.model_dump())
        
    except Exception as e:
        logger.error(f"获取需求文档详情失败: {e}")
        return request.app.error(msg=f"获取需求文档详情失败: {str(e)}")


@router.put("/projects/{project_id}/documents/{document_id}", response_model=RequirementDocumentResponse)
async def update_requirement_document(
    project_id: int,
    document_id: uuid.UUID,
    update_data: RequirementDocumentUpdate
):
    """更新需求文档"""
    try:
        service = get_requirement_service()
        # 检查文档是否属于该项目
        document = await service.get_requirement_document(document_id)
        if document.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        updated_document = await service.update_requirement_document(document_id, update_data)
        return RequirementDocumentResponse.model_validate(updated_document.__dict__)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新需求文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/projects/{project_id}/documents/{document_id}")
async def delete_requirement_document(
    request: Request,
    project_id: int,
    document_id: uuid.UUID
):
    """删除需求文档"""
    try:
        service = get_requirement_service()
        # 检查文档是否属于该项目
        document = await service.get_requirement_document(document_id)
        if document.project_id != project_id:
            return request.app.error(msg="无权限访问此文档", code=403)
        
        success = await service.delete_requirement_document(document_id)
        if success:
            return request.app.success(msg="需求文档删除成功")  # 使用success方法自定义消息
        else:
            return request.app.error(msg="删除失败")
        
    except Exception as e:
        logger.error(f"删除需求文档失败: {e}")
        return request.app.error(msg=f"删除需求文档失败: {str(e)}")


# ==================== 手动需求管理 ====================

@router.post("/projects/{project_id}/requirements")
async def create_requirement(
    request: Request,
    project_id: int,
    requirement_data: RequirementCreate
):
    """创建需求"""
    try:
        service = get_requirement_service()
        requirement = await service.create_requirement(
            project_id=project_id,
            requirement_data=requirement_data,
            user_id=1,  # TODO: 从认证中获取用户ID
            user_name="测试用户"  # TODO: 从认证中获取用户名
        )
        
        result = RequirementResponse.model_validate(requirement.__dict__)
        return request.app.post_success(data=result.model_dump())
        
    except Exception as e:
        logger.error(f"创建需求失败: {e}")
        return request.app.error(msg=f"创建需求失败: {str(e)}")


@router.get("/projects/{project_id}/requirements")
async def get_requirements(
    request: Request,
    project_id: int,
    search: Optional[str] = None,
    type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取需求列表"""
    try:
        service = get_requirement_service()
        search_params = RequirementSearchRequest(
            keyword=search,
            type=type,
            priority=priority,
            status=status,
            page=page,
            page_size=page_size
        )
        
        requirements, total = await service.get_requirements(project_id, search_params)
        
        items = [RequirementResponse.model_validate(req.__dict__) for req in requirements]
        pages = (total + page_size - 1) // page_size
        
        result = RequirementListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=pages
        )
        
        return request.app.get_success(data=result.model_dump())
        
    except Exception as e:
        logger.error(f"获取需求列表失败: {e}")
        return request.app.error(msg=f"获取需求列表失败: {str(e)}")


@router.get("/projects/{project_id}/requirements/{requirement_id}")
async def get_requirement(
    request: Request,
    project_id: int,
    requirement_id: uuid.UUID
):
    """获取需求详情"""
    try:
        service = get_requirement_service()
        requirement = await service.get_requirement(requirement_id)
        
        # 检查项目权限
        if requirement.project_id != project_id:
            return request.app.error(msg="无权限访问此需求", code=403)
        
        result = RequirementResponse.model_validate(requirement.__dict__)
        return request.app.get_success(data=result.model_dump())
        
    except Exception as e:
        logger.error(f"获取需求详情失败: {e}")
        return request.app.error(msg=f"获取需求详情失败: {str(e)}")


@router.put("/projects/{project_id}/requirements/{requirement_id}")
async def update_requirement(
    request: Request,
    project_id: int,
    requirement_id: uuid.UUID,
    update_data: RequirementUpdate
):
    """更新需求"""
    try:
        service = get_requirement_service()
        # 检查需求是否属于该项目
        requirement = await service.get_requirement(requirement_id)
        if requirement.project_id != project_id:
            return request.app.error(msg="无权限访问此需求", code=403)
        
        updated_requirement = await service.update_requirement(requirement_id, update_data)
        result = RequirementResponse.model_validate(updated_requirement.__dict__)
        return request.app.success(msg="需求更新成功", data=result.model_dump())
        
    except Exception as e:
        logger.error(f"更新需求失败: {e}")
        return request.app.error(msg=f"更新需求失败: {str(e)}")


@router.delete("/projects/{project_id}/requirements/{requirement_id}")
async def delete_requirement(
    request: Request,
    project_id: int,
    requirement_id: uuid.UUID
):
    """删除需求"""
    try:
        service = get_requirement_service()
        # 检查需求是否属于该项目
        requirement = await service.get_requirement(requirement_id)
        if requirement.project_id != project_id:
            return request.app.error(msg="无权限访问此需求", code=403)
        
        success = await service.delete_requirement(requirement_id)
        if success:
            return request.app.success(msg="需求删除成功")  # 使用success方法自定义消息
        else:
            return request.app.error(msg="删除失败")
        
    except Exception as e:
        logger.error(f"删除需求失败: {e}")
        return request.app.error(msg=f"删除需求失败: {str(e)}")


# ==================== 需求功能扩展 ====================

@router.post("/projects/{project_id}/requirements/{requirement_id}/generate-test-cases")
async def generate_test_cases(
    request: Request,
    project_id: int,
    requirement_id: uuid.UUID
):
    """为需求生成测试用例"""
    try:
        service = get_requirement_service()
        # 检查需求是否属于该项目
        requirement = await service.get_requirement(requirement_id)
        if requirement.project_id != project_id:
            return request.app.error(msg="无权限访问此需求", code=403)
        
        test_cases = await service.generate_test_cases(requirement_id)
        return request.app.success(msg="测试用例生成成功", data=test_cases)  # 使用success方法
        
    except Exception as e:
        logger.error(f"生成测试用例失败: {e}")
        return request.app.error(msg=f"生成测试用例失败: {str(e)}")


# ==================== 统计功能 ====================

@router.get("/projects/{project_id}/statistics", response_model=RequirementStatistics)
async def get_requirement_statistics(
    project_id: int
):
    """获取需求统计信息"""
    try:
        service = get_requirement_service()
        statistics = await service.get_requirement_statistics(project_id)
        return statistics
        
    except Exception as e:
        logger.error(f"获取需求统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/system-statistics")
async def get_project_statistics(
    request: Request,
    project_id: int
):
    """获取项目系统统计信息"""
    try:
        service = get_requirement_service()
        statistics = await service.get_project_statistics(project_id)
        return request.app.get_success(data=statistics.model_dump())
        
    except Exception as e:
        logger.error(f"获取项目统计失败: {e}")
        return request.app.error(msg=f"获取项目统计失败: {str(e)}")


# ==================== 文档处理功能 ====================

@router.post("/projects/{project_id}/documents/{document_id}/split-modules")
async def split_document_modules(
    project_id: int,
    document_id: uuid.UUID,
    split_request: DocumentSplitRequest
):
    """智能模块拆分"""
    try:
        service = get_requirement_service()
        # 检查文档是否属于该项目
        document = await service.get_requirement_document(document_id)
        if document.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        # TODO: 实现模块拆分逻辑
        return {
            "message": "模块拆分功能开发中",
            "document_id": str(document_id),
            "split_options": split_request.model_dump()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"模块拆分失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/documents/{document_id}/start-review")
async def start_document_review(
    request: Request,
    project_id: int,
    document_id: uuid.UUID,
    review_data: Optional[ReviewRequest] = None
):
    """开始需求评审"""
    try:
        service = get_requirement_service()
        # 检查文档是否属于该项目
        document = await service.get_requirement_document(document_id)
        if document.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        # 开始评审
        review_report = await service.start_document_review(
            document_id=document_id,
            review_type=review_data.review_type if review_data else "comprehensive",
            focus_areas=review_data.focus_areas if review_data else None,
            user_id=1  # TODO: 从认证中获取用户ID
        )
        
        result = ReviewReportResponse.model_validate(review_report.__dict__)
        return request.app.post_success(data=result.model_dump())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"开始评审失败: {e}")
        return request.app.error(msg=f"开始评审失败: {str(e)}")


# ==================== 评审管理 ====================

@router.get("/reviews")
async def get_review_results(
    request: Request,
    project_id: int,
    document_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取评审结果列表"""
    try:
        service = get_requirement_service()
        reviews, total = await service.get_review_results(
            project_id=project_id,
            document_id=document_id,
            status=status,
            page=page,
            page_size=page_size
        )
        
        items = [ReviewReportResponse.model_validate(review.__dict__) for review in reviews]
        pages = (total + page_size - 1) // page_size
        
        result = {
            "items": [item.model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": pages
        }
        
        return request.app.get_success(data=result)
        
    except Exception as e:
        logger.error(f"获取评审结果失败: {e}")
        return request.app.error(msg=f"获取评审结果失败: {str(e)}")


@router.get("/reviews/{review_id}")
async def get_review_detail(
    request: Request,
    review_id: uuid.UUID
):
    """获取评审详情"""
    try:
        service = get_requirement_service()
        review = await service.get_review_detail(review_id)
        
        result = ReviewReportResponse.model_validate(review.__dict__)
        return request.app.get_success(data=result.model_dump())
        
    except Exception as e:
        logger.error(f"获取评审详情失败: {e}")
        return request.app.error(msg=f"获取评审详情失败: {str(e)}")


@router.get("/reviews/{review_id}/progress")
async def get_review_progress(
    request: Request,
    review_id: uuid.UUID
):
    """获取评审进度"""
    try:
        service = get_requirement_service()
        progress = await service.get_review_progress(review_id)
        
        result = ReviewProgressResponse.model_validate(progress)
        return request.app.get_success(data=result.model_dump())
        
    except Exception as e:
        logger.error(f"获取评审进度失败: {e}")
        return request.app.error(msg=f"获取评审进度失败: {str(e)}")