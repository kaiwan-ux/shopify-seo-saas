"""On-page and content SEO audit rules for Shopify resources."""

from collections import defaultdict

from app.intelligence.utils import SEOHTMLParser, strip_html, words
from app.schemas.seo import (
    AuditRequest,
    AuditResult,
    Evidence,
    ResourceType,
    SEOFinding,
    Severity,
)


class SEOAuditEngine:
    """Run explainable checks; every finding carries evidence and a confidence."""

    async def analyze(self, request: AuditRequest) -> AuditResult:
        findings: list[SEOFinding] = []
        title_map: dict[str, list] = defaultdict(list)
        body_map: dict[str, list] = defaultdict(list)

        for resource in request.resources:
            text = strip_html(resource.body)
            parser = SEOHTMLParser()
            parser.feed(resource.body)
            images = [*resource.images]
            links = [*resource.links]

            title_map[(resource.seo_title or resource.title).strip().lower()].append(resource)
            if len(text) > 40:
                body_map[text[:500].lower()].append(resource)

            if resource.resource_type != ResourceType.PAGE:
                effective_title = (resource.seo_title or resource.title or "").strip()
                if not effective_title:
                    findings.append(
                        self._finding(
                            "metadata.missing_title",
                            "metadata",
                            Severity.HIGH,
                            resource,
                            "Missing SEO title",
                            "No SEO title or usable page title is set.",
                            "Add a unique, descriptive SEO title of roughly 30-60 characters.",
                            None,
                            "A populated SEO title or page title",
                        )
                    )
                elif not resource.seo_title and len(effective_title) < 30:
                    findings.append(
                        self._finding(
                            "metadata.title_fallback_short",
                            "metadata",
                            Severity.MEDIUM,
                            resource,
                            "SEO title uses short title fallback",
                            "Shopify is using the normal title as the search title, but it is shorter than the usual target range.",
                            "Add a distinct SEO title of roughly 30-60 characters.",
                            len(effective_title),
                            "30-60 characters",
                        )
                    )
                elif resource.seo_title and not 30 <= len(resource.seo_title) <= 60:
                    findings.append(
                        self._finding(
                            "metadata.title_length",
                            "metadata",
                            Severity.MEDIUM,
                            resource,
                            "SEO title length is suboptimal",
                            "The title may truncate or communicate too little in search results.",
                            "Rewrite the title to roughly 30-60 characters without keyword stuffing.",
                            len(resource.seo_title),
                            "30-60 characters",
                        )
                    )

                if not resource.meta_description:
                    findings.append(
                        self._finding(
                            "metadata.missing_description",
                            "metadata",
                            Severity.HIGH,
                            resource,
                            "Missing meta description",
                            "Search engines must create their own snippet.",
                            "Write a unique, persuasive description of roughly 120–160 characters.",
                            None,
                            "A unique meta description",
                        )
                    )
                elif not 120 <= len(resource.meta_description) <= 160:
                    findings.append(
                        self._finding(
                            "metadata.description_length",
                            "metadata",
                            Severity.LOW,
                            resource,
                            "Meta description length is suboptimal",
                            "The search snippet may truncate or leave useful space unused.",
                            "Keep the description around 120–160 characters.",
                            len(resource.meta_description),
                            "120–160 characters",
                        )
                    )

            minimum_words = {
                ResourceType.PRODUCT: 100,
                ResourceType.COLLECTION: 150,
                ResourceType.BLOG: 300,
                ResourceType.PAGE: 150,
            }.get(resource.resource_type, 50)
            if len(words(text)) < minimum_words:
                severity = Severity.HIGH if not text else Severity.MEDIUM
                findings.append(
                    self._finding(
                        "content.missing" if not text else "content.thin",
                        "content_quality",
                        severity,
                        resource,
                        "Missing content" if not text else "Thin content",
                        f"The page contains {len(words(text))} words; comparable "
                        f"{resource.resource_type.value} pages generally need substantive unique copy.",
                        "Add useful, intent-matched copy that answers customer questions; do not pad text.",
                        len(words(text)),
                        f"At least {minimum_words} useful words",
                    )
                )

            h1_count = sum(1 for tag, _ in parser.headings if tag == "h1")
            if resource.headings:
                h1_count = sum(1 for heading in resource.headings if heading.strip())
            if h1_count == 0:
                findings.append(
                    self._finding(
                        "headings.missing_h1",
                        "content_quality",
                        Severity.MEDIUM,
                        resource,
                        "Missing primary heading",
                        "No clear H1 was found.",
                        "Add one descriptive H1 that represents the page's primary topic.",
                        0,
                        1,
                    )
                )
            elif h1_count > 1:
                findings.append(
                    self._finding(
                        "headings.multiple_h1",
                        "content_quality",
                        Severity.LOW,
                        resource,
                        "Multiple primary headings",
                        f"{h1_count} H1-equivalent headings were found.",
                        "Use one clear primary heading and organize subsections with H2/H3 headings.",
                        h1_count,
                        1,
                    )
                )

            image_data = [
                *({"url": image.url, "alt": image.alt or ""} for image in images),
                *parser.images,
            ]
            for image in image_data:
                if not image["alt"].strip():
                    findings.append(
                        self._finding(
                            "accessibility.missing_alt",
                            "accessibility",
                            Severity.MEDIUM,
                            resource,
                            "Image is missing ALT text",
                            "An informative image has no text alternative for search or assistive technology.",
                            "Add concise, contextual ALT text; leave it empty only for decorative images.",
                            image["url"],
                            "Descriptive ALT text",
                            resource_type=ResourceType.IMAGE,
                        )
                    )

            for link in links:
                if link.status_code and link.status_code >= 400:
                    findings.append(
                        self._finding(
                            "links.broken",
                            "internal_linking",
                            Severity.HIGH,
                            resource,
                            "Broken link",
                            f"The link returns HTTP {link.status_code}.",
                            "Update, remove, or redirect the broken destination.",
                            link.status_code,
                            "HTTP 200",
                            url=link.url,
                        )
                    )

            if resource.canonical_url and resource.canonical_url.rstrip("/") != resource.url.rstrip(
                "/"
            ):
                findings.append(
                    self._finding(
                        "canonical.non_self",
                        "technical",
                        Severity.MEDIUM,
                        resource,
                        "Canonical points to another URL",
                        "The declared canonical differs from this resource URL.",
                        "Confirm this page is a duplicate; otherwise use a self-referencing canonical.",
                        resource.canonical_url,
                        resource.url,
                    )
                )

        for duplicate_type, mapping in (("title", title_map), ("content", body_map)):
            for value, resources in mapping.items():
                if value and len(resources) > 1:
                    for resource in resources:
                        findings.append(
                            self._finding(
                                f"duplicate.{duplicate_type}",
                                "content_quality",
                                Severity.HIGH,
                                resource,
                                f"Duplicate {duplicate_type}",
                                f"The same {duplicate_type} occurs on {len(resources)} resources.",
                                f"Make this page's {duplicate_type} distinct and aligned with its unique intent.",
                                value[:160],
                                "Unique value",
                            )
                        )

        findings = self._dedupe_findings(findings)
        confidence = 0.98 if request.resources else 0.3
        return AuditResult(
            findings=findings,
            resources_analyzed=len(request.resources),
            summary=f"Analyzed {len(request.resources)} resources and found {len(findings)} unique issues.",
            confidence=confidence,
        )

    @staticmethod
    def _dedupe_findings(findings: list[SEOFinding]) -> list[SEOFinding]:
        seen: set[tuple] = set()
        unique: list[SEOFinding] = []
        for item in findings:
            observed = item.evidence[0].observed if item.evidence else None
            key = (
                item.code,
                item.resource_type.value,
                item.resource_id,
                item.url,
                str(observed)[:120],
            )
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique

    @staticmethod
    def _finding(
        code: str,
        category: str,
        severity: Severity,
        resource,
        title: str,
        explanation: str,
        action: str,
        observed,
        expected,
        *,
        resource_type: ResourceType | None = None,
        url: str | None = None,
    ) -> SEOFinding:
        return SEOFinding(
            code=code,
            category=category,
            severity=severity,
            title=title,
            explanation=explanation,
            resource_type=resource_type or resource.resource_type,
            resource_id=resource.id,
            url=url or resource.url,
            confidence=0.97,
            evidence=[
                Evidence(
                    source="resource", observed=observed, expected=expected, url=url or resource.url
                )
            ],
            recommended_action=action,
            estimated_impact="high" if severity in {Severity.CRITICAL, Severity.HIGH} else "medium",
        )
