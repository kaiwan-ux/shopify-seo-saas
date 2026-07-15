import sys

from loguru import logger

from app.config.settings import Settings


def setup_logging(settings: Settings) -> None:
    """Configure Loguru logging for the application."""
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    if settings.log_json:
        log_format = (
            '{{"time":"{time:YYYY-MM-DD HH:mm:ss.SSS}",'
            '"level":"{level}",'
            '"message":"{message}",'
            '"module":"{module}",'
            '"function":"{function}",'
            '"line":{line}}}'
        )

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level.upper(),
        colorize=not settings.log_json,
        backtrace=settings.debug,
        diagnose=settings.debug,
    )

    logger.info(
        "Logging configured — env={} level={}",
        settings.app_env,
        settings.log_level.upper(),
    )
