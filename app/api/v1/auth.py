from fastapi import APIRouter, status

from app.dependencies.services import AuthServiceDep
from app.schemas.auth import TokenRefreshRequest, TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(data: UserCreate, auth_service: AuthServiceDep) -> UserResponse:
    user = await auth_service.register(data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT tokens",
)
async def login(data: UserLogin, auth_service: AuthServiceDep) -> TokenResponse:
    _, tokens = await auth_service.login(data)
    return tokens


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using a refresh token",
)
async def refresh_token(
    data: TokenRefreshRequest,
    auth_service: AuthServiceDep,
) -> TokenResponse:
    return await auth_service.refresh_tokens(data.refresh_token)
