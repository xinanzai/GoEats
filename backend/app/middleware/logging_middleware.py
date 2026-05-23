import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        log_data = {
            "method": request.method,
            "path": request.url.path,
            "query": str(request.url.query) if request.url.query else "",
            "client_ip": self.get_client_ip(request),
        }

        request_id = str(time.time()).replace(".", "")[-6:]
        logger.info(f"[{request_id}] >>> {log_data['method']} {log_data['path']} {log_data['query']} from {log_data['client_ip']}")

        response = await call_next(request)

        process_time = time.time() - start_time
        log_data["status"] = response.status_code
        log_data["process_time"] = f"{process_time:.4f}s"

        if response.status_code >= 400:
            logger.warning(
                f"[{request_id}] <<< {log_data['method']} {log_data['path']} "
                f"-> {log_data['status']} ({log_data['process_time']})"
            )
        else:
            logger.info(
                f"[{request_id}] <<< {log_data['method']} {log_data['path']} "
                f"-> {log_data['status']} ({log_data['process_time']})"
            )

        response.headers["X-Process-Time"] = log_data["process_time"]
        response.headers["X-Request-Id"] = request_id

        return response

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """获取客户端真实 IP"""
        if request.headers.get("x-forwarded-for"):
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        if request.headers.get("x-real-ip"):
            return request.headers["x-real-ip"]
        return request.client.host if request.client else "unknown"
