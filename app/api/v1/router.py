from fastapi import APIRouter

from app.api.v1.ai import router as ai_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.seo import router as seo_router
from app.api.v1.shopify import router as shopify_router
from app.api.v1.users import router as users_router
from app.config.settings import get_settings

settings = get_settings()

api_v1_router = APIRouter(prefix=settings.api_v1_prefix)

api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(users_router, prefix="/users", tags=["Users"])
api_v1_router.include_router(shopify_router, prefix="/shopify", tags=["Shopify"])
api_v1_router.include_router(ai_router, prefix="/ai", tags=["AI"])
api_v1_router.include_router(seo_router, prefix="/seo", tags=["SEO Intelligence"])
