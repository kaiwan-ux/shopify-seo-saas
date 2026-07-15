from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ShopifyConnectRequest(BaseModel):
    """Initiate Shopify OAuth connection."""

    shop_domain: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Shop domain (e.g. my-store or my-store.myshopify.com)",
        examples=["my-store.myshopify.com"],
    )


class ShopifyConnectResponse(BaseModel):
    """OAuth authorization URL response."""

    authorization_url: str
    state: str
    shop_domain: str


class StoreResponse(BaseModel):
    """Connected Shopify store response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    shop_domain: str
    shop_name: str | None
    shopify_shop_id: str | None
    is_connected: bool
    sync_status: str
    scopes: str | None
    installed_at: datetime | None
    last_sync_at: datetime | None
    last_sync_error: str | None
    created_at: datetime
    updated_at: datetime


class ShopifySyncRequest(BaseModel):
    """Trigger a store sync."""

    sync_type: str = Field(
        default="full",
        pattern="^(full|products|collections|pages|blogs|redirects)$",
    )


class SyncLogResponse(BaseModel):
    """Sync job result."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    store_id: UUID
    sync_type: str
    status: str
    records_processed: int
    records_failed: int
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    store_id: UUID
    shopify_id: str
    title: str
    handle: str
    description: str | None
    status: str | None
    vendor: str | None
    product_type: str | None
    seo_title: str | None
    seo_description: str | None
    synced_at: datetime | None
    is_deleted: bool


class CollectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    store_id: UUID
    shopify_id: str
    title: str
    handle: str
    description: str | None
    seo_title: str | None
    seo_description: str | None
    products_count: int | None
    synced_at: datetime | None


class PageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    store_id: UUID
    shopify_id: str
    title: str
    handle: str
    body_html: str | None
    seo_title: str | None
    seo_description: str | None
    is_published: bool
    synced_at: datetime | None


class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int


class CollectionListResponse(BaseModel):
    items: list[CollectionResponse]
    total: int


class PageListResponse(BaseModel):
    items: list[PageResponse]
    total: int
