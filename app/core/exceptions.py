from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from loguru import logger
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    detail: str
    error_code: str | None = None
    errors: list[dict[str, Any]] | None = None


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, message: str = "Resource not found", error_code: str = "NOT_FOUND") -> None:
        super().__init__(message, status.HTTP_404_NOT_FOUND, error_code)


class ConflictError(AppException):
    """Resource conflict (e.g., duplicate email)."""

    def __init__(
        self, message: str = "Resource already exists", error_code: str = "CONFLICT"
    ) -> None:
        super().__init__(message, status.HTTP_409_CONFLICT, error_code)


class UnauthorizedError(AppException):
    """Authentication failed."""

    def __init__(
        self, message: str = "Could not validate credentials", error_code: str = "UNAUTHORIZED"
    ) -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, error_code)


class ForbiddenError(AppException):
    """Authorization failed."""

    def __init__(self, message: str = "Forbidden", error_code: str = "FORBIDDEN") -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN, error_code)


class IntegrationError(AppException):
    """External integration failure (Shopify, MCP)."""

    def __init__(
        self,
        message: str = "Integration error",
        error_code: str = "INTEGRATION_ERROR",
        status_code: int = status.HTTP_502_BAD_GATEWAY,
    ) -> None:
        super().__init__(message, status_code, error_code)


class ShopifyAuthError(IntegrationError):
    """Shopify authentication or authorization failure."""

    def __init__(
        self, message: str = "Shopify authentication failed", error_code: str = "SHOPIFY_AUTH_ERROR"
    ) -> None:
        super().__init__(message, error_code, status.HTTP_401_UNAUTHORIZED)


class ShopifyPermissionError(AppException):
    """Shopify token is valid but missing permission for a requested Admin API field."""

    def __init__(
        self,
        message: str = "Shopify permission denied",
        error_code: str = "SHOPIFY_PERMISSION_DENIED",
    ) -> None:
        super().__init__(message, status.HTTP_403_FORBIDDEN, error_code)


class WebhookVerificationError(AppException):
    """Invalid webhook signature."""

    def __init__(
        self, message: str = "Invalid webhook signature", error_code: str = "WEBHOOK_INVALID"
    ) -> None:
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, error_code)


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.warning("AppException: {} ({})", exc.message, exc.error_code)
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=exc.message, error_code=exc.error_code).model_dump(),
    )


async def http_exception_handler(_request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette/FastAPI HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(detail=str(exc.detail)).model_dump(),
    )


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = [
        {
            "field": ".".join(str(loc) for loc in err["loc"]),
            "message": err["msg"],
            "type": err["type"],
        }
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            detail="Validation error",
            error_code="VALIDATION_ERROR",
            errors=errors,
        ).model_dump(),
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception("Unhandled exception: {}", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail="Internal server error",
            error_code="INTERNAL_ERROR",
        ).model_dump(),
    )
