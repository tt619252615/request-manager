"""
HTTP请求相关的数据模式
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, HttpUrl

from ..models.request import HttpMethodEnum


class HttpRequestBase(BaseModel):
    """HTTP请求基础模式"""
    name: str = Field(..., min_length=1, max_length=255, description="请求名称")
    description: Optional[str] = Field(None, description="请求描述")
    method: HttpMethodEnum = Field(default=HttpMethodEnum.GET, description="HTTP方法")
    url: str = Field(..., description="请求URL")
    headers: Dict[str, str] = Field(default_factory=dict, description="请求头")
    params: Dict[str, str] = Field(default_factory=dict, description="查询参数")
    body: Optional[str] = Field(None, description="请求体")
    tags: List[str] = Field(default_factory=list, description="标签")


class HttpRequestCreate(HttpRequestBase):
    """创建HTTP请求的数据模式"""
    pass


class HttpRequestUpdate(BaseModel):
    """更新HTTP请求的数据模式"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="请求名称")
    description: Optional[str] = Field(None, description="请求描述")
    method: Optional[HttpMethodEnum] = Field(None, description="HTTP方法")
    url: Optional[str] = Field(None, description="请求URL")
    headers: Optional[Dict[str, str]] = Field(None, description="请求头")
    params: Optional[Dict[str, str]] = Field(None, description="查询参数")
    body: Optional[str] = Field(None, description="请求体")
    tags: Optional[List[str]] = Field(None, description="标签")


class HttpRequestInDB(HttpRequestBase):
    """数据库中的HTTP请求模式"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HttpRequestResponse(HttpRequestInDB):
    """HTTP请求响应模式"""
    pass


class RequestTestData(BaseModel):
    """请求测试数据模式"""
    request_id: int = Field(..., description="请求ID")
    override_headers: Optional[Dict[str, str]] = Field(None, description="覆盖的请求头")
    override_params: Optional[Dict[str, str]] = Field(None, description="覆盖的查询参数")
    override_body: Optional[str] = Field(None, description="覆盖的请求体")
    timeout: Optional[int] = Field(30, description="超时时间（秒）")
    use_proxy: bool = Field(False, description="是否使用代理")


class RequestTestResult(BaseModel):
    """请求测试结果模式"""
    success: bool = Field(..., description="是否成功")
    status_code: Optional[int] = Field(None, description="HTTP状态码")
    response_body: Optional[str] = Field(None, description="响应体")
    response_headers: Optional[Dict[str, str]] = Field(None, description="响应头")
    response_time: Optional[float] = Field(None, description="响应时间（毫秒）")
    error_message: Optional[str] = Field(None, description="错误消息")


class FiddlerImportData(BaseModel):
    """Fiddler导入数据模式"""
    name: str = Field(..., min_length=1, max_length=255, description="请求名称")
    description: Optional[str] = Field(None, description="请求描述")
    raw_data: str = Field(..., min_length=1, description="Fiddler Raw数据")
    import_type: str = Field(default="fiddler", description="导入类型")


class CurlImportData(BaseModel):
    """cURL导入数据模式"""
    name: str = Field(..., min_length=1, max_length=255, description="请求名称")
    description: Optional[str] = Field(None, description="请求描述")
    curl_command: str = Field(..., min_length=1, description="cURL命令")
    import_type: str = Field(default="curl", description="导入类型") 