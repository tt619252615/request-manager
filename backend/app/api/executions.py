"""
执行记录 API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models.execution import ExecutionRecord, ExecutionStatusEnum
from ..schemas.execution import ExecutionRecordResponse
from ..schemas.response import BaseResponse, success_response, error_response, ErrorCodes

# 创建路由器
router = APIRouter()


@router.get("/", response_model=BaseResponse[List[ExecutionRecordResponse]])
async def get_execution_records(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数"),
    task_id: Optional[int] = Query(None, description="任务ID过滤"),
    request_id: Optional[int] = Query(None, description="请求ID过滤"),
    status: Optional[ExecutionStatusEnum] = Query(None, description="执行状态过滤"),
    db: Session = Depends(get_db)
):
    """获取执行记录列表"""
    try:
        query = db.query(ExecutionRecord)
        
        # 应用过滤条件
        if task_id:
            query = query.filter(ExecutionRecord.task_id == task_id)
        if request_id:
            query = query.filter(ExecutionRecord.request_id == request_id)
        if status:
            query = query.filter(ExecutionRecord.status == status)
        
        # 按执行时间倒序排列
        query = query.order_by(ExecutionRecord.execution_time.desc())
        
        records = query.offset(skip).limit(limit).all()
        
        # 转换为Pydantic模型，避免序列化问题
        record_data = []
        for record in records:
            record_dict = {
                "id": record.id,
                "task_id": record.task_id,
                "request_id": record.request_id,
                "status": record.status,
                "request_url": record.request_url,
                "request_headers": record.request_headers,
                "request_body": record.request_body,
                "proxy_used": record.proxy_used,
                "response_code": record.response_code,
                "response_headers": record.response_headers,
                "response_body": record.response_body,
                "response_time": record.response_time,
                "error_message": record.error_message,
                "error_traceback": record.error_traceback,
                "thread_id": record.thread_id,
                "attempt_number": record.attempt_number,
                "execution_time": record.execution_time.isoformat() if record.execution_time else None,
                "created_at": record.created_at.isoformat() if record.created_at else None,
                "updated_at": record.updated_at.isoformat() if record.updated_at else None
            }
            record_data.append(record_dict)
        
        total = query.count()
        
        return success_response(
            data=record_data,
            message=f"获取执行记录成功，共 {total} 条记录"
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"获取执行记录失败: {str(e)}"
        )


@router.get("/{record_id}", response_model=BaseResponse[ExecutionRecordResponse])
async def get_execution_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取执行记录"""
    try:
        record = db.query(ExecutionRecord).filter(ExecutionRecord.id == record_id).first()
        
        if not record:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"执行记录 ID {record_id} 不存在"
            )
        
        # 转换为字典，避免序列化问题
        record_dict = {
            "id": record.id,
            "task_id": record.task_id,
            "request_id": record.request_id,
            "status": record.status,
            "request_url": record.request_url,
            "request_headers": record.request_headers,
            "request_body": record.request_body,
            "proxy_used": record.proxy_used,
            "response_code": record.response_code,
            "response_headers": record.response_headers,
            "response_body": record.response_body,
            "response_time": record.response_time,
            "error_message": record.error_message,
            "error_traceback": record.error_traceback,
            "thread_id": record.thread_id,
            "attempt_number": record.attempt_number,
            "execution_time": record.execution_time.isoformat() if record.execution_time else None,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None
        }
        
        return success_response(data=record_dict, message="获取执行记录详情成功")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"获取执行记录详情失败: {str(e)}"
        )


@router.delete("/{record_id}", response_model=BaseResponse[dict])
async def delete_execution_record(
    record_id: int,
    db: Session = Depends(get_db)
):
    """删除执行记录"""
    try:
        record = db.query(ExecutionRecord).filter(ExecutionRecord.id == record_id).first()
        
        if not record:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"执行记录 ID {record_id} 不存在"
            )
        
        db.delete(record)
        db.commit()
        
        return success_response(
            data={"deleted_id": record_id},
            message="执行记录删除成功"
        )
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"删除执行记录失败: {str(e)}"
        )


@router.get("/stats/summary", response_model=BaseResponse[dict])
async def get_execution_stats(
    task_id: Optional[int] = Query(None, description="任务ID过滤"),
    db: Session = Depends(get_db)
):
    """获取执行统计信息"""
    try:
        query = db.query(ExecutionRecord)
        
        if task_id:
            query = query.filter(ExecutionRecord.task_id == task_id)
        
        total = query.count()
        success_count = query.filter(ExecutionRecord.status == ExecutionStatusEnum.SUCCESS).count()
        failed_count = query.filter(ExecutionRecord.status == ExecutionStatusEnum.FAILED).count()
        timeout_count = query.filter(ExecutionRecord.status == ExecutionStatusEnum.TIMEOUT).count()
        
        # 计算成功率
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        # 计算平均响应时间
        avg_response_time_result = db.query(
            func.avg(ExecutionRecord.response_time)
        ).filter(
            ExecutionRecord.response_time.isnot(None)
        )
        
        if task_id:
            avg_response_time_result = avg_response_time_result.filter(ExecutionRecord.task_id == task_id)
        
        avg_response_time = avg_response_time_result.scalar() or 0
        
        stats = {
            "total_executions": total,
            "success_count": success_count,
            "failed_count": failed_count,
            "timeout_count": timeout_count,
            "success_rate": round(success_rate, 2),
            "average_response_time": round(avg_response_time, 2)
        }
        
        return success_response(data=stats, message="获取执行统计成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"获取执行统计失败: {str(e)}"
        ) 