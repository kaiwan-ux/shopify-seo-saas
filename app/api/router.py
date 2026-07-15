from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from app.api.v1.router import api_v1_router

api_router = APIRouter()
api_router.include_router(api_v1_router)


@api_router.get("/")
async def root():
    """Redirect root to API docs."""
    return RedirectResponse(url="/api/v1/docs")
