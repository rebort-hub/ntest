"""
需求管理服务
"""
from typing import List, Optional, Dict, Any, Tuple
from fastapi import HTTPException, UploadFile
import uuid
import os
import logging
from datetime import datetime
from pathlib import Path
from tortoise.expressions import Q

from app.models.aitestrebort.requirements import (
    RequirementDocument, RequirementModule, Requirement,
    ReviewReport, ReviewIssue, ModuleReviewResult,
    RequirementType, RequirementPriority, RequirementStatus,
    DocumentStatus
)
from app.schemas.aitestrebort.requirements import (
    RequirementDocumentCreate, RequirementDocumentUpdate,
    RequirementCreate, RequirementUpdate,
    RequirementSearchRequest, RequirementStatistics,
    ProjectStatistics, DocumentSplitRequest
)

logger = logging.getLogger(__name__)


class RequirementService:
    """需求管理服务"""
    
    # ==================== 需求文档管理 ====================
    
    async def create_requirement_document(
        self,
        project_id: int,
        document_data: RequirementDocumentCreate,
        file: Optional[UploadFile] = None,
        user_id: Optional[int] = None
    ) -> RequirementDocument:
        """创建需求文档"""
        try:
            # 创建文档记录
            document_dict = {
                'project_id': project_id,
                'title': document_data.title,
                'description': document_data.description,
                'document_type': document_data.document_type,
                'uploader_id': user_id,
                'status': DocumentStatus.UPLOADED
            }
            
            # 处理文件上传
            if file:
                file_path = await self._save_uploaded_file(file, project_id)
                document_dict['file_path'] = file_path
                
                # 提取文档内容
                content = await self._extract_document_content(file_path)
                if content:
                    document_dict['content'] = content
                    document_dict['word_count'] = len(content)
                    document_dict['page_count'] = max(1, (len(content) // 500) + 1)
            
            document = await RequirementDocument.create(**document_dict)
            
            logger.info(f"需求文档创建成功: {document.id}")
            return document
            
        except Exception as e:
            logger.error(f"创建需求文档失败: {e}")
            raise HTTPException(status_code=500, detail=f"创建需求文档失败: {str(e)}")
    
    async def get_requirement_documents(
        self,
        project_id: int,
        search: Optional[str] = None,
        status: Optional[str] = None,  # 改为字符串类型
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[RequirementDocument], int]:
        """获取需求文档列表"""
        try:
            query = RequirementDocument.filter(project_id=project_id)
            
            # 搜索过滤
            if search:
                query = query.filter(
                    Q(title__icontains=search) |
                    Q(description__icontains=search) |
                    Q(content__icontains=search)
                )
            
            # 状态过滤
            if status:
                query = query.filter(status=status)
            
            # 总数
            total = await query.count()
            
            # 分页
            offset = (page - 1) * page_size
            documents = await query.order_by('-uploaded_at').offset(offset).limit(page_size)
            
            return documents, total
            
        except Exception as e:
            logger.error(f"获取需求文档列表失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取需求文档列表失败: {str(e)}")
    
    async def get_requirement_document(self, document_id: uuid.UUID) -> RequirementDocument:
        """获取需求文档详情"""
        document = await RequirementDocument.get_or_none(id=document_id)
        
        if not document:
            raise HTTPException(status_code=404, detail="需求文档不存在")
        
        return document
    
    async def update_requirement_document(
        self,
        document_id: uuid.UUID,
        update_data: RequirementDocumentUpdate
    ) -> RequirementDocument:
        """更新需求文档"""
        try:
            document = await self.get_requirement_document(document_id)
            
            # 更新字段
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict['updated_at'] = datetime.now()
            
            await document.update_from_dict(update_dict)
            await document.save()
            
            logger.info(f"需求文档更新成功: {document_id}")
            return document
            
        except Exception as e:
            logger.error(f"更新需求文档失败: {e}")
            raise HTTPException(status_code=500, detail=f"更新需求文档失败: {str(e)}")
    
    async def delete_requirement_document(self, document_id: uuid.UUID) -> bool:
        """删除需求文档"""
        try:
            document = await self.get_requirement_document(document_id)
            
            # 删除物理文件
            if document.file_path and os.path.exists(document.file_path):
                os.remove(document.file_path)
                logger.info(f"已删除文件: {document.file_path}")
            
            # 删除数据库记录（级联删除相关数据）
            await document.delete()
            
            logger.info(f"需求文档删除成功: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除需求文档失败: {e}")
            raise HTTPException(status_code=500, detail=f"删除需求文档失败: {str(e)}")
    
    # ==================== 手动需求管理 ====================
    
    async def create_requirement(
        self,
        project_id: int,
        requirement_data: RequirementCreate,
        user_id: Optional[int] = None,
        user_name: Optional[str] = None
    ) -> Requirement:
        """创建需求"""
        try:
            requirement_dict = {
                'project_id': project_id,
                'title': requirement_data.title,
                'description': requirement_data.description,
                'type': requirement_data.type,
                'priority': requirement_data.priority,
                'status': requirement_data.status,
                'stakeholders': requirement_data.stakeholders,
                'creator_id': user_id,
                'creator_name': user_name or "未知用户"
            }
            
            requirement = await Requirement.create(**requirement_dict)
            
            logger.info(f"需求创建成功: {requirement.id}")
            return requirement
            
        except Exception as e:
            logger.error(f"创建需求失败: {e}")
            raise HTTPException(status_code=500, detail=f"创建需求失败: {str(e)}")
    
    async def get_documents_from_filesystem(
        self,
        project_id: int,
        search: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[RequirementDocument], int]:
        """从文件系统获取需求文档列表"""
        try:
            import os
            from pathlib import Path
            
            # 构建项目文档目录路径
            upload_dir = f"uploads/requirements/{project_id}"
            
            if not os.path.exists(upload_dir):
                logger.info(f"项目 {project_id} 的文档目录不存在: {upload_dir}")
                return [], 0
            
            # 扫描目录中的文件
            documents = []
            for filename in os.listdir(upload_dir):
                file_path = os.path.join(upload_dir, filename)
                
                # 跳过目录
                if os.path.isdir(file_path):
                    continue
                
                # 获取文件信息
                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                created_time = datetime.fromtimestamp(file_stat.st_ctime)
                modified_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                # 提取文件名（去掉UUID前缀）
                display_name = filename
                if '_' in filename:
                    # 如果文件名包含UUID前缀，提取原始文件名
                    parts = filename.split('_', 1)
                    if len(parts) > 1:
                        display_name = parts[1]
                
                # 确定文档类型
                file_ext = Path(filename).suffix.lower()
                document_type = "unknown"
                if file_ext in ['.docx', '.doc']:
                    document_type = "word"
                elif file_ext in ['.pdf']:
                    document_type = "pdf"
                elif file_ext in ['.txt']:
                    document_type = "text"
                elif file_ext in ['.md']:
                    document_type = "markdown"
                
                # 搜索过滤
                if search and search.lower() not in display_name.lower():
                    continue
                
                # 创建文档对象（模拟数据库对象）
                doc_data = {
                    'id': str(uuid.uuid4()),  # 生成临时ID
                    'project_id': project_id,
                    'title': display_name,
                    'description': f"文件大小: {file_size} 字节",
                    'document_type': document_type,
                    'file_path': file_path,
                    'content': None,  # 暂不读取内容
                    'status': 'uploaded',
                    'version': '1.0',
                    'is_latest': True,
                    'parent_document': None,
                    'uploader_id': None,
                    'uploaded_at': created_time,
                    'updated_at': modified_time,
                    'word_count': 0,
                    'page_count': 1
                }
                
                # 创建临时文档对象，使用与RequirementDocument相同的结构
                class TempDocument:
                    def __init__(self, **kwargs):
                        for key, value in kwargs.items():
                            setattr(self, key, value)
                    
                    @property
                    def __dict__(self):
                        return {key: getattr(self, key) for key in [
                            'id', 'project_id', 'title', 'description', 'document_type',
                            'file_path', 'content', 'status', 'version', 'is_latest',
                            'parent_document', 'uploader_id', 'uploaded_at', 'updated_at',
                            'word_count', 'page_count'
                        ]}
                
                document = TempDocument(**doc_data)
                documents.append(document)
            
            # 按修改时间排序
            documents.sort(key=lambda x: x.updated_at, reverse=True)
            
            # 分页
            total = len(documents)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_docs = documents[start_idx:end_idx]
            
            logger.info(f"从文件系统找到 {total} 个文档，返回第 {page} 页的 {len(paginated_docs)} 个文档")
            return paginated_docs, total
            
        except Exception as e:
            logger.error(f"从文件系统获取需求文档失败: {e}")
            return [], 0

    async def get_requirements(
        self,
        project_id: int,
        search_params: RequirementSearchRequest
    ) -> Tuple[List[Requirement], int]:
        """获取需求列表"""
        try:
            query = Requirement.filter(project_id=project_id)
            
            # 搜索过滤
            if search_params.keyword:
                query = query.filter(
                    Q(title__icontains=search_params.keyword) | 
                    Q(description__icontains=search_params.keyword)
                )
            
            # 类型过滤
            if search_params.type:
                query = query.filter(type=search_params.type)
            
            # 优先级过滤
            if search_params.priority:
                query = query.filter(priority=search_params.priority)
            
            # 状态过滤
            if search_params.status:
                query = query.filter(status=search_params.status)
            
            # 总数
            total = await query.count()
            
            # 分页
            offset = (search_params.page - 1) * search_params.page_size
            requirements = await query.order_by('-created_at').offset(offset).limit(search_params.page_size)
            
            return requirements, total
            
        except Exception as e:
            logger.error(f"获取需求列表失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取需求列表失败: {str(e)}")
    
    async def get_requirement(self, requirement_id: uuid.UUID) -> Requirement:
        """获取需求详情"""
        requirement = await Requirement.get_or_none(id=requirement_id)
        
        if not requirement:
            raise HTTPException(status_code=404, detail="需求不存在")
        
        return requirement
    
    async def update_requirement(
        self,
        requirement_id: uuid.UUID,
        update_data: RequirementUpdate
    ) -> Requirement:
        """更新需求"""
        try:
            requirement = await self.get_requirement(requirement_id)
            
            # 更新字段
            update_dict = update_data.model_dump(exclude_unset=True)
            update_dict['updated_at'] = datetime.now()
            
            await requirement.update_from_dict(update_dict)
            await requirement.save()
            
            logger.info(f"需求更新成功: {requirement_id}")
            return requirement
            
        except Exception as e:
            logger.error(f"更新需求失败: {e}")
            raise HTTPException(status_code=500, detail=f"更新需求失败: {str(e)}")
    
    async def delete_requirement(self, requirement_id: uuid.UUID) -> bool:
        """删除需求"""
        try:
            requirement = await self.get_requirement(requirement_id)
            
            await requirement.delete()
            
            logger.info(f"需求删除成功: {requirement_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除需求失败: {e}")
            raise HTTPException(status_code=500, detail=f"删除需求失败: {str(e)}")
    
    # ==================== 统计功能 ====================
    
    async def get_requirement_statistics(self, project_id: int) -> RequirementStatistics:
        """获取需求统计信息"""
        try:
            # 基础统计
            total_requirements = await Requirement.filter(project_id=project_id).count()
            total_documents = await RequirementDocument.filter(project_id=project_id).count()
            
            # 需求类型分布
            type_distribution = {}
            for req_type in RequirementType:
                count = await Requirement.filter(project_id=project_id, type=req_type.value).count()
                if count > 0:
                    type_distribution[req_type.value] = count
            
            # 需求优先级分布
            priority_distribution = {}
            for priority in RequirementPriority:
                count = await Requirement.filter(project_id=project_id, priority=priority.value).count()
                if count > 0:
                    priority_distribution[priority.value] = count
            
            # 需求状态分布
            status_distribution = {}
            for status in RequirementStatus:
                count = await Requirement.filter(project_id=project_id, status=status.value).count()
                if count > 0:
                    status_distribution[status.value] = count
            
            # 文档状态分布
            doc_status_distribution = {}
            for status in DocumentStatus:
                count = await RequirementDocument.filter(project_id=project_id, status=status.value).count()
                if count > 0:
                    doc_status_distribution[status.value] = count
            
            # 模块和评审统计
            total_modules = await RequirementModule.filter(document__project_id=project_id).count()
            total_reviews = await ReviewReport.filter(document__project_id=project_id).count()
            
            # 评审统计
            review_statistics = {
                "total_reviews": total_reviews,
                "completed_reviews": await ReviewReport.filter(
                    document__project_id=project_id,
                    status="completed"
                ).count(),
                "average_completion_score": 0,
                "average_clarity_score": 0
            }
            
            return RequirementStatistics(
                total_requirements=total_requirements,
                total_documents=total_documents,
                total_modules=total_modules,
                total_reviews=total_reviews,
                requirement_type_distribution=type_distribution,
                requirement_priority_distribution=priority_distribution,
                requirement_status_distribution=status_distribution,
                document_status_distribution=doc_status_distribution,
                review_statistics=review_statistics
            )
            
        except Exception as e:
            logger.error(f"获取需求统计失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取需求统计失败: {str(e)}")
    
    async def get_project_statistics(self, project_id: int) -> ProjectStatistics:
        """获取项目统计信息（包含知识库统计）"""
        try:
            # 获取需求统计
            req_stats = await self.get_requirement_statistics(project_id)
            
            # 获取真实的知识库统计数据
            from app.models.aitestrebort.knowledge import (
                aitestrebortKnowledgeBase, aitestrebortDocument, aitestrebortDocumentChunk
            )
            
            # 知识库统计
            total_knowledge_bases = await aitestrebortKnowledgeBase.filter(project_id=project_id).count()
            active_knowledge_bases = await aitestrebortKnowledgeBase.filter(
                project_id=project_id, is_active=True
            ).count()
            inactive_knowledge_bases = total_knowledge_bases - active_knowledge_bases
            
            # 文档统计
            kb_documents = await aitestrebortDocument.filter(
                knowledge_base__project_id=project_id
            ).count()
            processed_documents = await aitestrebortDocument.filter(
                knowledge_base__project_id=project_id,
                status='completed'
            ).count()
            processing_documents = await aitestrebortDocument.filter(
                knowledge_base__project_id=project_id,
                status='processing'
            ).count()
            failed_documents = await aitestrebortDocument.filter(
                knowledge_base__project_id=project_id,
                status='failed'
            ).count()
            
            # 分块统计
            total_chunks = await aitestrebortDocumentChunk.filter(
                document__knowledge_base__project_id=project_id
            ).count()
            
            # 总文档数（需求文档 + 知识库文档）
            total_documents = req_stats.total_documents + kb_documents
            
            # 系统健康状态检查
            system_status = "healthy"
            database_status = "connected"
            vector_db_status = "connected"
            
            # 如果有失败的文档，系统状态为警告
            if failed_documents > 0:
                system_status = "warning"
            
            return ProjectStatistics(
                total_knowledge_bases=total_knowledge_bases,
                active_knowledge_bases=active_knowledge_bases,
                inactive_knowledge_bases=inactive_knowledge_bases,
                total_documents=total_documents,
                processed_documents=processed_documents,
                processing_documents=processing_documents,
                failed_documents=failed_documents,
                total_requirements=req_stats.total_requirements,
                requirement_type_distribution=req_stats.requirement_type_distribution,
                requirement_priority_distribution=req_stats.requirement_priority_distribution,
                total_chunks=total_chunks,
                system_status=system_status,
                database_status=database_status,
                vector_db_status=vector_db_status,
                last_updated=datetime.now().isoformat()
            )
            
        except Exception as e:
            logger.error(f"获取项目统计失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取项目统计失败: {str(e)}")

    # ==================== 评审管理 ====================
    
    async def start_document_review(
        self,
        document_id: uuid.UUID,
        review_type: str = "comprehensive",
        focus_areas: Optional[List[str]] = None,
        user_id: Optional[int] = None
    ) -> ReviewReport:
        """开始文档评审"""
        try:
            # 检查文档是否存在
            document = await RequirementDocument.get(id=document_id)
            
            # 创建评审报告
            review_data = {
                'document_id': document_id,
                'review_type': review_type,
                'status': 'pending',
                'reviewer': f"用户{user_id}" if user_id else "AI需求评审助手"
            }
            
            review_report = await ReviewReport.create(**review_data)
            
            # TODO: 启动实际的评审流程
            # 这里应该调用AI评审服务
            
            logger.info(f"评审开始: {review_report.id}")
            return review_report
            
        except Exception as e:
            logger.error(f"开始文档评审失败: {e}")
            raise HTTPException(status_code=500, detail=f"开始文档评审失败: {str(e)}")
    
    async def get_review_results(
        self,
        project_id: int,
        document_id: Optional[uuid.UUID] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ReviewReport], int]:
        """获取评审结果列表"""
        try:
            query = ReviewReport.filter(document__project_id=project_id)
            
            if document_id:
                query = query.filter(document_id=document_id)
            
            if status:
                query = query.filter(status=status)
            
            # 总数
            total = await query.count()
            
            # 分页
            offset = (page - 1) * page_size
            reviews = await query.order_by('-review_date').offset(offset).limit(page_size)
            
            return reviews, total
            
        except Exception as e:
            logger.error(f"获取评审结果失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取评审结果失败: {str(e)}")
    
    async def get_review_detail(self, review_id: uuid.UUID) -> ReviewReport:
        """获取评审详情"""
        try:
            review = await ReviewReport.get(id=review_id)
            return review
            
        except Exception as e:
            logger.error(f"获取评审详情失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取评审详情失败: {str(e)}")
    
    async def get_review_progress(self, review_id: uuid.UUID) -> dict:
        """获取评审进度"""
        try:
            review = await ReviewReport.get(id=review_id)
            
            # 计算进度
            progress = 0.0
            current_step = "准备中"
            estimated_time = None
            
            if review.status == "pending":
                progress = 10.0
                current_step = "等待开始"
            elif review.status == "processing":
                progress = 50.0
                current_step = "评审中"
                estimated_time = 300  # 5分钟
            elif review.status == "completed":
                progress = 100.0
                current_step = "已完成"
            elif review.status == "failed":
                progress = 0.0
                current_step = "评审失败"
            
            return {
                "document_id": str(review.document_id),
                "status": review.status,
                "progress": progress,
                "current_step": current_step,
                "estimated_time": estimated_time
            }
            
        except Exception as e:
            logger.error(f"获取评审进度失败: {e}")
            raise HTTPException(status_code=500, detail=f"获取评审进度失败: {str(e)}")
    
    # ==================== 辅助方法 ====================
    
    async def _save_uploaded_file(self, file: UploadFile, project_id: int) -> str:
        """保存上传的文件"""
        try:
            # 创建目录
            upload_dir = f"uploads/requirements/{project_id}"
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成文件名
            file_extension = os.path.splitext(file.filename)[1]
            file_name = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, file_name)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            logger.info(f"文件保存成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"保存文件失败: {e}")
            raise HTTPException(status_code=500, detail=f"保存文件失败: {str(e)}")
    
    async def _extract_document_content(self, file_path: str) -> Optional[str]:
        """提取文档内容"""
        try:
            # 这里应该根据文件类型使用不同的提取方法
            # 暂时返回模拟内容
            return f"从文件 {file_path} 提取的内容"
            
        except Exception as e:
            logger.error(f"提取文档内容失败: {e}")
            return None
    
    async def generate_test_cases(self, requirement_id: uuid.UUID) -> Dict[str, Any]:
        """生成测试用例"""
        try:
            requirement = await self.get_requirement(requirement_id)
            
            # 这里应该集成AI生成测试用例的逻辑
            # 暂时返回模拟数据
            test_cases = [
                {
                    "title": f"测试用例1 - {requirement.title}",
                    "description": "基于需求自动生成的测试用例",
                    "steps": [
                        "步骤1: 准备测试数据",
                        "步骤2: 执行功能操作",
                        "步骤3: 验证结果"
                    ],
                    "expected_result": "功能正常工作"
                }
            ]
            
            return {
                "requirement_id": str(requirement_id),
                "requirement_title": requirement.title,
                "test_cases": test_cases,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"生成测试用例失败: {e}")
            raise HTTPException(status_code=500, detail=f"生成测试用例失败: {str(e)}")