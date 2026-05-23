import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logging(
    level: str = "INFO",
    log_to_file: bool = True,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
):
    """配置全局日志"""
    log_level = getattr(logging, level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    handlers = [console_handler]

    if log_to_file:
        app_log_path = LOG_DIR / "app.log"
        app_handler = RotatingFileHandler(
            app_log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        app_handler.setFormatter(formatter)
        app_handler.setLevel(log_level)
        handlers.append(app_handler)

        error_log_path = LOG_DIR / "error.log"
        error_handler = RotatingFileHandler(
            error_log_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(logging.ERROR)
        handlers.append(error_handler)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()
    for handler in handlers:
        root_logger.addHandler(handler)

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取命名 logger"""
    return logging.getLogger(name)
