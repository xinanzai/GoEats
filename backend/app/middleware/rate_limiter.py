import time
import logging
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """限流中间件 - 基于 IP 的滑动窗口限流"""

    def __init__(
        self,
        app,
        requests_per_minute: int = 300,
        requests_per_second: int = 50,
        blocked_duration: int = 30,
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_second = requests_per_second
        self.blocked_duration = blocked_duration

        self.ip_requests = defaultdict(list)
        self.blocked_ips = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)

        if self._is_blocked(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "code": 429,
                    "message": "请求过于频繁，请稍后再试",
                    "data": None,
                },
            )

        now = time.time()

        if not self._check_rate_limit(client_ip, now):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            self._block_ip(client_ip)
            return JSONResponse(
                status_code=429,
                content={
                    "code": 429,
                    "message": "请求过于频繁，请稍后再试",
                    "data": None,
                },
            )

        self._record_request(client_ip, now)
        response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(
            self._get_remaining_requests(client_ip, now)
        )
        return response

    def _get_client_ip(self, request: Request) -> str:
        if request.headers.get("x-forwarded-for"):
            return request.headers["x-forwarded-for"].split(",")[0].strip()
        if request.headers.get("x-real-ip"):
            return request.headers["x-real-ip"]
        return request.client.host if request.client else "127.0.0.1"

    def _is_blocked(self, client_ip: str) -> bool:
        if client_ip in self.blocked_ips:
            if time.time() - self.blocked_ips[client_ip] < self.blocked_duration:
                return True
            else:
                del self.blocked_ips[client_ip]
        return False

    def _block_ip(self, client_ip: str):
        self.blocked_ips[client_ip] = time.time()
        logger.error(f"IP blocked due to rate limit: {client_ip}")

    def _check_rate_limit(self, client_ip: str, now: float) -> bool:
        requests = self.ip_requests.get(client_ip, [])

        second_requests = [t for t in requests if now - t < 1]
        if len(second_requests) >= self.requests_per_second:
            return False

        minute_requests = [t for t in requests if now - t < 60]
        if len(minute_requests) >= self.requests_per_minute:
            return False

        return True

    def _record_request(self, client_ip: str, now: float):
        if client_ip not in self.ip_requests:
            self.ip_requests[client_ip] = []

        self.ip_requests[client_ip].append(now)

        cutoff = now - 120
        self.ip_requests[client_ip] = [
            t for t in self.ip_requests[client_ip] if t > cutoff
        ]

    def _get_remaining_requests(self, client_ip: str, now: float) -> int:
        requests = self.ip_requests.get(client_ip, [])
        minute_requests = [t for t in requests if now - t < 60]
        return max(0, self.requests_per_minute - len(minute_requests))
