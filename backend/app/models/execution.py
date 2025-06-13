"""
执行记录数据模型
"""

from sqlalchemy import Column, String, Text, Enum, Integer, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class ExecutionStatusEnum(str, enum.Enum):
    """执行状态枚举"""
    SUCCESS = "success"    # 成功
    FAILED = "failed"      # 失败
    TIMEOUT = "timeout"    # 超时
    ERROR = "error"        # 错误


class ExecutionRecord(BaseModel):
    """执行记录模型"""
    
    __tablename__ = "execution_records"
    
    # 关联信息
    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的任务ID"
    )
    task = relationship("Task", backref="execution_records")
    
    request_id = Column(
        Integer,
        ForeignKey("http_requests.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的请求ID"
    )
    request = relationship("HttpRequest", backref="execution_records")
    
    # 执行信息
    status = Column(
        Enum(ExecutionStatusEnum),
        nullable=False,
        comment="执行状态"
    )
    
    # 请求详情
    request_url = Column(Text, comment="实际请求URL")
    request_headers = Column(JSON, comment="实际请求头")
    request_body = Column(Text, comment="实际请求体")
    proxy_used = Column(String(255), comment="使用的代理")
    
    # 响应详情
    response_code = Column(Integer, comment="HTTP状态码")
    response_headers = Column(JSON, comment="响应头")
    response_body = Column(Text, comment="响应体")
    response_time = Column(Float, comment="响应时间（毫秒）")
    
    # 错误信息
    error_message = Column(Text, comment="错误消息")
    error_traceback = Column(Text, comment="错误堆栈")
    
    # 执行上下文
    thread_id = Column(String(50), comment="线程ID")
    attempt_number = Column(Integer, default=1, comment="尝试次数")
    execution_time = Column(DateTime, comment="执行时间")
    
    def __repr__(self) -> str:
        return f"<ExecutionRecord(id={self.id}, task_id={self.task_id}, status={self.status})>" 