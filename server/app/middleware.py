from fastapi import Request, HTTPException
from collections import defaultdict
import time
import uuid
import os
from typing import Callable

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.max_requests = 10
        self.window = 60
    async def is_rate_limited(self, client_ip: str) -> tuple:
        now = time.time()
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.window]
        remaining = self.max_requests - len(self.requests[client_ip])
        reset_time = int(now + self.window)
        if len(self.requests[client_ip]) >= self.max_requests:
            return True, remaining, reset_time
        self.requests[client_ip].append(now)
        return False, remaining, reset_time
rate_limiter = RateLimiter()
async def production_middleware(request: Request, call_next: Callable):
    request_id = str(uuid.uuid4())
    api_key = request.headers.get("X-Api-Key")
    required_api_key = os.getenv("API_KEY")
    if required_api_key and api_key != required_api_key:
        raise HTTPException(401, "Invalid API key")
    is_limited, remaining, reset_time = await rate_limiter.is_rate_limited(request.client.host)
    if is_limited:
        raise HTTPException(429, "Rate limited", headers={"X-RateLimit-Remaining": "0","X-RateLimit-Reset": str(reset_time)})
    start_time = time.time()
    try:
        response = await call_next(request)
    except Exception as e:
        from app.database import log_error
        log_error(request_id, request.url.path, str(e))
        raise
    process_time = time.time() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(reset_time)
    response.headers["X-Process-Time"] = f"{process_time:.2f}"
    return response
