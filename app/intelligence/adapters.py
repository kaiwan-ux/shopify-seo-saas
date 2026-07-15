"""Adapters between Phase 2 Shopify payloads and Phase 4 engine contracts."""

from typing import Any

from app.schemas.seo import ImageInput, ResourceType, SEOResource


def resources_from_store_data(store_data: dict[str, Any]) -> list[SEOResource]:
    resources: list[SEOResource] = []
    mapping = (
        ("products", ResourceType.PRODUCT),
        ("collections", ResourceType.COLLECTION),
        ("pages", ResourceType.PAGE),
        ("blogs", ResourceType.BLOG),
    )
    for key, resource_type in mapping:
        values = store_data.get(key, [])
        if isinstance(values, dict):
            values = values.get(key, values.get("items", []))
        for index, item in enumerate(values or []):
            if not isinstance(item, dict):
                continue
            raw_images = item.get("images") or []
            images = [
                ImageInput(
                    url=image.get("url") or image.get("src") or "",
                    alt=image.get("alt") or image.get("altText"),
                )
                for image in raw_images
                if isinstance(image, dict) and (image.get("url") or image.get("src"))
            ]
            title = str(
                item.get("title") or item.get("name") or f"{resource_type.value} {index + 1}"
            )
            handle = str(item.get("handle") or item.get("id") or index)
            url = str(
                item.get("url") or item.get("onlineStoreUrl") or f"/{resource_type.value}s/{handle}"
            )
            seo = item.get("seo") if isinstance(item.get("seo"), dict) else {}
            resources.append(
                SEOResource(
                    id=str(item.get("id") or item.get("shopify_id") or handle),
                    resource_type=resource_type,
                    url=url,
                    title=title,
                    body=str(
                        item.get("descriptionHtml")
                        or item.get("description")
                        or item.get("body_html")
                        or item.get("body")
                        or ""
                    ),
                    seo_title=item.get("seo_title") or seo.get("title"),
                    meta_description=item.get("seo_description") or seo.get("description"),
                    canonical_url=item.get("canonical_url"),
                    headings=[title] if title else [],
                    images=images,
                    keywords=list(item.get("tags") or []),
                    published=not bool(item.get("is_deleted", False)),
                    indexable=str(item.get("status", "active")).lower()
                    not in {"draft", "archived"},
                    metadata=item,
                )
            )
    return resources
