"""Retry logic for connector operations."""

import asyncio
import logging
from typing import Callable, TypeVar, Any
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry logic."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """Initialize retry configuration.

        Args:
            max_attempts: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
        """

        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        """Get delay for given attempt number.

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            float: Delay in seconds
        """

        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        if self.jitter:
            import random
            delay *= (0.5 + random.random())

        return delay


class RetryableError(Exception):
    """Exception that can be retried."""

    pass


def retry_on_exception(
    config: RetryConfig = None,
    retryable_exceptions: tuple = (RetryableError, Exception),
):
    """Decorator for retrying async functions.

    Args:
        config: Retry configuration
        retryable_exceptions: Tuple of exceptions to retry on
    """

    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    logger.debug(f"Attempt {attempt + 1}/{config.max_attempts} for {func.__name__}")
                    return await func(*args, **kwargs)

                except retryable_exceptions as e:
                    last_exception = e

                    if attempt < config.max_attempts - 1:
                        delay = config.get_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.2f} seconds..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {config.max_attempts} attempts failed for {func.__name__}: {e}"
                        )

            raise last_exception

        return wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker for preventing cascading failures."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting to close circuit
        """

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    def record_success(self) -> None:
        """Record successful operation."""

        self.failure_count = 0
        self.state = "closed"

    def record_failure(self) -> None:
        """Record failed operation."""

        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def is_available(self) -> bool:
        """Check if circuit breaker allows operations.

        Returns:
            bool: True if operation can proceed, False otherwise
        """

        if self.state == "closed":
            return True

        if self.state == "open":
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = "half-open"
                    logger.info("Circuit breaker entering half-open state")
                    return True
            return False

        # Half-open state - allow operation
        return True

    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker.

        Args:
            func: Function to wrap

        Returns:
            Callable: Wrapped function
        """

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            if not self.is_available():
                raise RetryableError("Circuit breaker is open")

            try:
                result = await func(*args, **kwargs)
                self.record_success()
                return result
            except Exception as e:
                self.record_failure()
                raise

        return wrapper


class RateLimiter:
    """Rate limiter for API calls."""

    def __init__(self, max_requests: int, window_seconds: float):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []

    async def acquire(self) -> None:
        """Acquire rate limit token.

        Blocks until token is available.
        """

        while True:
            now = datetime.utcnow()
            window_start = now - timedelta(seconds=self.window_seconds)

            # Remove old requests outside window
            self.requests = [
                req_time for req_time in self.requests
                if req_time > window_start
            ]

            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return

            # Wait before retrying
            await asyncio.sleep(0.1)

    def __call__(self, func: Callable) -> Callable:
        """Decorator for rate limiting.

        Args:
            func: Function to wrap

        Returns:
            Callable: Wrapped function
        """

        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            await self.acquire()
            return await func(*args, **kwargs)

        return wrapper
