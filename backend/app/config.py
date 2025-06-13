"""
应用配置管理
兼容性模块，保持向后兼容
"""
import os
from typing import Optional, List
from .core.config_manager import init_config, get_config


# 初始化配置
try:
    init_config()
    config_manager = get_config()
except Exception:
    # 如果配置加载失败，使用默认配置
    config_manager = None


class Settings:
    """兼容性配置类"""
    
    def __init__(self):
        if config_manager:
            # 使用新的配置管理器
            self.app_name = config_manager.app.name
            self.app_version = config_manager.app.version
            self.debug = config_manager.app.debug
            self.host = config_manager.app.host
            self.port = config_manager.app.port
            
            self.database_url = config_manager.database.url
            self.redis_url = config_manager.redis.url
            
            self.secret_key = config_manager.security.secret_key
            self.algorithm = config_manager.security.algorithm
            self.access_token_expire_minutes = config_manager.security.access_token_expire_minutes
            
            self.cors_origins = config_manager.cors.origins
            
            self.default_timeout = config_manager.scheduler.default_timeout
            self.max_retry_attempts = config_manager.scheduler.max_retry_attempts
            self.default_thread_count = config_manager.scheduler.default_thread_count
            
            self.proxy_timeout = config_manager.proxy.timeout
            self.proxy_rotation_enabled = config_manager.proxy.rotation_enabled
            
            self.log_level = config_manager.logging.level
            self.log_file = config_manager.logging.file
        else:
            # 使用默认配置（备用方案）
            self.app_name = "RequestManager"
            self.app_version = "0.1.0"
            self.debug = True
            self.host = "0.0.0.0"
            self.port = 8000
            
            self.database_url = "sqlite:///./request_manager.db"
            self.redis_url = "redis://localhost:6379/0"
            
            self.secret_key = "your-secret-key-here"
            self.algorithm = "HS256"
            self.access_token_expire_minutes = 30
            
            self.cors_origins = [
                "http://localhost:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:5174"
            ]
            
            self.default_timeout = 30
            self.max_retry_attempts = 10
            self.default_thread_count = 5
            
            self.proxy_timeout = 30
            self.proxy_rotation_enabled = True
            
            self.log_level = "INFO"
            self.log_file = None


# 创建设置实例
settings = Settings()


def setup_logging() -> None:
    """配置应用日志"""
    from loguru import logger
    
    logger.remove()  # 移除默认的日志处理器
    
    # 控制台日志
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True,
    )
    
    # 文件日志（如果配置了日志文件）
    if settings.log_file:
        logger.add(
            sink=settings.log_file,
            level=settings.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="1 week",
            compression="zip",
        )
    
    logger.info(f"日志系统已初始化，级别：{settings.log_level}")


# 应用启动时不自动初始化日志，由main.py控制 