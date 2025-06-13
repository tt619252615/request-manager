"""
数据库配置和会话管理
支持MySQL和JSON配置
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .config import settings

# 创建数据库引擎
engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # 在调试模式下显示SQL语句
    pool_pre_ping=True,  # 启用连接池预检查
    pool_recycle=3600,   # 连接回收时间（秒）
    pool_size=20,        # 增加连接池大小以支持多线程
    max_overflow=30,     # 增加最大溢出连接数
    pool_timeout=30,     # 获取连接的超时时间（秒）
    # MySQL连接参数
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30,
    } if "mysql" in settings.database_url else {}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 使用models.base中的Base，而不是重新创建
from .models.base import Base


def get_db() -> Session:
    """获取数据库会话的依赖函数"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """获取数据库会话的上下文管理器"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """创建所有数据表"""
    # 确保所有模型都被导入，这样它们的表才会被注册到Base.metadata中
    from .models import request, task, execution
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """删除所有数据表"""
    Base.metadata.drop_all(bind=engine)


def create_database():
    """创建数据库（仅限MySQL）"""
    from .core.config_manager import get_config
    
    try:
        config = get_config()
        if config.database.type == "mysql":
            import pymysql
            
            # 连接到MySQL服务器（不指定数据库）
            connection = pymysql.connect(
                host=config.database.host,
                port=config.database.port,
                user=config.database.username,
                password=config.database.password,
                charset=config.database.charset
            )
            
            try:
                cursor = connection.cursor()
                # 创建数据库（如果不存在）
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.database.database}` CHARACTER SET {config.database.charset} COLLATE {config.database.charset}_unicode_ci")
                connection.commit()
                print(f"✅ 数据库 '{config.database.database}' 创建成功")
            finally:
                connection.close()
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        raise 