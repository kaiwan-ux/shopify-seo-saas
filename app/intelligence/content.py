"""Intent-aware content drafts with explicit review boundaries."""

import re

from app.intelligence.keywords import KeywordIntelligenceEngine
from app.intelligence.utils import words
from app.schemas.seo import ContentRequest, ContentResult, ContentType, KeywordRequest


class ContentIntelligenceEngine:
    async def generate(self, request: ContentRequest) -> ContentResult:
        attrs = ", ".join(f"{key}: {value}" for key, value in request.attributes.items())
        keyword = request.primary_keyword
        topic = request.topic
        sections: list[dict[str, str]] = []

        if request.content_type == ContentType.ALT_TEXT:
            content = f"{topic}{f' — {attrs}' if attrs else ''}"
            content = content[:125].rstrip()
        elif request.content_type == ContentType.FAQ:
            questions = [
                (
                    f"What should I know about {keyword}?",
                    f"{topic} is best evaluated by fit, quality, and the features that matter to your needs.",
                ),
                (
                    f"How do I choose the right {keyword}?",
                    "Compare the key specifications, intended use, care requirements, and total value before choosing.",
                ),
                (
                    f"How should I care for {keyword}?",
                    "Follow the supplied care instructions and store or maintain it appropriately for reliable use.",
                ),
            ]
            sections = [{"heading": q, "body": a} for q, a in questions]
            content = "\n\n".join(f"### {q}\n{a}" for q, a in questions)
        elif request.content_type == ContentType.PROS_CONS:
            sections = [
                {
                    "heading": "Pros",
                    "body": f"Purpose-built for {topic}; clear feature set; practical value.",
                },
                {
                    "heading": "Considerations",
                    "body": "Confirm sizing, compatibility, care, and exact specifications before purchase.",
                },
            ]
            content = "\n\n".join(f"## {s['heading']}\n{s['body']}" for s in sections)
        elif request.content_type == ContentType.COMPARISON:
            sections = [
                {
                    "heading": f"{topic}: key differences",
                    "body": f"Compare {keyword} options by intended use, materials, features, support, and total cost.",
                },
                {
                    "heading": "Which option fits?",
                    "body": "Choose based on the job you need done rather than the longest feature list.",
                },
            ]
            content = "\n\n".join(f"## {s['heading']}\n{s['body']}" for s in sections)
        elif request.content_type == ContentType.BUYING_GUIDE:
            sections = [
                {
                    "heading": f"How to choose {keyword}",
                    "body": f"Start with how and where you will use {topic}. Prioritize the features that affect that outcome.",
                },
                {
                    "heading": "Features to compare",
                    "body": attrs
                    or "Compare materials, dimensions, compatibility, durability, warranty, and upkeep.",
                },
                {
                    "heading": "Final checklist",
                    "body": "Confirm specifications, delivery, returns, and care instructions before ordering.",
                },
            ]
            content = "\n\n".join(f"## {s['heading']}\n{s['body']}" for s in sections)
        elif request.content_type == ContentType.FEATURE_HIGHLIGHTS:
            content = f"{topic} brings the essentials into one clear choice. {attrs or 'Review its practical features, reliable construction, and straightforward everyday use.'}"
        else:
            noun = (
                "collection"
                if request.content_type == ContentType.COLLECTION_DESCRIPTION
                else "product"
            )
            content = (
                f"Discover {topic}, a {noun} designed for shoppers looking for {keyword}. "
                f"{attrs + '. ' if attrs else ''}"
                "Its practical details make it easier to compare options and choose confidently. "
                f"Explore the features, confirm the specifications that matter to you, and find the right {keyword} for your needs."
            )

        title = (
            None
            if request.content_type == ContentType.ALT_TEXT
            else f"{topic}: {keyword.title()} Guide"
        )
        keyword_result = await KeywordIntelligenceEngine().analyze(
            KeywordRequest(
                text=content,
                title=title or "",
                seed_keywords=[keyword, *request.secondary_keywords],
            )
        )
        return ContentResult(
            content_type=request.content_type,
            content=content,
            title=title,
            sections=sections,
            keywords_used=[
                value
                for value in [keyword, *request.secondary_keywords]
                if value.lower() in content.lower()
            ],
            readability_score=self._readability(content),
            intent=keyword_result.intent,
            confidence=0.78,
            requires_human_review=True,
        )

    @staticmethod
    def _readability(text: str) -> float:
        sentences = max(1, len(re.findall(r"[.!?]+", text)))
        tokens = words(text)
        syllables = sum(max(1, len(re.findall(r"[aeiouy]+", word))) for word in tokens)
        if not tokens:
            return 0
        score = 206.835 - 1.015 * (len(tokens) / sentences) - 84.6 * (syllables / len(tokens))
        return round(max(0, min(100, score)), 1)
