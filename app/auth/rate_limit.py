from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from time import time
from typing import Deque, Dict, Tuple

from fastapi import Depends, HTTPException, Request, status


@dataclass(frozen=True)
class RateLimitConfig:
    max_requests: int
    window_seconds: int


# In-memory rate limit store (good enough for a class project / single-process app)
# For production: use Redis or another shared backend.
_BUCKETS: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)


def _get_client_key(request: Request) -> str:
    # TestClient sets a client host; fall back to a generic key.
    return request.client.host if request.client else "unknown"


def rate_limit(endpoint: str, *, config: RateLimitConfig = RateLimitConfig(max_requests=100, window_seconds=60)):
    def dependency(request: Request):
        key = (_get_client_key(request), endpoint)
        now = time()

        bucket = _BUCKETS[key]
        window_start = now - config.window_seconds
        while bucket and bucket[0] < window_start:
            bucket.popleft()

        if len(bucket) >= config.max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests, please try again later.",
            )

        bucket.append(now)

    return Depends(dependency)
