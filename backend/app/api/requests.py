"""
HTTP 请求管理 API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.request import HttpRequest
from ..schemas.request import (
    HttpRequestCreate, 
    HttpRequestUpdate, 
    HttpRequestResponse,
    FiddlerImportData,
    CurlImportData,
    RequestTestData,
    RequestTestResult
)
from ..schemas.response import BaseResponse, success_response, error_response, ErrorCodes
from ..services.request_service import RequestService
from ..services.executor_service import ExecutorService

# 创建路由器
router = APIRouter()


@router.post("/", response_model=BaseResponse[HttpRequestResponse])
async def create_request(
    request_data: HttpRequestCreate,
    db: Session = Depends(get_db)
):
    """创建HTTP请求"""
    try:
        service = RequestService(db)
        
        # 检查名称是否已存在
        existing = service.get_request_by_name(request_data.name)
        if existing:
            return error_response(
                code=ErrorCodes.PARAMETER_ERROR,
                message=f"请求名称 '{request_data.name}' 已存在"
            )
        
        result = service.create_request(request_data)
        return success_response(data=result, message="请求创建成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"创建请求失败: {str(e)}"
        )


@router.get("/", response_model=BaseResponse[List[HttpRequestResponse]])
async def get_requests(
    skip: int = Query(0, ge=0, description="跳过条数"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    method: Optional[str] = Query(None, description="HTTP方法过滤"),
    tags: Optional[List[str]] = Query(None, description="标签过滤"),
    db: Session = Depends(get_db)
):
    """获取HTTP请求列表"""
    try:
        service = RequestService(db)
        
        requests = service.get_requests(
            skip=skip,
            limit=limit,
            search=search,
            method=method,
            tags=tags
        )
        
        total = service.count_requests()
        
        return success_response(
            data=requests,
            message=f"获取请求列表成功，共 {total} 条记录"
        )
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"获取请求列表失败: {str(e)}"
        )


@router.get("/{request_id}", response_model=BaseResponse[HttpRequestResponse])
async def get_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """根据ID获取HTTP请求"""
    try:
        service = RequestService(db)
        request = service.get_request(request_id)
        
        if not request:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"请求 ID {request_id} 不存在"
            )
        
        return success_response(data=request, message="获取请求详情成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"获取请求详情失败: {str(e)}"
        )


@router.put("/{request_id}", response_model=BaseResponse[HttpRequestResponse])
async def update_request(
    request_id: int,
    request_data: HttpRequestUpdate,
    db: Session = Depends(get_db)
):
    """更新HTTP请求"""
    try:
        service = RequestService(db)
        
        # 检查请求是否存在
        existing = service.get_request(request_id)
        if not existing:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"请求 ID {request_id} 不存在"
            )
        
        # 检查名称冲突
        if request_data.name and request_data.name != existing.name:
            name_conflict = service.get_request_by_name(request_data.name)
            if name_conflict:
                return error_response(
                    code=ErrorCodes.PARAMETER_ERROR,
                    message=f"请求名称 '{request_data.name}' 已存在"
                )
        
        result = service.update_request(request_id, request_data)
        return success_response(data=result, message="请求更新成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"更新请求失败: {str(e)}"
        )


@router.delete("/{request_id}", response_model=BaseResponse[dict])
async def delete_request(
    request_id: int,
    db: Session = Depends(get_db)
):
    """删除HTTP请求"""
    try:
        service = RequestService(db)
        
        # 检查请求是否存在
        existing = service.get_request(request_id)
        if not existing:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"请求 ID {request_id} 不存在"
            )
        
        success = service.delete_request(request_id)
        if success:
            return success_response(
                data={"deleted_id": request_id},
                message="请求删除成功"
            )
        else:
            return error_response(
                code=ErrorCodes.INTERNAL_ERROR,
                message="删除请求失败"
            )
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"删除请求失败: {str(e)}"
        )


@router.post("/import/fiddler", response_model=BaseResponse[HttpRequestResponse])
async def import_from_fiddler(
    import_data: FiddlerImportData,
    db: Session = Depends(get_db)
):
    """从Fiddler Raw数据导入请求"""
    try:
        service = RequestService(db)
        
        # 检查名称是否已存在
        existing = service.get_request_by_name(import_data.name)
        if existing:
            return error_response(
                code=ErrorCodes.PARAMETER_ERROR,
                message=f"请求名称 '{import_data.name}' 已存在"
            )
        
        result = service.import_from_fiddler(
            name=import_data.name,
            raw_data=import_data.raw_data,
            description=import_data.description
        )
        
        return success_response(data=result, message="Fiddler数据导入成功")
        
    except ValueError as e:
        return error_response(
            code=ErrorCodes.PARAMETER_ERROR,
            message=str(e)
        )
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"导入失败: {str(e)}"
        )


@router.post("/import/curl", response_model=BaseResponse[HttpRequestResponse])
async def import_from_curl(
    import_data: CurlImportData,
    db: Session = Depends(get_db)
):
    """从cURL命令导入请求"""
    try:
        service = RequestService(db)
        
        # 检查名称是否已存在
        existing = service.get_request_by_name(import_data.name)
        if existing:
            return error_response(
                code=ErrorCodes.PARAMETER_ERROR,
                message=f"请求名称 '{import_data.name}' 已存在"
            )
        
        result = service.import_from_curl(
            name=import_data.name,
            curl_command=import_data.curl_command,
            description=import_data.description
        )
        
        return success_response(data=result, message="cURL命令导入成功")
        
    except ValueError as e:
        return error_response(
            code=ErrorCodes.PARAMETER_ERROR,
            message=str(e)
        )
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"导入失败: {str(e)}"
        )


@router.post("/{request_id}/test", response_model=BaseResponse[RequestTestResult])
async def test_request(
    request_id: int,
    test_data: Optional[RequestTestData] = None,
    db: Session = Depends(get_db)
):
    """测试HTTP请求"""
    try:
        # 获取请求
        service = RequestService(db)
        request = service.get_request(request_id)
        
        if not request:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"请求 ID {request_id} 不存在"
            )
        
        # 执行测试
        executor = ExecutorService()
        result = executor.test_request(request, test_data)
        
        return success_response(data=result, message="请求测试完成")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"测试请求失败: {str(e)}"
        )


@router.post("/{request_id}/duplicate", response_model=BaseResponse[HttpRequestResponse])
async def duplicate_request(
    request_id: int,
    new_name: str = Query(..., description="新请求名称"),
    db: Session = Depends(get_db)
):
    """复制HTTP请求"""
    try:
        service = RequestService(db)
        
        # 检查原请求是否存在
        original = service.get_request(request_id)
        if not original:
            return error_response(
                code=ErrorCodes.NOT_FOUND,
                message=f"请求 ID {request_id} 不存在"
            )
        
        # 检查新名称是否已存在
        existing = service.get_request_by_name(new_name)
        if existing:
            return error_response(
                code=ErrorCodes.PARAMETER_ERROR,
                message=f"请求名称 '{new_name}' 已存在"
            )
        
        result = service.duplicate_request(request_id, new_name)
        return success_response(data=result, message="请求复制成功")
        
    except Exception as e:
        return error_response(
            code=ErrorCodes.INTERNAL_ERROR,
            message=f"复制请求失败: {str(e)}"
        ) 