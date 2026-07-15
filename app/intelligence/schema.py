"""Schema.org JSON-LD generation with explicit type-specific validation."""

from datetime import UTC, datetime
from typing import Any

from app.schemas.seo import SchemaRequest, SchemaResult, SchemaType

REQUIRED_FIELDS: dict[SchemaType, tuple[str, ...]] = {
    SchemaType.PRODUCT: ("name",),
    SchemaType.ORGANIZATION: ("name", "url"),
    SchemaType.FAQ: ("questions",),
    SchemaType.REVIEW: ("itemReviewed", "reviewRating", "author"),
    SchemaType.BREADCRUMB: ("items",),
    SchemaType.ARTICLE: ("headline", "author", "datePublished"),
    SchemaType.COLLECTION: ("name", "url"),
    SchemaType.VIDEO: ("name", "description", "thumbnailUrl", "uploadDate"),
    SchemaType.LOCAL_BUSINESS: ("name", "address"),
}


class SchemaIntelligenceEngine:
    async def generate(self, request: SchemaRequest) -> SchemaResult:
        data = dict(request.data)
        errors = [
            f"Missing required field: {field}"
            for field in REQUIRED_FIELDS[request.schema_type]
            if data.get(field) in (None, "", [])
        ]
        warnings: list[str] = []
        schema = self._build(request.schema_type, data)

        if request.schema_type == SchemaType.PRODUCT and not data.get("offers"):
            warnings.append(
                "Product markup should include Offer data when price and availability are shown."
            )
        if (
            request.schema_type == SchemaType.FAQ
            and data.get("questions")
            and len(data["questions"]) < 2
        ):
            warnings.append("FAQ markup is valid, but a single question provides limited value.")
        if request.schema_type in {SchemaType.ARTICLE, SchemaType.VIDEO}:
            for key in ("datePublished", "uploadDate"):
                if data.get(key) and not self._valid_date(str(data[key])):
                    errors.append(f"{key} must use ISO 8601 format")
        return SchemaResult(
            schema_type=request.schema_type,
            json_ld=schema,
            valid=not errors,
            errors=errors,
            warnings=warnings,
            confidence=0.99 if not errors else 0.75,
        )

    def validate(self, schema: dict[str, Any]) -> tuple[bool, list[str]]:
        errors = []
        if schema.get("@context") != "https://schema.org":
            errors.append("@context must be https://schema.org")
        raw_type = schema.get("@type")
        try:
            schema_type = SchemaType(raw_type)
        except ValueError:
            return False, [*errors, f"Unsupported @type: {raw_type}"]
        for field in REQUIRED_FIELDS[schema_type]:
            mapped = {"questions": "mainEntity", "items": "itemListElement"}.get(field, field)
            if schema.get(mapped) in (None, "", []):
                errors.append(f"Missing required property: {mapped}")
        return not errors, errors

    @staticmethod
    def _build(schema_type: SchemaType, data: dict[str, Any]) -> dict[str, Any]:
        schema: dict[str, Any] = {"@context": "https://schema.org", "@type": schema_type.value}
        if schema_type == SchemaType.FAQ:
            schema["mainEntity"] = [
                {
                    "@type": "Question",
                    "name": item.get("question", ""),
                    "acceptedAnswer": {"@type": "Answer", "text": item.get("answer", "")},
                }
                for item in data.pop("questions", [])
            ]
        elif schema_type == SchemaType.BREADCRUMB:
            schema["itemListElement"] = [
                {
                    "@type": "ListItem",
                    "position": index,
                    "name": item.get("name", ""),
                    "item": item.get("url", ""),
                }
                for index, item in enumerate(data.pop("items", []), start=1)
            ]
        schema.update({key: value for key, value in data.items() if value is not None})
        return schema

    @staticmethod
    def _valid_date(value: str) -> bool:
        try:
            datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
            return True
        except ValueError:
            return False
