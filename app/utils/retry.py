"""Async retry helpers built on tenacity."""

from collections.abc import Awaitable, Callable
from typing import TypeVar

from loguru import logger
from tenacity import (
    AsyncRetrying,
    RetryError,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

T = TypeVar("T")


async def with_retry(
    operation: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    min_wait: float = 1.0,
    max_wait: float = 10.0,
    retry_on: tuple[type[Exception], ...] = (Exception,),
    operation_name: str = "operation",
) -> T:
    """Execute an async operation with exponential backoff retry."""
    try:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=min_wait, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(retry_on),
            reraise=True,
        ):
            with attempt:
                return await operation()
    except RetryError as exc:
        logger.error("{} failed after {} attempts", operation_name, max_attempts)
        raise exc.last_attempt.exception() from exc

    raise RuntimeError(f"{operation_name} retry loop exited unexpectedly")
