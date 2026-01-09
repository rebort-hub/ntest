# -*- coding: utf-8 -*-
"""
AI代码生成记录模型
"""
from tortoise import fields
from app.models.base_model import BaseModel
from app.schemas.enums import DataStatusEnum


class AICodeGeneration(BaseModel):
    """AI代码生成记录表"""
    
    # 接口信息
    path = fields.CharField(max_length=500, description="接口路径")
    method = fields.CharField(max_length=10, description="请求方法")
    summary = fields.CharField(max_length=200, null=True, description="接口描述")
    
    # 请求参数（JSON格式存储）
    parameters = fields.JSONField(null=True, description="请求参数")
    request_body = fields.TextField(null=True, description="请求体")
    response_example = fields.TextField(null=True, description="响应示例")
    
    # 生成结果
    generated_code = fields.TextField(description="生成的代码")
    file_name = fields.CharField(max_length=200, description="文件名")
    language = fields.CharField(max_length=50, default="python", description="编程语言")
    framework = fields.CharField(max_length=50, default="pytest", description="测试框架")
    
    # 生成状态和统计
    status = fields.CharEnumField(DataStatusEnum, default=DataStatusEnum.ENABLE, description="记录状态")
    generation_time = fields.FloatField(null=True, description="生成耗时(秒)")
    code_lines = fields.IntField(null=True, description="代码行数")
    
    # 使用统计
    download_count = fields.IntField(default=0, description="下载次数")
    copy_count = fields.IntField(default=0, description="复制次数")
    last_used_time = fields.DatetimeField(null=True, description="最后使用时间")
    
    class Meta:
        table = "ai_code_generation"
        table_description = "AI代码生成记录表"
        ordering = ["-create_time"]
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.file_name}"