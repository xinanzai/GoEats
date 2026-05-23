import os
import sys

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.exceptions import AppException
from app.database import init_db
from app.utils.logger import setup_logging, get_logger
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.rate_limiter import RateLimiterMiddleware


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    setup_logging(level="DEBUG" if settings.DEBUG else "INFO")
    logger = get_logger(__name__)

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    # 配置 CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 请求日志中间件
    app.add_middleware(RequestLoggingMiddleware)

    # 限流中间件（测试环境中禁用）
    if "pytest" not in sys.modules:
        app.add_middleware(RateLimiterMiddleware)

    # 全局异常处理
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.code,
            content={
                "code": exc.code,
                "message": exc.message,
                "data": exc.data,
            },
        )

    # 启动时初始化数据库
    @app.on_event("startup")
    async def startup_event():
        await init_db()
        logger.info("数据库链接初始化完成")
        logger.info(f"应用启动: {settings.APP_NAME} v{settings.APP_VERSION}")

    # 注册路由
    from app.api.router import router
    app.include_router(router, prefix="/api/v1")

    # 挂载静态文件服务（上传的文件）
    upload_dir = settings.UPLOAD_DIR
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

    return app


app = create_app()
