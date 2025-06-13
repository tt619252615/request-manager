"""
任务管理服务
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.task import Task, TaskTypeEnum, TaskStatusEnum, ScheduleTypeEnum
from ..models.request import HttpRequest
from ..schemas.task import TaskCreate, TaskUpdate
from ..config import settings


class TaskService:
    """任务管理服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_task(self, task_data: TaskCreate) -> Task:
        """创建任务"""
        # 验证关联的请求是否存在
        request = self.db.query(HttpRequest).filter(HttpRequest.id == task_data.request_id).first()
        if not request:
            raise ValueError(f"请求 ID {task_data.request_id} 不存在")
        
        # 转换数据格式
        task_dict = task_data.model_dump()
        
        # 处理嵌套的配置对象
        task_dict['schedule_config'] = task_data.schedule_config.model_dump()
        task_dict['retry_config'] = task_data.retry_config.model_dump()
        task_dict['proxy_config'] = task_data.proxy_config.model_dump()
        
        # 计算下次执行时间
        next_execution_at = self._calculate_next_execution(task_data.schedule_config)
        if next_execution_at:
            task_dict['next_execution_at'] = next_execution_at
        
        # 创建任务
        db_task = Task(**task_dict)
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        return self.db.query(Task).filter(Task.id == task_id).first()
    
    def get_tasks(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[TaskStatusEnum] = None,
        task_type: Optional[TaskTypeEnum] = None,
        request_id: Optional[int] = None
    ) -> List[Task]:
        """获取任务列表"""
        query = self.db.query(Task)
        
        # 搜索过滤
        if search:
            search_filter = or_(
                Task.name.ilike(f"%{search}%"),
                Task.description.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # 状态过滤
        if status:
            query = query.filter(Task.status == status)
        
        # 类型过滤
        if task_type:
            query = query.filter(Task.task_type == task_type)
        
        # 请求ID过滤
        if request_id:
            query = query.filter(Task.request_id == request_id)
        
        return query.offset(skip).limit(limit).all()
    
    def update_task(
        self, 
        task_id: int, 
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """更新任务"""
        db_task = self.get_task(task_id)
        if not db_task:
            return None
        
        # 只更新提供的字段
        update_data = task_data.model_dump(exclude_unset=True)
        
        # 处理嵌套对象
        if 'schedule_config' in update_data and update_data['schedule_config']:
            update_data['schedule_config'] = task_data.schedule_config.model_dump()
            # 重新计算下次执行时间
            next_execution_at = self._calculate_next_execution(task_data.schedule_config)
            if next_execution_at:
                update_data['next_execution_at'] = next_execution_at
        
        if 'retry_config' in update_data and update_data['retry_config']:
            update_data['retry_config'] = task_data.retry_config.model_dump()
        
        if 'proxy_config' in update_data and update_data['proxy_config']:
            update_data['proxy_config'] = task_data.proxy_config.model_dump()
        
        # 应用更新
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def delete_task(self, task_id: int) -> bool:
        """删除任务"""
        db_task = self.get_task(task_id)
        if not db_task:
            return False
        
        # 首先删除相关的执行记录，避免外键约束错误
        from ..models.execution import ExecutionRecord
        execution_records = self.db.query(ExecutionRecord).filter(ExecutionRecord.task_id == task_id).all()
        for record in execution_records:
            self.db.delete(record)
        
        # 然后删除任务
        self.db.delete(db_task)
        self.db.commit()
        return True
    
    def update_task_status(self, task_id: int, status: TaskStatusEnum) -> Optional[Task]:
        """更新任务状态"""
        db_task = self.get_task(task_id)
        if not db_task:
            return None
        
        db_task.status = status
        
        # 如果任务被停止，清除下次执行时间
        if status == TaskStatusEnum.STOPPED:
            db_task.next_execution_at = None
        elif status == TaskStatusEnum.RUNNING and db_task.task_type != TaskTypeEnum.SINGLE:
            # 如果任务重新启动，重新计算下次执行时间
            from ..schemas.task import ScheduleConfigSchema
            schedule_config = ScheduleConfigSchema(**db_task.schedule_config)
            next_execution_at = self._calculate_next_execution(schedule_config)
            if next_execution_at:
                db_task.next_execution_at = next_execution_at
        
        self.db.commit()
        self.db.refresh(db_task)
        return db_task
    
    def get_pending_tasks(self) -> List[Task]:
        """获取待执行的任务"""
        now = datetime.now()
        return self.db.query(Task).filter(
            and_(
                Task.status == TaskStatusEnum.PENDING,
                or_(
                    Task.next_execution_at.is_(None),  # 立即执行
                    Task.next_execution_at <= now      # 到时间执行
                )
            )
        ).all()
    
    def get_running_tasks(self) -> List[Task]:
        """获取运行中的任务"""
        return self.db.query(Task).filter(Task.status == TaskStatusEnum.RUNNING).all()
    
    def increment_execution_count(self, task_id: int, success: bool = True) -> None:
        """增加执行计数"""
        db_task = self.get_task(task_id)
        if not db_task:
            return
        
        db_task.execution_count += 1
        db_task.last_execution_at = datetime.now()
        
        if success:
            db_task.success_count += 1
        else:
            db_task.failure_count += 1
        
        # 对于单次任务，执行后设为完成
        if db_task.task_type == TaskTypeEnum.SINGLE:
            db_task.status = TaskStatusEnum.COMPLETED
            db_task.next_execution_at = None
        else:
            # 计算下次执行时间
            from ..schemas.task import ScheduleConfigSchema
            schedule_config = ScheduleConfigSchema(**db_task.schedule_config)
            next_execution_at = self._calculate_next_execution(schedule_config)
            db_task.next_execution_at = next_execution_at
        
        self.db.commit()
    
    def count_tasks(self, status: Optional[TaskStatusEnum] = None) -> int:
        """获取任务总数"""
        query = self.db.query(Task)
        if status:
            query = query.filter(Task.status == status)
        return query.count()
    
    def get_task_by_name(self, name: str) -> Optional[Task]:
        """根据名称获取任务"""
        return self.db.query(Task).filter(Task.name == name).first()
    
    def _calculate_next_execution(self, schedule_config) -> Optional[datetime]:
        """计算下次执行时间"""
        from ..schemas.task import ScheduleConfigSchema
        
        if isinstance(schedule_config, dict):
            config = ScheduleConfigSchema(**schedule_config)
        else:
            config = schedule_config
        
        if config.type == ScheduleTypeEnum.IMMEDIATE:
            return datetime.now()
        elif config.type == ScheduleTypeEnum.DATETIME:
            if config.start_time:
                try:
                    return datetime.fromisoformat(config.start_time.replace('Z', '+00:00'))
                except Exception:
                    return None
        elif config.type == ScheduleTypeEnum.CRON:
            # 这里需要实现cron表达式解析
            # 暂时简化处理，每5分钟执行一次
            return datetime.now() + timedelta(minutes=5)
        
        return None
    
    def duplicate_task(self, task_id: int, new_name: str) -> Optional[Task]:
        """复制任务"""
        original = self.get_task(task_id)
        if not original:
            return None
        
        # 创建副本
        from ..schemas.task import TaskCreate, ScheduleConfigSchema, RetryConfigSchema, ProxyConfigSchema
        
        task_data = TaskCreate(
            name=new_name,
            description=f"Copy of {original.name}",
            request_id=original.request_id,
            task_type=original.task_type,
            schedule_config=ScheduleConfigSchema(**original.schedule_config),
            retry_config=RetryConfigSchema(**original.retry_config),
            proxy_config=ProxyConfigSchema(**original.proxy_config),
            thread_count=original.thread_count,
            time_diff=original.time_diff
        )
        
        return self.create_task(task_data) 