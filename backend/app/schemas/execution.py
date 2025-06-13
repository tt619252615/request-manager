"""
执行记录相关的数据模式
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from ..models.execution import ExecutionStatusEnum


class ExecutionRecordBase(BaseModel):
    """执行记录基础模式"""
    task_id: int = Field(..., description="关联的任务ID")
    request_id: int = Field(..., description="关联的请求ID")
    status: ExecutionStatusEnum = Field(..., description="执行状态")
    
    # 请求详情
    request_url: Optional[str] = Field(None, description="实际请求URL")
    request_headers: Optional[Dict[str, Any]] = Field(None, description="实际请求头")
    request_body: Optional[str] = Field(None, description="实际请求体")
    proxy_used: Optional[str] = Field(None, description="使用的代理")
    
    # 响应详情
    response_code: Optional[int] = Field(None, description="HTTP状态码")
    response_headers: Optional[Dict[str, Any]] = Field(None, description="响应头")
    response_body: Optional[str] = Field(None, description="响应体")
    response_time: Optional[float] = Field(None, description="响应时间（毫秒）")
    
    # 错误信息
    error_message: Optional[str] = Field(None, description="错误消息")
    error_traceback: Optional[str] = Field(None, description="错误堆栈")
    
    # 执行上下文
    thread_id: Optional[str] = Field(None, description="线程ID")
    attempt_number: int = Field(default=1, description="尝试次数")
    execution_time: Optional[datetime] = Field(None, description="执行时间")


class ExecutionRecordCreate(ExecutionRecordBase):
    """创建执行记录的数据模式"""
    pass


class ExecutionRecordInDB(ExecutionRecordBase):
    """数据库中的执行记录模式"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ExecutionRecordResponse(ExecutionRecordInDB):
    """执行记录响应模式"""
    pass  # 移除关联对象，避免序列化问题


class ExecutionRecordWithRelations(ExecutionRecordInDB):
    """包含关联信息的执行记录响应模式"""
    # 如果需要关联的任务和请求信息，使用这个模式
    task: Optional[Dict[str, Any]] = None
    request: Optional[Dict[str, Any]] = None


class ExecutionStatsResponse(BaseModel):
    """执行统计响应模式"""
    total_executions: int = Field(..., description="总执行次数")
    successful_executions: int = Field(..., description="成功执行次数")
    failed_executions: int = Field(..., description="失败执行次数")
    success_rate: float = Field(..., description="成功率")
    average_response_time: Optional[float] = Field(None, description="平均响应时间（毫秒）")
    
    # 按时间段统计
    executions_by_hour: Dict[str, int] = Field(default_factory=dict, description="按小时统计")
    executions_by_day: Dict[str, int] = Field(default_factory=dict, description="按天统计")
    
    # 按状态统计
    executions_by_status: Dict[str, int] = Field(default_factory=dict, description="按状态统计")


class ExecutionQueryParams(BaseModel):
    """执行记录查询参数"""
    task_id: Optional[int] = Field(None, description="任务ID")
    request_id: Optional[int] = Field(None, description="请求ID")
    status: Optional[ExecutionStatusEnum] = Field(None, description="执行状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量") 