"""Search, social, canonical, and rich-result metadata generation."""

from app.intelligence.utils import strip_html, truncate_at_word
from app.schemas.seo import MetadataRequest, MetadataResult, ResourceType


class MetadataIntelligenceEngine:
    TITLE_MAX = 60
    DESCRIPTION_MAX = 160

    async def generate(self, request: MetadataRequest) -> MetadataResult:
        resource = request.resource
        keyword = request.primary_keyword or (
            resource.keywords[0] if resource.keywords else resource.title
        )
        brand = request.brand_name or _brand_from_resource(resource)
        base_title = _build_distinct_title(resource.title, keyword, brand, resource.resource_type)
        seo_title = truncate_at_word(base_title, self.TITLE_MAX)

        source = strip_html(resource.body)
        if source:
            description = truncate_at_word(source, 157)
        else:
            description = f"Explore {resource.title}. Find useful details, features and options to help you choose."
        if len(description) < 70:
            description = truncate_at_word(
                f"{description} Shop with confidence and discover the option that fits your needs.",
                self.DESCRIPTION_MAX,
            )

        canonical = resource.canonical_url or resource.url
        image = resource.images[0].url if resource.images else ""
        rich_type = {
            ResourceType.PRODUCT: "Product",
            ResourceType.BLOG: "Article",
            ResourceType.COLLECTION: "CollectionPage",
        }.get(resource.resource_type, "WebPage")
        rich = {
            "@context": "https://schema.org",
            "@type": rich_type,
            "name": resource.title,
            "url": canonical,
            "description": description,
        }
        if image:
            rich["image"] = image

        warnings = []
        if len(seo_title) < 30:
            warnings.append("Generated title is shorter than the usual 30–60 character target.")
        if len(description) < 120:
            warnings.append(
                "Generated description is shorter than the usual 120–160 character target."
            )
        return MetadataResult(
            seo_title=seo_title,
            meta_description=description,
            open_graph={
                "og:type": "product"
                if resource.resource_type == ResourceType.PRODUCT
                else "website",
                "og:title": seo_title,
                "og:description": description,
                "og:url": canonical,
                **({"og:image": image} if image else {}),
            },
            twitter_card={
                "twitter:card": "summary_large_image" if image else "summary",
                "twitter:title": seo_title,
                "twitter:description": description,
                **({"twitter:image": image} if image else {}),
            },
            canonical_tag=f'<link rel="canonical" href="{canonical}">',
            rich_snippet=rich,
            warnings=warnings,
            confidence=0.9 if source else 0.72,
        )


def _brand_from_resource(resource) -> str:
    vendor = resource.metadata.get("vendor") if isinstance(resource.metadata, dict) else None
    return str(vendor or "").strip()


def _build_distinct_title(title: str, keyword: str, brand: str, resource_type: ResourceType) -> str:
    clean_title = " ".join((title or keyword).split())
    clean_keyword = " ".join((keyword or clean_title).split())
    clean_brand = " ".join((brand or "").split())

    if clean_brand and clean_brand.lower() not in clean_title.lower():
        candidate = f"{clean_title} | {clean_brand}"
    elif resource_type == ResourceType.COLLECTION:
        candidate = f"{clean_title} Collection | Shop Products"
    elif resource_type == ResourceType.PRODUCT:
        candidate = f"{clean_title} | Details & Options"
    else:
        candidate = f"{clean_title} | Store Guide"

    if candidate.strip().lower() == clean_title.lower():
        candidate = f"{clean_title} | Shop Online"

    if len(candidate) < 30 and clean_keyword.lower() not in candidate.lower():
        candidate = f"{candidate} - {clean_keyword}"
    return candidate
