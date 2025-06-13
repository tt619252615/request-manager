"""
HTTP 请求服务
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..models.request import HttpRequest
from ..schemas.request import HttpRequestCreate, HttpRequestUpdate
from ..utils.parser import FiddlerParser, CurlParser, validate_parsed_request


class RequestService:
    """HTTP请求服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_request(self, request_data: HttpRequestCreate) -> HttpRequest:
        """创建HTTP请求"""
        db_request = HttpRequest(**request_data.model_dump())
        self.db.add(db_request)
        self.db.commit()
        self.db.refresh(db_request)
        return db_request
    
    def get_request(self, request_id: int) -> Optional[HttpRequest]:
        """根据ID获取请求"""
        return self.db.query(HttpRequest).filter(HttpRequest.id == request_id).first()
    
    def get_requests(
        self, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        method: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[HttpRequest]:
        """获取请求列表"""
        query = self.db.query(HttpRequest)
        
        # 搜索过滤
        if search:
            search_filter = or_(
                HttpRequest.name.ilike(f"%{search}%"),
                HttpRequest.description.ilike(f"%{search}%"),
                HttpRequest.url.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # 方法过滤
        if method:
            query = query.filter(HttpRequest.method == method)
        
        # 标签过滤
        if tags:
            for tag in tags:
                query = query.filter(HttpRequest.tags.contains([tag]))
        
        return query.offset(skip).limit(limit).all()
    
    def update_request(
        self, 
        request_id: int, 
        request_data: HttpRequestUpdate
    ) -> Optional[HttpRequest]:
        """更新请求"""
        db_request = self.get_request(request_id)
        if not db_request:
            return None
        
        # 只更新提供的字段
        update_data = request_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_request, field, value)
        
        self.db.commit()
        self.db.refresh(db_request)
        return db_request
    
    def delete_request(self, request_id: int) -> bool:
        """删除请求"""
        db_request = self.get_request(request_id)
        if not db_request:
            return False
        
        self.db.delete(db_request)
        self.db.commit()
        return True
    
    def import_from_fiddler(self, name: str, raw_data: str, description: Optional[str] = None) -> HttpRequest:
        """从Fiddler Raw数据导入请求"""
        try:
            # 解析Fiddler数据
            parsed = FiddlerParser.parse(raw_data)
            
            # 验证解析结果
            is_valid, errors = validate_parsed_request(parsed)
            if not is_valid:
                raise ValueError(f"解析失败: {', '.join(errors)}")
            
            # 创建请求对象
            request_data = HttpRequestCreate(
                name=name,
                description=description,
                method=parsed.method,
                url=parsed.url,
                headers=parsed.headers,
                params=parsed.params,
                body=parsed.body,
                tags=["imported", "fiddler"]
            )
            
            return self.create_request(request_data)
            
        except Exception as e:
            raise ValueError(f"Fiddler数据导入失败: {str(e)}")
    
    def import_from_curl(self, name: str, curl_command: str, description: Optional[str] = None) -> HttpRequest:
        """从cURL命令导入请求"""
        try:
            # 解析cURL命令
            parsed = CurlParser.parse(curl_command)
            
            # 验证解析结果
            is_valid, errors = validate_parsed_request(parsed)
            if not is_valid:
                raise ValueError(f"解析失败: {', '.join(errors)}")
            
            # 创建请求对象
            request_data = HttpRequestCreate(
                name=name,
                description=description,
                method=parsed.method,
                url=parsed.url,
                headers=parsed.headers,
                params=parsed.params,
                body=parsed.body,
                tags=["imported", "curl"]
            )
            
            return self.create_request(request_data)
            
        except Exception as e:
            raise ValueError(f"cURL命令导入失败: {str(e)}")
    
    def count_requests(self) -> int:
        """获取请求总数"""
        return self.db.query(HttpRequest).count()
    
    def get_request_by_name(self, name: str) -> Optional[HttpRequest]:
        """根据名称获取请求"""
        return self.db.query(HttpRequest).filter(HttpRequest.name == name).first()
    
    def duplicate_request(self, request_id: int, new_name: str) -> Optional[HttpRequest]:
        """复制请求"""
        original = self.get_request(request_id)
        if not original:
            return None
        
        # 创建副本
        request_data = HttpRequestCreate(
            name=new_name,
            description=f"Copy of {original.name}",
            method=original.method,
            url=original.url,
            headers=original.headers,
            params=original.params,
            body=original.body,
            tags=original.tags + ["copied"]
        )
        
        return self.create_request(request_data) 