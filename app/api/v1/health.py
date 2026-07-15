from fastapi import APIRouter
from sqlalchemy import text

from app.config.settings import get_settings
from app.dependencies.auth import SessionDep
from app.schemas.common import HealthResponse, VersionResponse
from app.utils.datetime import utc_now

router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check(session: SessionDep) -> HealthResponse:
    """Liveness and database connectivity check."""
    db_status = "healthy"
    try:
        await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    overall = "healthy" if db_status == "healthy" else "degraded"

    return HealthResponse(
        status=overall,
        timestamp=utc_now(),
        database=db_status,
    )


@router.get("/version", response_model=VersionResponse)
async def version_info() -> VersionResponse:
    """Return application version metadata."""
    return VersionResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        api_prefix=settings.api_v1_prefix,
    )
