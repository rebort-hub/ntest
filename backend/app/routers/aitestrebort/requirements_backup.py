"""
需求管理API路由
"""
from typing import List, Optional
from fastapi import HTTPException, UploadFile, File, Form
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
    RequirementUploadRequest, DocumentSplitRequest
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/aitestrebort/requirements", tags=["aitestrebort - 需求管理"])


def get_requirement_service() -> RequirementService:
    """获取需求管理服务实例"""
    return RequirementService()


# ==================== 需求文档管理 ====================

@router.post("/projects/{project_id}/documents", response_model=RequirementDocumentResponse)
async def create_requirement_document(
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
            title=title,
            description=description,
            document_type=document_type,
            project_id=project_id
        )
        
        document = service.create_requirement_document(
            project_id=project_id,
            document_data=document_data,
            file=file,
            user_id=1  # TODO: 从认证中获取用户ID
        )
        
        return RequirementDocumentResponse.model_validate(document)
        
    except Exception as e:
        logger.error(f"创建需求文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/documents", response_model=RequirementDocumentListResponse)
async def get_requirement_documents(
    project_id: int,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取需求文档列表"""
            service = get_requirement_service()
        try:
        documents, total = service.get_requirement_documents(
            project_id=project_id,
            search=search,
            status=status,
            page=page,
            page_size=page_size
        )
        
        items = [RequirementDocumentResponse.model_validate(doc) for doc in documents]
        pages = (total + page_size - 1) // page_size
        
        return RequirementDocumentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"获取需求文档列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/documents/{document_id}", response_model=RequirementDocumentDetail)
async def get_requirement_document(
    project_id: int,
    document_id: uuid.UUID
):
    """获取需求文档详情"""
            service = get_requirement_service()
        try:
        document = service.get_requirement_document(document_id)
        
        # 检查项目权限
        if document.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        return RequirementDocumentDetail.model_validate(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取需求文档详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/projects/{project_id}/documents/{document_id}", response_model=RequirementDocumentResponse)
async def update_requirement_document(
    project_id: int,
    document_id: uuid.UUID,
    update_data: RequirementDocumentUpdate
):
    """更新需求文档"""
            service = get_requirement_service()
        try:
        # 检查文档是否属于该项目
        document = service.get_requirement_document(document_id)
        if document.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        updated_document = service.update_requirement_document(document_id, update_data)
        return RequirementDocumentResponse.model_validate(updated_document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新需求文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/projects/{project_id}/documents/{document_id}")
async def delete_requirement_document(
    project_id: int,
    document_id: uuid.UUID
):
    """删除需求文档"""
            service = get_requirement_service()
        try:
        # 检查文档是否属于该项目
        document = service.get_requirement_document(document_id)
        if document.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        success = service.delete_requirement_document(document_id)
        if success:
            return {"message": "需求文档删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除需求文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 手动需求管理 ====================

@router.post("/projects/{project_id}/requirements", response_model=RequirementResponse)
async def create_requirement(
    project_id: int,
    requirement_data: RequirementCreate
):
    """创建需求"""
            service = get_requirement_service()
        try:
        requirement = service.create_requirement(
            project_id=project_id,
            requirement_data=requirement_data,
            user_id=1,  # TODO: 从认证中获取用户ID
            user_name="测试用户"  # TODO: 从认证中获取用户名
        )
        
        return RequirementResponse.model_validate(requirement)
        
    except Exception as e:
        logger.error(f"创建需求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/requirements", response_model=RequirementListResponse)
async def get_requirements(
    project_id: int,
    search: Optional[str] = None,
    type: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """获取需求列表"""
            service = get_requirement_service()
        try:
        search_params = RequirementSearchRequest(
            search=search,
            type=type,
            priority=priority,
            status=status,
            page=page,
            page_size=page_size
        )
        
        requirements, total = service.get_requirements(project_id, search_params)
        
        items = [RequirementResponse.model_validate(req) for req in requirements]
        pages = (total + page_size - 1) // page_size
        
        return RequirementListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"获取需求列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/requirements/{requirement_id}", response_model=RequirementResponse)
async def get_requirement(
    project_id: int,
    requirement_id: uuid.UUID
):
    """获取需求详情"""
            service = get_requirement_service()
        try:
        requirement = service.get_requirement(requirement_id)
        
        # 检查项目权限
        if requirement.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此需求")
        
        return RequirementResponse.model_validate(requirement)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取需求详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/projects/{project_id}/requirements/{requirement_id}", response_model=RequirementResponse)
async def update_requirement(
    project_id: int,
    requirement_id: uuid.UUID,
    update_data: RequirementUpdate
):
    """更新需求"""
            service = get_requirement_service()
        try:
        # 检查需求是否属于该项目
        requirement = service.get_requirement(requirement_id)
        if requirement.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此需求")
        
        updated_requirement = service.update_requirement(requirement_id, update_data)
        return RequirementResponse.model_validate(updated_requirement)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新需求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/projects/{project_id}/requirements/{requirement_id}")
async def delete_requirement(
    project_id: int,
    requirement_id: uuid.UUID
):
    """删除需求"""
            service = get_requirement_service()
        try:
        # 检查需求是否属于该项目
        requirement = service.get_requirement(requirement_id)
        if requirement.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此需求")
        
        success = service.delete_requirement(requirement_id)
        if success:
            return {"message": "需求删除成功"}
        else:
            raise HTTPException(status_code=500, detail="删除失败")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除需求失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 需求功能扩展 ====================

@router.post("/projects/{project_id}/requirements/{requirement_id}/generate-test-cases")
async def generate_test_cases(
    project_id: int,
    requirement_id: uuid.UUID
):
    """为需求生成测试用例"""
            service = get_requirement_service()
        try:
        # 检查需求是否属于该项目
        requirement = service.get_requirement(requirement_id)
        if requirement.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此需求")
        
        test_cases = service.generate_test_cases(requirement_id)
        return {
            "message": "测试用例生成成功",
            "data": test_cases
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成测试用例失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 统计功能 ====================

@router.get("/projects/{project_id}/statistics", response_model=RequirementStatistics)
async def get_requirement_statistics(
    project_id: int
):
    """获取需求统计信息"""
            service = get_requirement_service()
        try:
        statistics = service.get_requirement_statistics(project_id)
        return statistics
        
    except Exception as e:
        logger.error(f"获取需求统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/system-statistics", response_model=ProjectStatistics)
async def get_project_statistics(
    project_id: int
):
    """获取项目系统统计信息"""
            service = get_requirement_service()
        try:
        statistics = service.get_project_statistics(project_id)
        return statistics
        
    except Exception as e:
        logger.error(f"获取项目统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 文档处理功能 ====================

@router.post("/projects/{project_id}/documents/{document_id}/split-modules")
async def split_document_modules(
    project_id: int,
    document_id: uuid.UUID,
    split_request: DocumentSplitRequest
):
    """智能模块拆分"""
            service = get_requirement_service()
        try:
        # 检查文档是否属于该项目
        document = service.get_requirement_document(document_id)
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
    project_id: int,
    document_id: uuid.UUID
):
    """开始需求评审"""
            service = get_requirement_service()
        try:
        # 检查文档是否属于该项目
        document = service.get_requirement_document(document_id)
        if document.project_id != project_id:
            raise HTTPException(status_code=403, detail="无权限访问此文档")
        
        # TODO: 实现评审逻辑
        return {
            "message": "需求评审功能开发中",
            "document_id": str(document_id),
            "status": "reviewing"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"开始评审失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))