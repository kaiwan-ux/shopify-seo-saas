"""Phase 4: SEO intelligence persistence.

Revision ID: 004_seo_intelligence
Revises: 003_ai_infrastructure
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "004_seo_intelligence"
down_revision: str | None = "003_ai_infrastructure"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    op.create_table(
        "seo_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "store_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("stores.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("report_type", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="completed"),
        sa.Column("summary", sa.Text()),
        sa.Column("overall_score", sa.Float()),
        sa.Column("report_data", postgresql.JSONB()),
        *_timestamps(),
    )
    op.create_index("ix_seo_reports_store_id", "seo_reports", ["store_id"])
    op.create_index("ix_seo_reports_report_type", "seo_reports", ["report_type"])

    op.create_table(
        "seo_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "report_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("seo_reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("code", sa.String(128), nullable=False),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("title", sa.String(512), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("resource_type", sa.String(32)),
        sa.Column("resource_id", sa.String(128)),
        sa.Column("url", sa.Text()),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence", postgresql.JSONB()),
        sa.Column("recommended_action", sa.Text(), nullable=False),
        sa.Column("estimated_impact", sa.String(32), nullable=False),
        sa.Column(
            "approval_required", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        *_timestamps(),
    )
    op.create_index("ix_seo_issues_report_id", "seo_issues", ["report_id"])
    op.create_index("ix_seo_issues_code", "seo_issues", ["code"])
    op.create_index("ix_seo_issues_category", "seo_issues", ["category"])
    op.create_index("ix_seo_issues_severity", "seo_issues", ["severity"])
    op.create_index("ix_seo_issues_resource_id", "seo_issues", ["resource_id"])

    op.create_table(
        "seo_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "report_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("seo_reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", sa.String(64), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("issue_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Float(), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_seo_scores_report_id", "seo_scores", ["report_id"])
    op.create_index("ix_seo_scores_category", "seo_scores", ["category"])

    op.create_table(
        "seo_recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "report_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("seo_reports.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("issue_code", sa.String(128), nullable=False),
        sa.Column("priority", sa.String(16), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("estimated_seo_impact", sa.String(32), nullable=False),
        sa.Column("suggested_fix", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "approval_required", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("resource_id", sa.String(128)),
        *_timestamps(),
    )
    op.create_index("ix_seo_recommendations_report_id", "seo_recommendations", ["report_id"])
    op.create_index("ix_seo_recommendations_issue_code", "seo_recommendations", ["issue_code"])
    op.create_index("ix_seo_recommendations_priority", "seo_recommendations", ["priority"])

    simple_tables = {
        "keyword_analyses": [
            sa.Column("resource_id", sa.String(128)),
            sa.Column("primary_keyword", sa.String(512)),
            sa.Column("search_intent", sa.String(32), nullable=False),
            sa.Column("secondary_keywords", postgresql.JSONB()),
            sa.Column("semantic_keywords", postgresql.JSONB()),
            sa.Column("metrics", postgresql.JSONB()),
            sa.Column("suggestions", postgresql.JSONB()),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("provider_data", postgresql.JSONB()),
        ],
        "schema_validations": [
            sa.Column("resource_id", sa.String(128)),
            sa.Column("schema_type", sa.String(64), nullable=False),
            sa.Column("json_ld", postgresql.JSONB(), nullable=False),
            sa.Column("is_valid", sa.Boolean(), nullable=False),
            sa.Column("errors", postgresql.JSONB()),
            sa.Column("warnings", postgresql.JSONB()),
            sa.Column("confidence", sa.Float(), nullable=False),
        ],
        "redirect_recommendations": [
            sa.Column("source_url", sa.Text(), nullable=False),
            sa.Column("target_url", sa.Text()),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("status", sa.String(32), nullable=False, server_default="pending"),
            sa.Column(
                "approval_required", sa.Boolean(), nullable=False, server_default=sa.text("true")
            ),
        ],
        "content_generation_logs": [
            sa.Column("resource_id", sa.String(128)),
            sa.Column("content_type", sa.String(64), nullable=False),
            sa.Column("prompt_data", postgresql.JSONB()),
            sa.Column("generated_content", sa.Text(), nullable=False),
            sa.Column("readability_score", sa.Float()),
            sa.Column("confidence", sa.Float(), nullable=False),
            sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        ],
    }
    for name, columns in simple_tables.items():
        op.create_table(
            name,
            sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column(
                "store_id",
                postgresql.UUID(as_uuid=True),
                sa.ForeignKey("stores.id", ondelete="CASCADE"),
                nullable=False,
            ),
            *columns,
            *_timestamps(),
        )
        op.create_index(f"ix_{name}_store_id", name, ["store_id"])

    op.create_table(
        "technical_audits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "store_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("stores.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "report_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("seo_reports.id", ondelete="SET NULL"),
        ),
        sa.Column("base_url", sa.Text(), nullable=False),
        sa.Column("crawled_urls", sa.Integer(), nullable=False),
        sa.Column("indexable_urls", sa.Integer(), nullable=False),
        sa.Column("findings", postgresql.JSONB()),
        sa.Column("summary", sa.Text()),
        sa.Column("confidence", sa.Float(), nullable=False),
        *_timestamps(),
    )
    op.create_index("ix_technical_audits_store_id", "technical_audits", ["store_id"])
    op.create_index("ix_technical_audits_report_id", "technical_audits", ["report_id"])


def downgrade() -> None:
    for table in [
        "technical_audits",
        "content_generation_logs",
        "redirect_recommendations",
        "schema_validations",
        "keyword_analyses",
        "seo_recommendations",
        "seo_scores",
        "seo_issues",
        "seo_reports",
    ]:
        op.drop_table(table)
