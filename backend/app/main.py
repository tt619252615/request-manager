"""
RequestManager 主应用
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger
import time

from backend.app.config import settings, setup_logging
from backend.app.database import create_database, create_tables
from backend.app.schemas.response import error_response, ErrorCodes, BaseResponse
from backend.app.services.scheduler_service import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    setup_logging()
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} 启动中...")
    
    try:
        # 创建数据库（仅MySQL需要）
        create_database()
        # 创建数据表
        create_tables()
        logger.info("✅ 数据库初始化成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        logger.warning("⚠️ 应用将在无数据库模式下运行")
    
    # 启动调度服务
    try:
        scheduler_service.start()
        logger.info("✅ 任务调度服务启动成功")
    except Exception as e:
        logger.error(f"❌ 调度服务启动失败: {e}")
    
    logger.info(f"📝 API文档地址: http://localhost:{settings.port}/docs")
    logger.info(f"🔧 调试模式: {settings.debug}")
    logger.info(f"🗄️ 数据库类型: {settings.database_url.split('://')[0]}")
    
    yield
    
    # 关闭时
    logger.info(f"👋 {settings.app_name} 正在关闭...")
    
    # 停止调度服务
    try:
        scheduler_service.stop()
        logger.info("✅ 调度服务已停止")
    except Exception as e:
        logger.error(f"❌ 停止调度服务失败: {e}")


# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于FastAPI的HTTP请求管理与调度系统",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    start_time = time.time()
    
    # 记录请求开始
    logger.info(f"🌐 {request.method} {request.url.path} - 开始处理")
    
    response = await call_next(request)
    
    # 计算处理时间
    process_time = time.time() - start_time
    
    # 记录请求结束
    logger.info(
        f"✅ {request.method} {request.url.path} - "
        f"状态码: {response.status_code}, "
        f"耗时: {process_time:.3f}s"
    )
    
    return response


# 异常处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """处理请求验证错误"""
    logger.warning(f"参数验证失败: {exc.errors()}")
    
    # 安全地提取错误信息，避免datetime序列化问题
    errors = []
    for error in exc.errors():
        error_dict = {
            "type": str(error.get("type", "")),
            "loc": list(error.get("loc", [])),
            "msg": str(error.get("msg", "")),
            "input": str(error.get("input", ""))[:100]  # 限制长度避免过长
        }
        errors.append(error_dict)
    
    response_data = error_response(
        code=ErrorCodes.PARAMETER_ERROR,
        message=f"参数验证失败: {errors[0]['msg'] if errors else '未知错误'}"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=response_data.model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    error_msg = f"未处理的异常: {type(exc).__name__}: {str(exc)}"
    logger.error(error_msg)
    
    response_data = error_response(
        code=ErrorCodes.INTERNAL_ERROR,
        message="服务器内部错误"
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=response_data.model_dump()
    )


@app.get("/", response_model=BaseResponse[dict])
async def root():
    """根路径"""
    return BaseResponse(
        code=0,
        data={
            "name": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "scheduler_status": "running" if scheduler_service.running else "stopped",
            "database_type": settings.database_url.split('://')[0]
        },
        message="RequestManager API is running"
    )


@app.get("/health", response_model=BaseResponse[dict])
async def health_check():
    """健康检查"""
    return BaseResponse(
        code=0,
        data={
            "status": "healthy",
            "scheduler_running": scheduler_service.running,
            "running_tasks": scheduler_service.get_running_task_count(),
            "database_type": settings.database_url.split('://')[0]
        },
        message="Service is healthy"
    )


@app.get("/config", response_model=BaseResponse[dict])
async def get_config_info():
    """获取配置信息"""
    from .core.config_manager import get_config
    
    try:
        config = get_config()
        config_info = {
            "app": {
                "name": config.app.name,
                "version": config.app.version,
                "debug": config.app.debug
            },
            "database": {
                "type": config.database.type,
                "host": config.database.host,
                "port": config.database.port,
                "database": config.database.database
            },
            "scheduler": {
                "default_timeout": config.scheduler.default_timeout,
                "default_thread_count": config.scheduler.default_thread_count,
                "check_interval": config.scheduler.check_interval
            }
        }
        
        return BaseResponse(
            code=0,
            data=config_info,
            message="Configuration loaded successfully"
        )
    except Exception as e:
        return BaseResponse(
            code=1,
            data={"error": str(e)},
            message="Failed to load configuration"
        )


# 注册API路由
from .api import requests, tasks, executions, system

app.include_router(requests.router, prefix="/api/requests", tags=["HTTP请求管理"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["任务管理"])
app.include_router(executions.router, prefix="/api/executions", tags=["执行记录"])
app.include_router(system.router, prefix="/api/system", tags=["系统管理"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    ) 