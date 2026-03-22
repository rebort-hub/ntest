"""
aitestrebort 自动化脚本管理数据模式
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.base_form import PaginationForm


class aitestrebortAutomationScriptQueryForm(PaginationForm):
    """自动化脚本查询表单"""
    search: Optional[str] = Field(None, description="搜索关键词")
    test_case_id: Optional[int] = Field(None, description="测试用例ID")
    script_type: Optional[str] = Field(None, description="脚本类型")
    status: Optional[str] = Field(None, description="状态")
    source: Optional[str] = Field(None, description="来源")
    page: Optional[int] = Field(None, description="页码")  # 添加page字段
    
    def get_query_filter(self, *args, **kwargs):
        """查询条件"""
        filter_dict = {}
        if self.search:
            filter_dict["search"] = self.search
        if self.test_case_id:
            filter_dict["test_case_id"] = self.test_case_id
        if self.script_type:
            filter_dict["script_type"] = self.script_type
        if self.status:
            filter_dict["status"] = self.status
        if self.source:
            filter_dict["source"] = self.source
        return filter_dict


class aitestrebortAutomationScriptSchema(BaseModel):
    """自动化脚本模式"""
    id: Optional[int] = None
    name: str = Field(..., max_length=255, description="脚本名称")
    description: Optional[str] = Field(None, description="脚本描述")
    script_type: str = Field("playwright_python", description="脚本类型")
    script_content: str = Field(..., description="脚本代码")
    source: str = Field("manual", description="来源")
    status: str = Field("draft", description="状态")
    version: int = Field(1, description="版本号")
    test_case_id: Optional[int] = Field(None, description="关联测试用例ID")
    target_url: Optional[str] = Field(None, description="目标URL")
    timeout_seconds: int = Field(30, description="超时时间(秒)")
    headless: bool = Field(True, description="无头模式")
    created_by: Optional[int] = Field(None, description="创建人ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # 扩展信息
    test_case_name: Optional[str] = None
    latest_status: Optional[str] = None

    class Config:
        from_attributes = True


class aitestrebortAutomationScriptCreateSchema(BaseModel):
    """创建自动化脚本模式"""
    name: str = Field(..., max_length=255, description="脚本名称")
    description: Optional[str] = Field(None, description="脚本描述")
    script_type: str = Field("playwright_python", description="脚本类型")
    script_content: str = Field(..., description="脚本代码")
    source: Optional[str] = Field("manual", description="来源")
    test_case_id: Optional[int] = Field(None, description="关联测试用例ID")
    target_url: Optional[str] = Field(None, description="目标URL")
    timeout_seconds: Optional[int] = Field(30, description="超时时间(秒)")
    headless: Optional[bool] = Field(True, description="无头模式")


class aitestrebortAutomationScriptUpdateSchema(BaseModel):
    """更新自动化脚本模式"""
    name: Optional[str] = Field(None, max_length=255, description="脚本名称")
    description: Optional[str] = Field(None, description="脚本描述")
    script_type: Optional[str] = Field(None, description="脚本类型")
    script_content: Optional[str] = Field(None, description="脚本代码")
    source: Optional[str] = Field(None, description="来源")
    status: Optional[str] = Field(None, description="状态")
    target_url: Optional[str] = Field(None, description="目标URL")
    timeout_seconds: Optional[int] = Field(None, description="超时时间(秒)")
    headless: Optional[bool] = Field(None, description="无头模式")


class aitestrebortScriptExecutionSchema(BaseModel):
    """脚本执行记录模式"""
    id: Optional[int] = None
    script_id: int = Field(..., description="脚本ID")
    status: str = Field("pending", description="执行状态")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    output: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    screenshots: List[str] = Field(default_factory=list, description="截图列表")
    videos: List[str] = Field(default_factory=list, description="录屏列表")
    browser_type: str = Field("chromium", description="浏览器类型")
    viewport: Dict[str, Any] = Field(default_factory=dict, description="视口大小")
    executor_id: Optional[int] = Field(None, description="执行人ID")
    created_at: Optional[datetime] = None
    
    # 扩展信息
    executor_detail: Optional[Dict[str, Any]] = None
    duration: Optional[float] = None

    class Config:
        from_attributes = True


class aitestrebortScriptExecutionCreateSchema(BaseModel):
    """创建脚本执行记录模式"""
    browser_type: Optional[str] = Field("chromium", description="浏览器类型")
    viewport: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {"width": 1280, "height": 720}, 
        description="视口大小"
    )
    headless: Optional[bool] = Field(True, description="无头模式")
    record_video: Optional[bool] = Field(False, description="是否录制视频")


class aitestrebortAutomationScriptListSchema(BaseModel):
    """自动化脚本列表模式"""
    id: int
    name: str
    script_type: str
    source: str
    status: str
    version: int
    test_case_id: Optional[int] = None
    test_case_name: Optional[str] = None
    created_at: Optional[datetime] = None
    latest_status: Optional[str] = None

    class Config:
        from_attributes = True