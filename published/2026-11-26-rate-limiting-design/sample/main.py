import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, int] = defaultdict(int)
        self.timestamps: Dict[str, int] = defaultdict(int)
    
    def allow_request(self, key: str) -> bool:
        # Get current time
        now = time.time()
        
        # Remove old entries outside the window
        cutoff = now - self.window_seconds
        if self.timestamps[key] < cutoff:
            self.requests[key] = 0
            self.timestamps[key] = now
        
        # Check if we've exceeded the limit
        if self.requests[key] >= self.max_requests:
            return False
        
        # Allow request and update counters
        self.requests[key] += 1
        self.timestamps[key] = now
        
        return True

# Example usage
if __name__ == "__main__":
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    # Simulate 10 requests from same client
    client_id = "client_123"
    for i in range(10):
        if limiter.allow_request(client_id):
            print(f"Request {i+1} allowed")
        else:
            print(f"Request {i+1} denied (rate limit exceeded)")
        time.sleep(0.1)  # Simulate time between requests
