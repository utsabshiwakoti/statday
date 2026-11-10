"""A fixed-window rate limiter kept in memory.

Each caller (an API key, or an IP address without one) gets `limit` requests per window. Windows
are aligned to the clock (every hour on the hour by default), so the reset time is easy to report.

In memory means per process: fine for one instance. With several instances this would move to
Redis, where INCR + EXPIRE does the same thing atomically.
"""

import math
import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Decision:
    allowed: bool
    limit: int
    remaining: int
    reset_after: int  # seconds until the window resets

    def headers(self, window: int) -> dict[str, str]:
        # Header names from the IETF "RateLimit header fields for HTTP" draft.
        headers = {
            "RateLimit-Limit": str(self.limit),
            "RateLimit-Remaining": str(self.remaining),
            "RateLimit-Reset": str(self.reset_after),
            "RateLimit-Policy": f"{self.limit};w={window}",
        }
        if not self.allowed:
            headers["Retry-After"] = str(self.reset_after)
        return headers


class FixedWindowLimiter:
    def __init__(self, window_seconds: int, clock=time.time):
        self.window = window_seconds
        self.clock = clock  # injectable so tests can move time forward
        self._counts: dict[str, tuple[int, int]] = {}  # caller -> (window number, requests so far)
        self._lock = threading.Lock()  # sync routes run in a thread pool

    def hit(self, caller: str, limit: int) -> Decision:
        now = self.clock()
        current = int(now // self.window)
        reset_after = max(1, math.ceil((current + 1) * self.window - now))
        with self._lock:
            window, count = self._counts.get(caller, (current, 0))
            if window != current:
                count = 0
                if len(self._counts) > 10_000:  # now and then, forget callers from old windows
                    self._counts = {k: v for k, v in self._counts.items() if v[0] == current}
            if count >= limit:
                return Decision(False, limit, 0, reset_after)
            self._counts[caller] = (current, count + 1)
        return Decision(True, limit, limit - count - 1, reset_after)

    def reset(self) -> None:
        with self._lock:
            self._counts.clear()
