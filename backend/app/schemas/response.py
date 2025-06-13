"""
统一API响应模式
"""
from typing import Any, Generic, Optional, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime


DataType = TypeVar("DataType")


class BaseResponse(BaseModel, Generic[DataType]):
    """统一API响应基类"""
    
    code: int = Field(description="响应状态码，0表示成功，非0表示失败")
    data: Optional[DataType] = Field(default=None, description="响应数据")
    message: str = Field(description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    
    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp() * 1000)  # 转换为毫秒时间戳
        }


class SuccessResponse(BaseResponse[DataType], Generic[DataType]):
    """成功响应"""
    
    def __init__(
        self, 
        data: Optional[DataType] = None, 
        message: str = "操作成功",
        **kwargs
    ):
        super().__init__(code=0, data=data, message=message, **kwargs)


class ErrorResponse(BaseResponse[None]):
    """错误响应"""
    
    def __init__(
        self, 
        code: int = -1, 
        message: str = "操作失败",
        **kwargs
    ):
        super().__init__(code=code, data=None, message=message, **kwargs)


class PaginationInfo(BaseModel):
    """分页信息"""
    
    page: int = Field(description="当前页码")
    size: int = Field(description="每页大小")
    total: int = Field(description="总记录数")
    pages: int = Field(description="总页数")


class PaginatedData(BaseModel, Generic[DataType]):
    """分页数据"""
    
    items: list[DataType] = Field(description="数据列表")
    pagination: PaginationInfo = Field(description="分页信息")


class PaginatedResponse(BaseResponse[PaginatedData[DataType]], Generic[DataType]):
    """分页响应"""
    
    def __init__(
        self,
        items: list[DataType],
        page: int,
        size: int,
        total: int,
        message: str = "查询成功",
        **kwargs
    ):
        pages = (total + size - 1) // size if size > 0 else 0
        pagination_info = PaginationInfo(page=page, size=size, total=total, pages=pages)
        paginated_data = PaginatedData(items=items, pagination=pagination_info)
        super().__init__(code=0, data=paginated_data, message=message, **kwargs)


# 常用响应函数
def success_response(
    data: Any = None, 
    message: str = "操作成功"
) -> SuccessResponse:
    """创建成功响应"""
    return SuccessResponse(data=data, message=message)


def error_response(
    code: int = -1, 
    message: str = "操作失败"
) -> ErrorResponse:
    """创建错误响应"""
    return ErrorResponse(code=code, message=message)


def paginated_response(
    items: list[Any],
    page: int,
    size: int,
    total: int,
    message: str = "查询成功"
) -> PaginatedResponse:
    """创建分页响应"""
    return PaginatedResponse(
        items=items,
        page=page,
        size=size,
        total=total,
        message=message
    )


# 常用错误码定义
class ErrorCodes:
    """错误码定义"""
    
    # 通用错误码
    SUCCESS = 0
    UNKNOWN_ERROR = -1
    PARAMETER_ERROR = -2
    UNAUTHORIZED = -3
    FORBIDDEN = -4
    NOT_FOUND = -5
    METHOD_NOT_ALLOWED = -6
    INTERNAL_ERROR = -7
    
    # 业务错误码
    REQUEST_NOT_FOUND = 1001
    REQUEST_INVALID = 1002
    REQUEST_EXECUTION_FAILED = 1003
    
    TASK_NOT_FOUND = 2001
    TASK_INVALID = 2002
    TASK_ALREADY_RUNNING = 2003
    TASK_NOT_RUNNING = 2004
    
    EXECUTION_NOT_FOUND = 3001
    EXECUTION_FAILED = 3002
    
    # 解析错误码
    PARSE_ERROR = 4001
    INVALID_FORMAT = 4002 