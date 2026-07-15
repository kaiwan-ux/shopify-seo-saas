"""Phase 4 SEO intelligence HTTP API."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.core.exceptions import NotFoundError
from app.dependencies.auth import CurrentUserDep, SessionDep
from app.dependencies.services import ShopifyServiceDep
from app.intelligence import InternalLinkingEngine, KeywordIntelligenceEngine
from app.repositories.seo import SEOReportRepository
from app.repositories.store import StoreRepository
from app.schemas.seo import (
    AuditRequest,
    ContentRequest,
    InternalLinkRequest,
    KeywordRequest,
    MetadataRequest,
    RedirectRequest,
    SchemaRequest,
    ScoreRequest,
    TechnicalAuditRequest,
)
from app.services.seo import SEOService

router = APIRouter()


async def _resolve_store(current_user, store_id, session, shopify_service):
    if store_id:
        store = await StoreRepository(session).get_by_id(store_id)
        if store is None or store.owner_id != current_user.id:
            raise NotFoundError("Store not found")
        return store
    return await shopify_service.get_user_store(current_user)


@router.post("/audit", summary="Run a complete on-page SEO audit")
async def audit(
    data: AuditRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
    shopify_service: ShopifyServiceDep,
):
    store = await _resolve_store(current_user, data.store_id, session, shopify_service)
    return await SEOService(session).audit(data, store.id)


@router.post("/technical", summary="Run a technical SEO audit")
async def technical(
    data: TechnicalAuditRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
    shopify_service: ShopifyServiceDep,
):
    store = await _resolve_store(current_user, data.store_id, session, shopify_service)
    return await SEOService(session).technical(data, store.id)


@router.post("/content", summary="Generate intent-aware SEO content")
async def content(
    data: ContentRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
    shopify_service: ShopifyServiceDep,
    store_id: Annotated[UUID | None, Query()] = None,
):
    store = await _resolve_store(current_user, store_id, session, shopify_service)
    return await SEOService(session).content(data, store.id)


@router.post("/schema", summary="Generate and validate Schema.org JSON-LD")
async def schema(
    data: SchemaRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
    shopify_service: ShopifyServiceDep,
    store_id: Annotated[UUID | None, Query()] = None,
):
    store = await _resolve_store(current_user, store_id, session, shopify_service)
    return await SEOService(session).schema(data, store.id)


@router.post("/redirect", summary="Recommend semantically relevant redirects")
async def redirect(
    data: RedirectRequest,
    current_user: CurrentUserDep,
    session: SessionDep,
    shopify_service: ShopifyServiceDep,
):
    store = await _resolve_store(current_user, data.store_id, session, shopify_service)
    return await SEOService(session).redirect(data, store.id)


@router.post("/score", summary="Calculate a configurable SEO score")
async def score(data: ScoreRequest, current_user: CurrentUserDep, session: SessionDep):
    return await SEOService(session).score(data)


@router.post("/metadata", summary="Generate search and social metadata")
async def metadata(data: MetadataRequest, current_user: CurrentUserDep, session: SessionDep):
    return await SEOService(session).metadata_engine.generate(data)


@router.post("/keywords", summary="Analyze keyword usage and search intent")
async def keywords(data: KeywordRequest, current_user: CurrentUserDep):
    return await KeywordIntelligenceEngine().analyze(data)


@router.post("/links", summary="Analyze internal linking and topic clusters")
async def links(data: InternalLinkRequest, current_user: CurrentUserDep):
    return await InternalLinkingEngine().analyze(data)


@router.get("/report/{report_id}", summary="Get a persisted SEO report")
async def get_report(
    report_id: UUID,
    current_user: CurrentUserDep,
    session: SessionDep,
):
    report = await SEOReportRepository(session).get_complete(report_id)
    if report is None:
        raise NotFoundError("SEO report not found")
    store = await StoreRepository(session).get_by_id(report.store_id)
    if store is None or store.owner_id != current_user.id:
        raise NotFoundError("SEO report not found")
    result = await SEOService(session).get_report(report_id, report.store_id)
    if result is None:
        raise NotFoundError("SEO report not found")
    return result
