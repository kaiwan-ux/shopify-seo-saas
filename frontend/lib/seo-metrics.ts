import type { Issue, SEOResource, Severity } from "@/lib/types";

export type IssueCounts = Record<Severity, number>;

const severityPenalty: Record<Severity, number> = {
  critical: 8,
  high: 2.2,
  medium: 0.8,
  low: 0.3,
};

export function countIssues(findings: Issue[]): IssueCounts {
  return {
    critical: findings.filter((item) => item.severity === "critical").length,
    high: findings.filter((item) => item.severity === "high").length,
    medium: findings.filter((item) => item.severity === "medium").length,
    low: findings.filter((item) => item.severity === "low").length,
  };
}

export function scoreFromFindings(findings: Issue[]) {
  const penalty = findings.reduce((sum, issue) => sum + severityPenalty[issue.severity], 0);
  return clampScore(Math.round(100 - penalty));
}

export function liveFindingsFromResources(resources: SEOResource[]): Issue[] {
  const findings: Issue[] = [];
  for (const resource of resources) {
    const type = resource.resource_type;
    const bodyWords = wordCount(resource.body ?? "");
    const minWords = type === "collection" || type === "page" ? 150 : 100;

    if ((type === "product" || type === "collection") && !resource.meta_description?.trim()) {
      findings.push(issue(resource, "metadata.missing_description", "Missing meta description", "high", "Search engines must create their own snippet."));
    }

    if (type === "product" || type === "collection") {
      const effectiveTitle = (resource.seo_title || resource.title || "").trim();
      if (!effectiveTitle) {
        findings.push(issue(resource, "metadata.missing_title", "Missing SEO title", "high", "No SEO title or usable page title is set."));
      } else if (!resource.seo_title && effectiveTitle.length < 30) {
        findings.push(issue(resource, "metadata.title_fallback_short", "SEO title uses short title fallback", "medium", "Shopify is using a short normal title as the search title."));
      } else if (resource.seo_title && (resource.seo_title.length < 30 || resource.seo_title.length > 60)) {
        findings.push(issue(resource, "metadata.title_length", "SEO title length is suboptimal", "medium", "The title may truncate or communicate too little in search results."));
      }
    }

    if (bodyWords < minWords) {
      findings.push(issue(resource, bodyWords ? "content.thin" : "content.missing", bodyWords ? "Thin content" : "Missing content", bodyWords ? "medium" : "high", `The page contains ${bodyWords} words.`));
    }
  }
  return findings;
}

export function issueLabel(count: number) {
  if (count === 0) return "No open SEO issues detected from synced data.";
  if (count === 1) return "1 open SEO issue detected from synced data.";
  return `${count} open SEO issues detected from synced data.`;
}

export function relativeTime(value?: string) {
  if (!value) return "Not run yet";
  const diff = Date.now() - new Date(value).getTime();
  if (!Number.isFinite(diff) || diff < 0) return "Just now";
  const minutes = Math.floor(diff / 60_000);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

function issue(resource: SEOResource, code: string, title: string, severity: Severity, explanation: string): Issue {
  return {
    code,
    title,
    severity,
    explanation,
    category: code.split(".")[0] || "seo",
    confidence: 0.97,
    approval_required: false,
    resource_id: resource.id,
    resource_type: resource.resource_type,
    url: resource.url,
  };
}

function wordCount(value: string) {
  return value.replace(/<[^>]+>/g, " ").trim().split(/\s+/).filter(Boolean).length;
}

function clampScore(value: number) {
  return Math.max(0, Math.min(100, value));
}
