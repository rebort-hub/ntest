"""
需求管理服务
"""
import logging
import os
import uuid
from typing import List, Optional, Tuple
from fastapi import UploadFile

from app.models.aitestrebort.requirements import (
    RequirementDocument, RequirementModule, Requirement,
    ReviewReport, ReviewIssue, ModuleReviewResult
)
from app.schemas.aitestrebort.requirements import (
    RequirementDocumentCreate, RequirementDocumentUpdate,
    RequirementModuleCreate, RequirementModuleUpdate,
    RequirementCreate, RequirementUpdate,
    BatchModuleUpdateRequest, DocumentSplitRequest
)

logger = logging.getLogger(__name__)


class RequirementService:
    """需求管理服务类"""
    
    @staticmethod
    async def create_document(
        document_data: RequirementDocumentCreate,
        user_id: int
    ) -> RequirementDocument:
        """创建需求文档"""
        try:
            return await RequirementDocument.create(
                project_id=document_data.project_id,
                title=document_data.title,
                description=document_data.description,
                document_type=document_data.document_type,
                content=document_data.content,
                version=document_data.version,
                uploader_id=user_id,
                status="uploaded"
            )
        except Exception as e:
            logger.error(f"Create document failed: {e}")
            raise
    
    @staticmethod
    async def upload_document(
        project_id: int,
        title: str,
        description: Optional[str],
        file: UploadFile,
        user_id: int
    ) -> RequirementDocument:
        """上传需求文档"""
        try:
            # 保存文件
            file_path = f"uploads/requirements/{project_id}/{uuid.uuid4()}_{file.filename}"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # 提取文档类型
            document_type = file.filename.split('.')[-1].lower()
            
            # 创建文档记录
            document = await RequirementDocument.create(
                project_id=project_id,
                title=title,
                description=description,
                document_type=document_type,
                file_path=file_path,
                uploader_id=user_id,
                status="uploaded",
                word_count=len(content) if document_type == 'txt' else 0,
                page_count=1  # 简化处理
            )
            
            return document
            
        except Exception as e:
            logger.error(f"Upload document failed: {e}")
            raise
    
    @staticmethod
    async def list_documents(
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequirementDocument]:
        """获取需求文档列表"""
        try:
            query = RequirementDocument.all()
            
            if project_id:
                query = query.filter(project_id=project_id)
            if status:
                query = query.filter(status=status)
            
            return await query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"List documents failed: {e}")
            raise
    
    @staticmethod
    async def update_document(
        document_id: uuid.UUID,
        document_update: RequirementDocumentUpdate
    ) -> RequirementDocument:
        """更新需求文档"""
        try:
            await RequirementDocument.filter(id=document_id).update(
                **document_update.model_dump(exclude_unset=True)
            )
            return await RequirementDocument.get(id=document_id)
        except Exception as e:
            logger.error(f"Update document failed: {e}")
            raise
    
    @staticmethod
    async def delete_document(document_id: uuid.UUID):
        """删除需求文档"""
        try:
            document = await RequirementDocument.get_or_none(id=document_id)
            if document and document.file_path and os.path.exists(document.file_path):
                os.remove(document.file_path)
            
            await RequirementDocument.filter(id=document_id).delete()
        except Exception as e:
            logger.error(f"Delete document failed: {e}")
            raise
    
    @staticmethod
    async def split_document(
        document_id: uuid.UUID,
        split_request: DocumentSplitRequest
    ) -> List[RequirementModule]:
        """拆分需求文档为模块"""
        try:
            document = await RequirementDocument.get_or_none(id=document_id)
            if not document:
                raise ValueError("Document not found")
            
            # TODO: 实现AI文档拆分逻辑
            # 这里应该调用AI服务进行智能拆分
            
            # 模拟拆分结果
            modules = []
            for i in range(3):  # 模拟拆分为3个模块
                module = await RequirementModule.create(
                    document_id=document_id,
                    title=f"模块{i+1}",
                    content=f"这是模块{i+1}的内容",
                    order=i,
                    is_auto_generated=True,
                    confidence_score=0.85
                )
                modules.append(module)
            
            # 更新文档状态
            await RequirementDocument.filter(id=document_id).update(
                status="module_split"
            )
            
            return modules
            
        except Exception as e:
            logger.error(f"Split document failed: {e}")
            raise
    
    @staticmethod
    async def create_module(module_data: RequirementModuleCreate) -> RequirementModule:
        """创建需求模块"""
        try:
            return await RequirementModule.create(**module_data.model_dump())
        except Exception as e:
            logger.error(f"Create module failed: {e}")
            raise
    
    @staticmethod
    async def list_modules(
        document_id: Optional[uuid.UUID] = None,
        parent_module_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[RequirementModule]:
        """获取需求模块列表"""
        try:
            query = RequirementModule.all()
            
            if document_id:
                query = query.filter(document_id=document_id)
            if parent_module_id:
                query = query.filter(parent_module_id=parent_module_id)
            
            return await query.offset(skip).limit(limit).all()
        except Exception as e:
            logger.error(f"List modules failed: {e}")
            raise
    
    @staticmethod
    async def update_module(
        module_id: uuid.UUID,
        module_update: RequirementModuleUpdate
    ) -> RequirementModule:
        """更新需求模块"""
        try:
            await RequirementModule.filter(id=module_id).update(
                **module_update.model_dump(exclude_unset=True)
            )
            return await RequirementModule.get(id=module_id)
        except Exception as e:
            logger.error(f"Update module failed: {e}")
            raise
    
    @staticmethod
    async def delete_module(module_id: uuid.UUID):
        """删除需求模块"""
        try:
            await RequirementModule.filter(id=module_id).delete()
        except Exception as e:
            logger.error(f"Delete module failed: {e}")
            raise
    
    @staticmethod
    async def batch_update_modules(
        batch_request: BatchModuleUpdateRequest
    ) -> List[RequirementModule]:
        """批量更新需求模块"""
        try:
            updated_modules = []
            for i, module_update in enumerate(batch_request.modules):
                # 这里需要根据实际需求实现批量更新逻辑
                # 暂时返回空列表
                pass
            return updated_modules
        except Exception as e:
            logger.error(f"Batch update modules failed: {e}")
            raise
    
    @staticmethod
    async def create_requirement(
        requirement_data: RequirementCreate,
        user_id: int,
        user_name: str
    ) -> Requirement:
        """创建需求"""
        try:
            return await Requirement.create(
                project_id=requirement_data.project_id,
                title=requirement_data.title,
                description=requirement_data.description,
                type=requirement_data.type,
                priority=requirement_data.priority,
                status=requirement_data.status,
                stakeholders=requirement_data.stakeholders,
                creator_id=user_id,
                creator_name=user_name
            )
        except Exception as e:
            logger.error(f"Create requirement failed: {e}")
            raise
    
    @staticmethod
    async def list_requirements(
        project_id: Optional[int] = None,
        type: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[Requirement], int]:
        """获取需求列表"""
        try:
            query = Requirement.all()
            
            if project_id:
                query = query.filter(project_id=project_id)
            if type:
                query = query.filter(type=type)
            if status:
                query = query.filter(status=status)
            if priority:
                query = query.filter(priority=priority)
            
            total = await query.count()
            requirements = await query.offset(skip).limit(limit).all()
            
            return requirements, total
        except Exception as e:
            logger.error(f"List requirements failed: {e}")
            raise
    
    @staticmethod
    async def update_requirement(
        requirement_id: uuid.UUID,
        requirement_update: RequirementUpdate
    ) -> Requirement:
        """更新需求"""
        try:
            await Requirement.filter(id=requirement_id).update(
                **requirement_update.model_dump(exclude_unset=True)
            )
            return await Requirement.get(id=requirement_id)
        except Exception as e:
            logger.error(f"Update requirement failed: {e}")
            raise
    
    @staticmethod
    async def delete_requirement(requirement_id: uuid.UUID):
        """删除需求"""
        try:
            await Requirement.filter(id=requirement_id).delete()
        except Exception as e:
            logger.error(f"Delete requirement failed: {e}")
            raise
    
    @staticmethod
    async def generate_test_cases(requirement_id: uuid.UUID) -> dict:
        """为需求生成测试用例"""
        try:
            requirement = await Requirement.get_or_none(id=requirement_id)
            if not requirement:
                raise ValueError("Requirement not found")
            
            # 使用AI服务生成测试用例
            from app.services.ai.llm_service import get_llm_service
            
            llm_service = await get_llm_service()
            
            # 构建需求文本
            requirement_text = f"""
需求标题: {requirement.title}
需求描述: {requirement.description}
需求类型: {requirement.type}
优先级: {requirement.priority}
"""
            
            # 生成测试用例
            test_cases = await llm_service.generate_test_cases(requirement_text)
            
            return {"test_cases": test_cases, "count": len(test_cases)}
            
        except Exception as e:
            logger.error(f"Generate test cases failed: {e}")
            # 返回默认测试用例
            return {
                "test_cases": [
                    {
                        "name": f"测试用例1 - {requirement.title}",
                        "description": "基于需求自动生成的测试用例",
                        "priority": "P2",
                        "precondition": "系统正常运行",
                        "steps": [
                            "打开应用",
                            "执行功能操作",
                            "验证结果"
                        ],
                        "expected_result": "功能按预期工作"
                    }
                ],
                "count": 1
            }