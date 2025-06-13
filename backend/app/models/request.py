"""
HTTP 请求数据模型
"""

from sqlalchemy import Column, String, Text, Enum
from sqlalchemy.dialects.postgresql import JSON
import enum

from .base import BaseModel


class HttpMethodEnum(str, enum.Enum):
    """HTTP 方法枚举"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class HttpRequest(BaseModel):
    """HTTP 请求模型"""
    
    __tablename__ = "http_requests"
    
    # 基本信息
    name = Column(String(255), nullable=False, comment="请求名称")
    description = Column(Text, comment="请求描述")
    
    # 请求信息
    method = Column(
        Enum(HttpMethodEnum), 
        nullable=False, 
        default=HttpMethodEnum.GET,
        comment="HTTP方法"
    )
    url = Column(Text, nullable=False, comment="请求URL")
    headers = Column(JSON, default=dict, comment="请求头")
    params = Column(JSON, default=dict, comment="查询参数")
    body = Column(Text, comment="请求体")
    
    # 元数据
    tags = Column(JSON, default=list, comment="标签")
    
    def __repr__(self) -> str:
        return f"<HttpRequest(id={self.id}, name='{self.name}', method={self.method})>" 