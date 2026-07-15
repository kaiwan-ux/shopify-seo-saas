"""OpenTelemetry and structured metrics for AI operations."""

import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from loguru import logger

from app.config.settings import get_settings


class AIMetrics:
    """In-process metrics collector for AI operations."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._timings: dict[str, list[int]] = {}

    def increment(self, metric: str, value: int = 1) -> None:
        self._counters[metric] = self._counters.get(metric, 0) + value

    def record_timing(self, metric: str, duration_ms: int) -> None:
        if metric not in self._timings:
            self._timings[metric] = []
        self._timings[metric].append(duration_ms)

    def get_summary(self) -> dict[str, Any]:
        timing_summary = {}
        for name, values in self._timings.items():
            if values:
                timing_summary[name] = {
                    "count": len(values),
                    "avg_ms": sum(values) / len(values),
                    "max_ms": max(values),
                    "min_ms": min(values),
                }
        return {"counters": dict(self._counters), "timings": timing_summary}


_metrics = AIMetrics()


def get_metrics() -> AIMetrics:
    return _metrics


def setup_telemetry() -> None:
    """Initialize OpenTelemetry if enabled."""
    settings = get_settings()
    if not settings.otel_enabled:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry initialized for service={}", settings.otel_service_name)
    except ImportError:
        logger.warning("OpenTelemetry packages not available")


@asynccontextmanager
async def trace_operation(
    operation: str, attributes: dict[str, Any] | None = None
) -> AsyncGenerator[None, None]:
    """Context manager for tracing AI operations."""
    settings = get_settings()
    start = time.perf_counter()
    _metrics.increment(f"{operation}.started")

    if settings.otel_enabled:
        try:
            from opentelemetry import trace
            tracer = trace.get_tracer(settings.otel_service_name)
            with tracer.start_as_current_span(operation, attributes=attributes or {}):
                yield
        except ImportError:
            yield
    else:
        yield

    duration_ms = int((time.perf_counter() - start) * 1000)
    _metrics.record_timing(operation, duration_ms)
    _metrics.increment(f"{operation}.completed")
    logger.debug("Operation {} completed in {}ms", operation, duration_ms)
