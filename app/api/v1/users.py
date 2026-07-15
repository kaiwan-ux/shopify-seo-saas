from fastapi import APIRouter

from app.dependencies.auth import CurrentUserDep
from app.schemas.user import UserResponse

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
async def get_current_user_profile(current_user: CurrentUserDep) -> UserResponse:
    return UserResponse.model_validate(current_user)
