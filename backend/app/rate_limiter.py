import time
from fastapi import HTTPException, Request,status

class TokenBucketLimiter:
    """
    In Memoery Thread safe token bucket rate limiter
    Track structural api traffic allocation mathematically without redis
    """
    def __init__(self,capacity:int,refill_rate:float):
        self.capacity=capacity
        self.refill_rate=refill_rate
        self.tokens=float(capacity)
        self.last_refill=time.time()
    
    def consume(self)->bool:
        now=time.time()
        elapsed=now-self.last_refill
        self.tokens = min(self.capacity, self.tokens + (elapsed * self.refill_rate))
        self.last_refill = now

        if self.tokens>=1:
            self.tokens-=1
            return True
        else:
            return False

ai_endpoint_limiter=TokenBucketLimiter(capacity=5,refill_rate=0.1) # 5 requests per second

def rate_limit_ai_summary(request: Request):
    
    if not ai_endpoint_limiter.consume():
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit breached. Artificial Intelligence processing pipelines are currently saturated."
        )