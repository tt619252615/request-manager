"""
任务数据模型
"""

from sqlalchemy import Column, String, Text, Enum, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class TaskTypeEnum(str, enum.Enum):
    """任务类型枚举"""
    SINGLE = "single"        # 单次执行
    SCHEDULED = "scheduled"  # 定时任务
    RETRY = "retry"         # 循环重试


class TaskStatusEnum(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"      # 待运行
    RUNNING = "running"      # 运行中
    STOPPED = "stopped"      # 已停止
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败


class ScheduleTypeEnum(str, enum.Enum):
    """调度类型枚举"""
    IMMEDIATE = "immediate"  # 立即执行
    DATETIME = "datetime"    # 指定时间
    CRON = "cron"           # Cron表达式


class Task(BaseModel):
    """任务模型"""
    
    __tablename__ = "tasks"
    
    # 基本信息
    name = Column(String(255), nullable=False, comment="任务名称")
    description = Column(Text, comment="任务描述")
    
    # 关联请求
    request_id = Column(
        Integer, 
        ForeignKey("http_requests.id", ondelete="CASCADE"),
        nullable=False,
        comment="关联的HTTP请求ID"
    )
    request = relationship("HttpRequest", backref="tasks")
    
    # 任务配置
    task_type = Column(
        Enum(TaskTypeEnum),
        nullable=False,
        default=TaskTypeEnum.SINGLE,
        comment="任务类型"
    )
    status = Column(
        Enum(TaskStatusEnum),
        nullable=False,
        default=TaskStatusEnum.PENDING,
        comment="任务状态"
    )
    
    # 调度配置
    schedule_config = Column(JSON, default=dict, comment="调度配置")
    # 结构: {
    #   "type": "immediate|datetime|cron",
    #   "start_time": "2024-01-20 15:00:00",  # datetime类型时使用
    #   "cron_expression": "0 */5 * * *",    # cron类型时使用
    #   "timezone": "Asia/Shanghai"
    # }
    
    # 重试配置
    retry_config = Column(JSON, default=dict, comment="重试配置")
    # 结构: {
    #   "max_attempts": 10,
    #   "interval_seconds": 5,
    #   "success_condition": "response.status_code == 200",
    #   "stop_condition": "response.text.contains('success')"
    # }
    
    # 代理配置
    proxy_config = Column(JSON, default=dict, comment="代理配置")
    # 结构: {
    #   "enabled": true,
    #   "proxy_url": "http://proxy.example.com/api/get",
    #   "rotation": true,
    #   "timeout": 30
    # }
    
    # 执行配置
    thread_count = Column(Integer, default=1, comment="线程数")
    time_diff = Column(Integer, default=0, comment="时间差（秒）")
    
    # 执行统计
    execution_count = Column(Integer, default=0, comment="执行次数")
    success_count = Column(Integer, default=0, comment="成功次数")
    failure_count = Column(Integer, default=0, comment="失败次数")
    
    # 时间记录
    last_execution_at = Column(DateTime, comment="最后执行时间")
    next_execution_at = Column(DateTime, comment="下次执行时间")
    
    def __repr__(self) -> str:
        return f"<Task(id={self.id}, name='{self.name}', type={self.task_type}, status={self.status})>" 