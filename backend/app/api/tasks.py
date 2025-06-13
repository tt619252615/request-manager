"""
任务管理 API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.task import Task, TaskStatusEnum, TaskTypeEnum
from ..schemas.task import (
    TaskCreate, 
    TaskUpdate, 
    TaskResponse,
    TaskStatusUpdate
)
from ..schemas.response import BaseResponse, success_response, error_response, ErrorCodes
from ..services.task_service import TaskService
from ..services.scheduler_service import scheduler_service

# 创建路由器
router = APIRouter()


@router.post("/", response_model=BaseResponse[TaskResponse])
async def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db)
):
    """创建任务"""
    try:
        service = TaskService(db)
        
        # 检查名称是否已存在
        existing = service.get_task_by_name(task_data.name)
        if existing:
            return error_response(
                code=ErrorCodes.PARAMETER_ERROR,
                message=f"任务名称 '{task_data.name}' 已存在"
            )
        
        result = service.create_task(task_data)
        
        # 将SQLAlchemy对象转换为Pydantic模型
        task_response = TaskResponse.from_orm(result)
        
        return success_response(data=task_response, message="任务创建成功")
        
    except ValueError as e:
        return error_response(
            code=ErrorCodes.PARAMETER_ERROR,
            message=str(e)
        )
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"创建任务失败: {str(e)}"
        )


@router.get("/", response_model=BaseResponse[List[TaskResponse]])
async def get_tasks(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    status: Optional[TaskStatusEnum] = Query(None, description="任务状态过滤"),
    task_type: Optional[TaskTypeEnum] = Query(None, description="任务类型过滤"),
    request_id: Optional[int] = Query(None, description="请求ID过滤"),
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    try:
        service = TaskService(db)
        
        tasks = service.get_tasks(
            skip=skip,
            limit=limit,
            search=search,
            status=status,
            task_type=task_type,
            request_id=request_id
        )
        
        # 将SQLAlchemy对象列表转换为Pydantic模型列表
        task_responses = [TaskResponse.from_orm(task) for task in tasks]
        
        total = service.count_tasks()
        
        return success_response(
            data=task_responses,
            message=f"获取任务列表成功，共 {total} 条记录"
        )
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"获取任务列表失败: {str(e)}"
        )


@router.get("/{task_id}", response_model=BaseResponse[TaskResponse])
async def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取任务"""
    try:
        service = TaskService(db)
        task = service.get_task(task_id)
        
        if not task:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"任务 ID {task_id} 不存在"
            )
        
        task_response = TaskResponse.from_orm(task)
        return success_response(data=task_response, message="获取任务详情成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"获取任务详情失败: {str(e)}"
        )


@router.put("/{task_id}", response_model=BaseResponse[TaskResponse])
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db)
):
    """更新任务"""
    try:
        service = TaskService(db)
        
        # 检查任务是否存在
        existing = service.get_task(task_id)
        if not existing:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"任务 ID {task_id} 不存在"
            )
        
        # 检查名称冲突
        if task_data.name and task_data.name != existing.name:
            name_conflict = service.get_task_by_name(task_data.name)
            if name_conflict:
                return error_response(
                    code=ErrorCodes.PARAMETER_ERROR,
                    message=f"任务名称 '{task_data.name}' 已存在"
                )
        
        result = service.update_task(task_id, task_data)
        task_response = TaskResponse.from_orm(result)
        return success_response(data=task_response, message="任务更新成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"更新任务失败: {str(e)}"
        )


@router.delete("/{task_id}", response_model=BaseResponse[dict])
async def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """删除任务"""
    try:
        service = TaskService(db)
        
        # 检查任务是否存在
        existing = service.get_task(task_id)
        if not existing:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"任务 ID {task_id} 不存在"
            )
        
        # 如果任务正在运行，先停止任务
        if existing.status == TaskStatusEnum.RUNNING:
            scheduler_service.stop_task(task_id)
        
        success = service.delete_task(task_id)
        if success:
            return success_response(
                data={"deleted_id": task_id},
                message="任务删除成功"
            )
        else:
            return error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message="删除任务失败"
            )
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"删除任务失败: {str(e)}"
        )


@router.post("/{task_id}/status", response_model=BaseResponse[TaskResponse])
async def update_task_status(
    task_id: int,
    status_data: TaskStatusUpdate,
    db: Session = Depends(get_db)
):
    """更新任务状态"""
    try:
        service = TaskService(db)
        
        # 检查任务是否存在
        existing = service.get_task(task_id)
        if not existing:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"任务 ID {task_id} 不存在"
            )
        
        # 处理状态变更
        if status_data.status == TaskStatusEnum.RUNNING:
            # 启动任务 - 这里需要触发调度器
            result = service.update_task_status(task_id, status_data.status)
        elif status_data.status == TaskStatusEnum.STOPPED:
            # 停止任务
            scheduler_service.stop_task(task_id)
            result = service.update_task_status(task_id, status_data.status)
        else:
            # 其他状态变更
            result = service.update_task_status(task_id, status_data.status)
        
        if result:
            task_response = TaskResponse.from_orm(result)
            return success_response(data=task_response, message="任务状态更新成功")
        else:
            return error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message="更新任务状态失败"
            )
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"更新任务状态失败: {str(e)}"
        )


@router.post("/{task_id}/start", response_model=BaseResponse[TaskResponse])
async def start_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """启动任务"""
    try:
        service = TaskService(db)
        
        # 检查任务是否存在
        task = service.get_task(task_id)
        if not task:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"任务 ID {task_id} 不存在"
            )
        
        # 检查任务状态
        if task.status == TaskStatusEnum.RUNNING:
            return error_response(
                code=ErrorCodes.PARAMETER_ERROR,
                message="任务已在运行中"
            )
        
        # 更新任务状态为待执行
        result = service.update_task_status(task_id, TaskStatusEnum.PENDING)
        
        task_response = TaskResponse.from_orm(result)
        return success_response(data=task_response, message="任务已加入执行队列")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"启动任务失败: {str(e)}"
        )


@router.post("/{task_id}/stop", response_model=BaseResponse[TaskResponse])
async def stop_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    """停止任务"""
    try:
        service = TaskService(db)
        
        # 检查任务是否存在
        task = service.get_task(task_id)
        if not task:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"任务 ID {task_id} 不存在"
            )
        
        # 停止运行中的任务
        if task.status == TaskStatusEnum.RUNNING:
            success = scheduler_service.stop_task(task_id)
            if not success:
                return error_response(
                    code=ErrorCodes.INTERNAL_ERROR,
                    message="停止任务失败"
                )
        
        # 更新任务状态
        result = service.update_task_status(task_id, TaskStatusEnum.STOPPED)
        
        task_response = TaskResponse.from_orm(result)
        return success_response(data=task_response, message="任务已停止")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"停止任务失败: {str(e)}"
        )


@router.post("/{task_id}/duplicate", response_model=BaseResponse[TaskResponse])
async def duplicate_task(
    task_id: int,
    new_name: str = Query(..., description="新任务名称"),
    db: Session = Depends(get_db)
):
    """复制任务"""
    try:
        service = TaskService(db)
        
        # 检查原任务是否存在
        original = service.get_task(task_id)
        if not original:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"任务 ID {task_id} 不存在"
            )
        
        # 检查新名称是否已存在
        existing = service.get_task_by_name(new_name)
        if existing:
            return error_response(
                code=ErrorCodes.PARAMETER_ERROR,
                message=f"任务名称 '{new_name}' 已存在"
            )
        
        result = service.duplicate_task(task_id, new_name)
        task_response = TaskResponse.from_orm(result)
        return success_response(data=task_response, message="任务复制成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"复制任务失败: {str(e)}"
        )


@router.get("/stats/summary", response_model=BaseResponse[dict])
async def get_task_stats(
    db: Session = Depends(get_db)
):
    """获取任务统计信息"""
    try:
        service = TaskService(db)
        
        stats = {
            "total": service.count_tasks(),
            "running": service.count_tasks(TaskStatusEnum.RUNNING),
            "pending": service.count_tasks(TaskStatusEnum.PENDING),
            "completed": service.count_tasks(TaskStatusEnum.COMPLETED),
            "failed": service.count_tasks(TaskStatusEnum.FAILED),
            "stopped": service.count_tasks(TaskStatusEnum.STOPPED),
            "scheduler_running_count": scheduler_service.get_running_task_count()
        }
        
        return success_response(data=stats, message="获取任务统计成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"获取任务统计失败: {str(e)}"
        ) 