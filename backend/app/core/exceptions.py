from fastapi import HTTPException
from typing import Any


class AppException(HTTPException):
    """应用基础异常"""
    def __init__(self, code: int, message: str, data: Any = None):
        self.code = code
        self.message = message
        self.data = data
        super().__init__(status_code=code, detail=message)


class NotFoundException(AppException):
    """资源未找到异常"""
    def __init__(self, resource: str, resource_id: Any):
        super().__init__(
            code=404,
            message=f"{resource} {resource_id} 不存在",
        )


class ValidationException(AppException):
    """数据验证异常"""
    def __init__(self, message: str):
        super().__init__(code=400, message=message)


class PermissionException(AppException):
    """权限异常"""
    def __init__(self, message: str = "没有权限执行此操作"):
        super().__init__(code=403, message=message)


class ConflictException(AppException):
    """资源冲突异常"""
    def __init__(self, message: str):
        super().__init__(code=409, message=message)
