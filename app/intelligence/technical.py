"""Technical crawl, indexation, redirect, and URL structure analysis."""

from urllib.parse import urlparse

from app.intelligence.utils import url_depth
from app.schemas.seo import (
    Evidence,
    ResourceType,
    SEOFinding,
    Severity,
    TechnicalAuditRequest,
    TechnicalAuditResult,
)


class TechnicalSEOEngine:
    async def analyze(self, request: TechnicalAuditRequest) -> TechnicalAuditResult:
        findings: list[SEOFinding] = []
        by_url = {item.url: item for item in request.urls}
        robots = (request.robots_txt or "").lower()

        if not request.robots_txt:
            findings.append(
                self._store_finding(
                    "robots.missing",
                    Severity.HIGH,
                    "robots.txt is unavailable",
                    "Crawlers have no store-specific crawl directives.",
                    "Serve a valid robots.txt and reference the canonical sitemap.",
                    request.base_url,
                )
            )
        elif "disallow: /" in robots and "user-agent: *" in robots:
            findings.append(
                self._store_finding(
                    "robots.site_blocked",
                    Severity.CRITICAL,
                    "Site may be blocked by robots.txt",
                    "A global Disallow directive was detected.",
                    "Remove the global block from production unless it is deliberately temporary.",
                    request.base_url,
                )
            )
        if not request.sitemap_urls:
            findings.append(
                self._store_finding(
                    "sitemap.missing",
                    Severity.HIGH,
                    "Sitemap is empty or unavailable",
                    "No discoverable sitemap URLs were supplied.",
                    "Publish a valid sitemap.xml containing canonical, indexable URLs.",
                    request.base_url,
                )
            )

        for item in request.urls:
            if item.status_code >= 500:
                findings.append(
                    self._url_finding(
                        "http.server_error",
                        Severity.CRITICAL,
                        item.url,
                        "Server error",
                        f"The URL returns HTTP {item.status_code}.",
                        "Resolve the application or upstream error and confirm a stable 200 response.",
                    )
                )
            elif item.status_code == 404:
                findings.append(
                    self._url_finding(
                        "http.not_found",
                        Severity.HIGH,
                        item.url,
                        "404 page",
                        "An internally known URL returns 404.",
                        "Restore it, remove links to it, or add a relevant one-hop 301 redirect.",
                    )
                )
            elif 300 <= item.status_code < 400:
                chain, seen, current = [item.url], {item.url}, item
                while current.redirect_to and current.redirect_to in by_url:
                    target = current.redirect_to
                    chain.append(target)
                    if target in seen:
                        findings.append(
                            self._url_finding(
                                "redirect.loop",
                                Severity.CRITICAL,
                                item.url,
                                "Redirect loop",
                                f"Redirect loop detected: {' → '.join(chain)}.",
                                "Point every URL in the loop directly to the final canonical destination.",
                            )
                        )
                        break
                    seen.add(target)
                    current = by_url[target]
                if len(chain) > 2:
                    findings.append(
                        self._url_finding(
                            "redirect.chain",
                            Severity.HIGH,
                            item.url,
                            "Redirect chain",
                            f"The redirect requires {len(chain) - 1} hops.",
                            "Update links and redirects to point directly to the final URL.",
                        )
                    )

            if item.status_code == 200 and not item.canonical_url:
                findings.append(
                    self._url_finding(
                        "canonical.missing",
                        Severity.HIGH,
                        item.url,
                        "Missing canonical",
                        "No canonical URL is declared.",
                        "Add an absolute self-referencing canonical.",
                    )
                )
            elif (
                item.canonical_url
                and item.canonical_url not in by_url
                and not item.canonical_url.startswith(request.base_url)
            ):
                findings.append(
                    self._url_finding(
                        "canonical.external",
                        Severity.CRITICAL,
                        item.url,
                        "External canonical",
                        f"The canonical points outside the store: {item.canonical_url}.",
                        "Verify intent and use the preferred store URL if this page should rank.",
                    )
                )

            if not item.robots_index and item.in_sitemap:
                findings.append(
                    self._url_finding(
                        "indexability.noindex_in_sitemap",
                        Severity.HIGH,
                        item.url,
                        "Noindex URL appears in sitemap",
                        "The sitemap asks crawlers to discover a URL that asks not to be indexed.",
                        "Remove the URL from the sitemap or make it indexable.",
                    )
                )
            if item.robots_index and item.status_code == 200 and not item.in_sitemap:
                findings.append(
                    self._url_finding(
                        "crawlability.not_in_sitemap",
                        Severity.MEDIUM,
                        item.url,
                        "Indexable URL missing from sitemap",
                        "The URL is indexable but receives no sitemap discovery signal.",
                        "Include the canonical URL in the appropriate Shopify sitemap.",
                    )
                )
            if url_depth(item.url) > 4:
                findings.append(
                    self._url_finding(
                        "url.excessive_depth",
                        Severity.MEDIUM,
                        item.url,
                        "Deep URL structure",
                        f"The URL has a path depth of {url_depth(item.url)}.",
                        "Use a concise descriptive hierarchy and strengthen links from shallower pages.",
                    )
                )
            parsed = urlparse(item.url)
            if any(char.isupper() for char in parsed.path) or "_" in parsed.path or "?" in item.url:
                findings.append(
                    self._url_finding(
                        "url.structure",
                        Severity.LOW,
                        item.url,
                        "Non-ideal URL structure",
                        "The URL contains uppercase letters, underscores, or query parameters.",
                        "Prefer stable lowercase paths with readable hyphen-separated words.",
                    )
                )
            if not item.breadcrumbs and url_depth(item.url) > 1:
                findings.append(
                    self._url_finding(
                        "breadcrumbs.missing",
                        Severity.MEDIUM,
                        item.url,
                        "Missing breadcrumbs",
                        "A nested page has no breadcrumb trail.",
                        "Add visible breadcrumbs and matching BreadcrumbList structured data.",
                    )
                )
            for locale, alternate in item.hreflang.items():
                alternate_item = by_url.get(alternate)
                if alternate_item and item.url not in alternate_item.hreflang.values():
                    findings.append(
                        self._url_finding(
                            "hreflang.no_return",
                            Severity.HIGH,
                            item.url,
                            "Missing hreflang return link",
                            f"The {locale} alternate does not reference this URL.",
                            "Add reciprocal hreflang annotations and an x-default where appropriate.",
                        )
                    )
            if (item.pagination_next or item.pagination_prev) and not item.canonical_url:
                findings.append(
                    self._url_finding(
                        "pagination.canonical",
                        Severity.MEDIUM,
                        item.url,
                        "Pagination canonical missing",
                        "A paginated page has no canonical declaration.",
                        "Give each useful paginated page a self-referencing canonical.",
                    )
                )

        indexable = sum(item.status_code == 200 and item.robots_index for item in request.urls)
        return TechnicalAuditResult(
            findings=findings,
            crawled_urls=len(request.urls),
            indexable_urls=indexable,
            summary=f"Analyzed {len(request.urls)} URLs and found {len(findings)} technical issues.",
            confidence=0.98 if request.urls else 0.5,
        )

    @staticmethod
    def _url_finding(
        code: str,
        severity: Severity,
        url: str,
        title: str,
        explanation: str,
        action: str,
    ) -> SEOFinding:
        return SEOFinding(
            code=code,
            category="technical",
            severity=severity,
            title=title,
            explanation=explanation,
            resource_type=ResourceType.URL,
            url=url,
            confidence=0.97,
            evidence=[Evidence(source="crawl", url=url)],
            recommended_action=action,
            estimated_impact="high" if severity in {Severity.CRITICAL, Severity.HIGH} else "medium",
        )

    @classmethod
    def _store_finding(
        cls,
        code: str,
        severity: Severity,
        title: str,
        explanation: str,
        action: str,
        url: str,
    ) -> SEOFinding:
        finding = cls._url_finding(code, severity, url, title, explanation, action)
        finding.resource_type = ResourceType.STORE
        return finding
