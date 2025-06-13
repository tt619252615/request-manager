"""
任务相关的数据模式
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from ..models.task import TaskTypeEnum, TaskStatusEnum, ScheduleTypeEnum


class ScheduleConfigSchema(BaseModel):
    """调度配置模式"""
    type: ScheduleTypeEnum = Field(..., description="调度类型")
    start_time: Optional[str] = Field(None, description="开始时间")
    cron_expression: Optional[str] = Field(None, description="Cron表达式")
    timezone: str = Field(default="Asia/Shanghai", description="时区")


class RetryConfigSchema(BaseModel):
    """重试配置模式"""
    max_attempts: int = Field(default=10, ge=1, le=1000, description="最大尝试次数")
    interval_seconds: int = Field(default=5, ge=0, le=3600, description="重试间隔（秒）")
    success_condition: Optional[str] = Field(None, description="成功条件表达式")
    stop_condition: Optional[str] = Field(None, description="停止条件表达式")
    key_message: Optional[str] = Field(None, description="关键消息")


class ProxyConfigSchema(BaseModel):
    """代理配置模式"""
    enabled: bool = Field(default=False, description="是否启用代理")
    proxy_url: Optional[str] = Field(None, description="代理获取URL")
    rotation: bool = Field(default=True, description="是否轮换代理")
    timeout: int = Field(default=30, ge=1, le=300, description="超时时间（秒）")


class TaskBase(BaseModel):
    """任务基础模式"""
    name: str = Field(..., min_length=1, max_length=255, description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    request_id: int = Field(..., description="关联的请求ID")
    task_type: TaskTypeEnum = Field(default=TaskTypeEnum.SINGLE, description="任务类型")
    schedule_config: ScheduleConfigSchema = Field(..., description="调度配置")
    retry_config: RetryConfigSchema = Field(default_factory=RetryConfigSchema, description="重试配置")
    proxy_config: ProxyConfigSchema = Field(default_factory=ProxyConfigSchema, description="代理配置")
    thread_count: int = Field(default=1, ge=1, le=50, description="线程数")
    time_diff: int = Field(default=0, description="时间差（秒）")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TaskCreate(TaskBase):
    """创建任务的数据模式"""
    pass


class TaskUpdate(BaseModel):
    """更新任务的数据模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    request_id: Optional[int] = Field(None, description="关联的请求ID")
    task_type: Optional[TaskTypeEnum] = Field(None, description="任务类型")
    schedule_config: Optional[ScheduleConfigSchema] = Field(None, description="调度配置")
    retry_config: Optional[RetryConfigSchema] = Field(None, description="重试配置")
    proxy_config: Optional[ProxyConfigSchema] = Field(None, description="代理配置")
    thread_count: Optional[int] = Field(None, ge=1, le=50, description="线程数")
    time_diff: Optional[int] = Field(None, description="时间差（秒）")


class TaskInDB(TaskBase):
    """数据库中的任务模式"""
    id: int
    status: TaskStatusEnum
    execution_count: int
    success_count: int
    failure_count: int
    last_execution_at: Optional[datetime]
    next_execution_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(TaskInDB):
    """任务响应模式"""
    pass  # 暂时移除request字段避免序列化问题

    class Config:
        from_attributes = True


class TaskActionRequest(BaseModel):
    """任务操作请求模式"""
    action: str = Field(..., description="操作类型: start, stop, restart")


class TaskStatusUpdate(BaseModel):
    """任务状态更新模式"""
    status: TaskStatusEnum = Field(..., description="新状态") 