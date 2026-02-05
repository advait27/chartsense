"""
Rate Limiter for Chartered

Simple in-memory rate limiter to prevent API abuse.

Author: Chartered
Version: 1.0.0
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    max_requests: int = 10  # Maximum requests
    time_window: int = 60   # Time window in seconds
    block_duration: int = 300  # Block duration in seconds after exceeding limit


class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    Tracks requests by identifier (e.g., IP address) and enforces limits.
    For production, consider using Redis for distributed rate limiting.
    """
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        """
        Initialize rate limiter.
        
        Args:
            config: Rate limit configuration
        """
        self.config = config or RateLimitConfig()
        self.request_log: Dict[str, list] = defaultdict(list)
        self.blocked_until: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)
    
    def is_allowed(self, identifier: str) -> tuple[bool, Optional[str]]:
        """
        Check if request is allowed for identifier.
        
        Args:
            identifier: Unique identifier (e.g., IP address, user ID)
            
        Returns:
            Tuple of (is_allowed, reason_if_blocked)
        """
        current_time = time.time()
        
        # Check if currently blocked
        if identifier in self.blocked_until:
            if current_time < self.blocked_until[identifier]:
                remaining = int(self.blocked_until[identifier] - current_time)
                self.logger.warning(f"Blocked request from {identifier}, {remaining}s remaining")
                return False, f"Rate limit exceeded. Try again in {remaining} seconds."
            else:
                # Block expired, remove from blocked list
                del self.blocked_until[identifier]
                self.request_log[identifier] = []
        
        # Clean old requests outside time window
        cutoff_time = current_time - self.config.time_window
        self.request_log[identifier] = [
            req_time for req_time in self.request_log[identifier]
            if req_time > cutoff_time
        ]
        
        # Check if limit exceeded
        if len(self.request_log[identifier]) >= self.config.max_requests:
            # Block the identifier
            self.blocked_until[identifier] = current_time + self.config.block_duration
            self.logger.warning(
                f"Rate limit exceeded for {identifier}. "
                f"Blocked for {self.config.block_duration}s"
            )
            return False, (
                f"Rate limit exceeded. Maximum {self.config.max_requests} requests "
                f"per {self.config.time_window} seconds. "
                f"Blocked for {self.config.block_duration} seconds."
            )
        
        # Allow request and log it
        self.request_log[identifier].append(current_time)
        return True, None
    
    def get_remaining_requests(self, identifier: str) -> int:
        """
        Get remaining requests for identifier in current window.
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Number of remaining requests
        """
        current_time = time.time()
        cutoff_time = current_time - self.config.time_window
        
        # Clean old requests
        self.request_log[identifier] = [
            req_time for req_time in self.request_log[identifier]
            if req_time > cutoff_time
        ]
        
        current_count = len(self.request_log[identifier])
        return max(0, self.config.max_requests - current_count)
    
    def reset(self, identifier: Optional[str] = None):
        """
        Reset rate limit for identifier or all identifiers.
        
        Args:
            identifier: Specific identifier to reset, or None to reset all
        """
        if identifier:
            if identifier in self.request_log:
                del self.request_log[identifier]
            if identifier in self.blocked_until:
                del self.blocked_until[identifier]
            self.logger.info(f"Rate limit reset for {identifier}")
        else:
            self.request_log.clear()
            self.blocked_until.clear()
            self.logger.info("Rate limit reset for all identifiers")


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter(config: Optional[RateLimitConfig] = None) -> RateLimiter:
    """
    Get global rate limiter instance.
    
    Args:
        config: Optional configuration (only used on first call)
        
    Returns:
        RateLimiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(config)
    return _rate_limiter


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create rate limiter with custom config
    config = RateLimitConfig(
        max_requests=5,
        time_window=10,
        block_duration=30
    )
    limiter = RateLimiter(config)
    
    # Simulate requests
    test_user = "user123"
    
    print(f"Testing rate limiter (max {config.max_requests} requests per {config.time_window}s)")
    print("=" * 60)
    
    for i in range(8):
        allowed, reason = limiter.is_allowed(test_user)
        remaining = limiter.get_remaining_requests(test_user)
        
        if allowed:
            print(f"Request {i+1}: ✅ Allowed (remaining: {remaining})")
            time.sleep(0.5)
        else:
            print(f"Request {i+1}: ❌ Blocked - {reason}")
    
    print("\nWaiting for time window to pass...")
    time.sleep(11)
    
    allowed, reason = limiter.is_allowed(test_user)
    if allowed:
        print("Request after wait: ✅ Allowed - limit reset")
