from fastapi import Request, HTTPException
from collections import defaultdict
import time
from typing import Callable
import os

class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.max_requests = 10
        self.window = 60  # 1 minute
    
    async def is_rate_limited(self, client_ip: str) -> bool:
        now = time.time()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] 
            if now - req_time < self.window
        ]
        if len(self.requests[client_ip]) >= self.max_requests:
            return True
        self.requests[client_ip].append(now)
        return False

rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next: Callable):
    client_ip = request.client.host
    if await rate_limiter.is_rate_limited(client_ip):
        raise HTTPException(status_code=429, detail="Rate limited - 10 req/min")
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
