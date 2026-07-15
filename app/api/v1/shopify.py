from fastapi import APIRouter, Query, Request, status
from fastapi.responses import RedirectResponse

from app.dependencies.auth import CurrentUserDep, SessionDep
from app.dependencies.services import ShopifyServiceDep
from app.models.sync_log import SyncType
from app.repositories.collection import CollectionRepository
from app.repositories.page import PageRepository
from app.repositories.product import ProductRepository
from app.schemas.common import MessageResponse
from app.schemas.shopify import (
    CollectionListResponse,
    CollectionResponse,
    PageListResponse,
    PageResponse,
    ProductListResponse,
    ProductResponse,
    ShopifyConnectRequest,
    ShopifyConnectResponse,
    ShopifySyncRequest,
    StoreResponse,
    SyncLogResponse,
)

router = APIRouter()

@router.post(
    "/connect",
    response_model=ShopifyConnectResponse,
    summary="Initiate Shopify store connection via OAuth",
)
async def connect_shopify(
    data: ShopifyConnectRequest,
    current_user: CurrentUserDep,
    shopify_service: ShopifyServiceDep,
) -> ShopifyConnectResponse:
    result = await shopify_service.initiate_connection(current_user, data.shop_domain)
    return ShopifyConnectResponse(**result)


@router.get(
    "/callback",
    summary="Shopify OAuth callback (redirect from Shopify)",
    include_in_schema=True,
)
async def shopify_oauth_callback(
    request: Request,
    shopify_service: ShopifyServiceDep,
    code: str = Query(...),
    state: str = Query(...),
    shop: str = Query(...),
    hmac: str | None = Query(default=None),
):
    query_params = dict(request.query_params)
    hmac_valid = shopify_service.oauth.verify_hmac(query_params) if hmac else False

    store = await shopify_service.complete_connection(
        shop_domain=shop,
        code=code,
        state=state,
        hmac_valid=hmac_valid,
    )
    # Return success message instead of redirecting to non-existent frontend route
    from fastapi.responses import HTMLResponse
    return HTMLResponse(
        content=f"""
        <html>
            <head><title>Store Connected</title></head>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>✅ Store Connected Successfully!</h1>
                <p>Your Shopify store <strong>{store.shop_domain}</strong> has been connected.</p>
                <p>Store ID: {store.id}</p>
                <p><a href="{request.base_url}api/v1/docs">Go to API Docs</a></p>
            </body>
        </html>
        """,
        status_code=200,
    )


@router.get(
    "/store",
    response_model=StoreResponse,
    summary="Get the connected Shopify store for the current user",
)
async def get_connected_store(
    current_user: CurrentUserDep,
    shopify_service: ShopifyServiceDep,
) -> StoreResponse:
    store = await shopify_service.get_user_store(current_user)
    return StoreResponse.model_validate(store)


@router.post(
    "/disconnect",
    response_model=StoreResponse,
    summary="Disconnect the Shopify store",
)
async def disconnect_shopify(
    current_user: CurrentUserDep,
    shopify_service: ShopifyServiceDep,
) -> StoreResponse:
    store = await shopify_service.disconnect_store(current_user)
    return StoreResponse.model_validate(store)


@router.post(
    "/sync",
    response_model=SyncLogResponse,
    summary="Trigger a store data synchronization",
)
async def sync_shopify_store(
    data: ShopifySyncRequest,
    current_user: CurrentUserDep,
    shopify_service: ShopifyServiceDep,
) -> SyncLogResponse:
    sync_log = await shopify_service.trigger_sync(current_user, SyncType(data.sync_type))
    return SyncLogResponse.model_validate(sync_log)


@router.get(
    "/products",
    response_model=ProductListResponse,
    summary="List synced products for the connected store",
)
async def list_products(
    current_user: CurrentUserDep,
    shopify_service: ShopifyServiceDep,
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> ProductListResponse:
    store = await shopify_service.get_user_store(current_user)
    repo = ProductRepository(session)
    products = await repo.list_by_store(store.id, limit=limit)
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in products],
        total=len(products),
    )


@router.get(
    "/collections",
    response_model=CollectionListResponse,
    summary="List synced collections for the connected store",
)
async def list_collections(
    current_user: CurrentUserDep,
    shopify_service: ShopifyServiceDep,
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> CollectionListResponse:
    store = await shopify_service.get_user_store(current_user)
    repo = CollectionRepository(session)
    collections = await repo.list_by_store(store.id, limit=limit)
    return CollectionListResponse(
        items=[CollectionResponse.model_validate(c) for c in collections],
        total=len(collections),
    )


@router.get(
    "/pages",
    response_model=PageListResponse,
    summary="List synced pages for the connected store",
)
async def list_pages(
    current_user: CurrentUserDep,
    shopify_service: ShopifyServiceDep,
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
) -> PageListResponse:
    store = await shopify_service.get_user_store(current_user)
    repo = PageRepository(session)
    pages = await repo.list_by_store(store.id, limit=limit)
    return PageListResponse(
        items=[PageResponse.model_validate(p) for p in pages],
        total=len(pages),
    )


@router.post(
    "/webhooks",
    response_model=MessageResponse,
    summary="Shopify webhook receiver",
    include_in_schema=False,
)
async def shopify_webhook(
    request: Request,
    shopify_service: ShopifyServiceDep,
) -> MessageResponse:
    body = await request.body()
    topic = request.headers.get("X-Shopify-Topic", "")
    shop_domain = request.headers.get("X-Shopify-Shop-Domain", "")
    hmac_header = request.headers.get("X-Shopify-Hmac-Sha256")
    webhook_id = request.headers.get("X-Shopify-Webhook-Id")

    result = await shopify_service.webhook_handler.handle(
        topic=topic,
        shop_domain=shop_domain,
        body=body,
        hmac_header=hmac_header,
        webhook_id=webhook_id,
    )
    return MessageResponse(message=f"Webhook {result['status']}: {result['topic']}")
