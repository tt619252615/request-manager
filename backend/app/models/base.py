"""
基础数据库模型
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base, declared_attr

Base = declarative_base()


class BaseModel(Base):
    """基础模型类，提供通用字段和方法"""
    
    __abstract__ = True
    
    @declared_attr
    def __tablename__(cls):
        """自动生成表名（类名转下划线）"""
        import re
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    created_at = Column(
        DateTime, 
        default=func.now(), 
        server_default=func.now(),
        comment="创建时间"
    )
    updated_at = Column(
        DateTime, 
        default=func.now(), 
        onupdate=func.now(),
        server_default=func.now(),
        comment="更新时间"
    )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>" 