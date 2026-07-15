"""Phase 2: Shopify integration and sync tables

Revision ID: 002_shopify_integration
Revises: 001_initial
Create Date: 2026-07-05

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_shopify_integration"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Extend stores table
    op.add_column("stores", sa.Column("shopify_shop_id", sa.String(length=64), nullable=True))
    op.add_column("stores", sa.Column("encrypted_access_token", sa.Text(), nullable=True))
    op.add_column("stores", sa.Column("scopes", sa.Text(), nullable=True))
    op.add_column("stores", sa.Column("sync_status", sa.String(length=32), server_default="idle", nullable=False))
    op.add_column("stores", sa.Column("installed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("stores", sa.Column("uninstalled_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("stores", sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("stores", sa.Column("last_sync_error", sa.Text(), nullable=True))
    op.create_index(op.f("ix_stores_shopify_shop_id"), "stores", ["shopify_shop_id"], unique=False)

    # Make shop_domain NOT NULL — set placeholder for any existing rows first
    op.execute("UPDATE stores SET shop_domain = 'unknown-' || id::text WHERE shop_domain IS NULL")
    op.alter_column("stores", "shop_domain", existing_type=sa.String(length=255), nullable=False)

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shopify_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("handle", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=True),
        sa.Column("vendor", sa.String(length=255), nullable=True),
        sa.Column("product_type", sa.String(length=255), nullable=True),
        sa.Column("seo_title", sa.String(length=512), nullable=True),
        sa.Column("seo_description", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "shopify_id", name="uq_products_store_shopify_id"),
    )
    op.create_index(op.f("ix_products_store_id"), "products", ["store_id"], unique=False)
    op.create_index(op.f("ix_products_shopify_id"), "products", ["shopify_id"], unique=False)
    op.create_index(op.f("ix_products_handle"), "products", ["handle"], unique=False)

    op.create_table(
        "collections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shopify_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("handle", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("collection_type", sa.String(length=32), nullable=True),
        sa.Column("seo_title", sa.String(length=512), nullable=True),
        sa.Column("seo_description", sa.Text(), nullable=True),
        sa.Column("products_count", sa.Integer(), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "shopify_id", name="uq_collections_store_shopify_id"),
    )
    op.create_index(op.f("ix_collections_store_id"), "collections", ["store_id"], unique=False)

    op.create_table(
        "pages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shopify_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("handle", sa.String(length=512), nullable=False),
        sa.Column("body_html", sa.Text(), nullable=True),
        sa.Column("seo_title", sa.String(length=512), nullable=True),
        sa.Column("seo_description", sa.Text(), nullable=True),
        sa.Column("is_published", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "shopify_id", name="uq_pages_store_shopify_id"),
    )
    op.create_index(op.f("ix_pages_store_id"), "pages", ["store_id"], unique=False)

    op.create_table(
        "blogs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shopify_id", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("handle", sa.String(length=512), nullable=False),
        sa.Column("seo_title", sa.String(length=512), nullable=True),
        sa.Column("seo_description", sa.Text(), nullable=True),
        sa.Column("articles_count", sa.Integer(), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "shopify_id", name="uq_blogs_store_shopify_id"),
    )
    op.create_index(op.f("ix_blogs_store_id"), "blogs", ["store_id"], unique=False)

    op.create_table(
        "redirects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shopify_id", sa.String(length=64), nullable=False),
        sa.Column("path", sa.String(length=2048), nullable=False),
        sa.Column("target", sa.String(length=2048), nullable=False),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "shopify_id", name="uq_redirects_store_shopify_id"),
    )
    op.create_index(op.f("ix_redirects_store_id"), "redirects", ["store_id"], unique=False)

    op.create_table(
        "metafields",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("shopify_id", sa.String(length=64), nullable=False),
        sa.Column("owner_type", sa.String(length=64), nullable=False),
        sa.Column("owner_shopify_id", sa.String(length=64), nullable=False),
        sa.Column("namespace", sa.String(length=255), nullable=False),
        sa.Column("key", sa.String(length=255), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("value_type", sa.String(length=64), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("store_id", "shopify_id", name="uq_metafields_store_shopify_id"),
    )
    op.create_index(op.f("ix_metafields_store_id"), "metafields", ["store_id"], unique=False)

    op.create_table(
        "sync_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sync_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), server_default="pending", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("records_processed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("records_failed", sa.Integer(), server_default="0", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("triggered_by", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_sync_logs_store_id"), "sync_logs", ["store_id"], unique=False)

    op.create_table(
        "webhook_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("topic", sa.String(length=128), nullable=False),
        sa.Column("shop_domain", sa.String(length=255), nullable=False),
        sa.Column("shopify_webhook_id", sa.String(length=64), nullable=True),
        sa.Column("payload_hash", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=32), server_default="received", nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhook_logs_store_id"), "webhook_logs", ["store_id"], unique=False)
    op.create_index(op.f("ix_webhook_logs_topic"), "webhook_logs", ["topic"], unique=False)
    op.create_index(op.f("ix_webhook_logs_shop_domain"), "webhook_logs", ["shop_domain"], unique=False)

    op.create_table(
        "mcp_tool_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("store_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("tool_name", sa.String(length=255), nullable=False),
        sa.Column("arguments", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("result", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("attempt", sa.Integer(), server_default="1", nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("executed_by", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mcp_tool_logs_store_id"), "mcp_tool_logs", ["store_id"], unique=False)
    op.create_index(op.f("ix_mcp_tool_logs_tool_name"), "mcp_tool_logs", ["tool_name"], unique=False)


def downgrade() -> None:
    op.drop_table("mcp_tool_logs")
    op.drop_table("webhook_logs")
    op.drop_table("sync_logs")
    op.drop_table("metafields")
    op.drop_table("redirects")
    op.drop_table("blogs")
    op.drop_table("pages")
    op.drop_table("collections")
    op.drop_table("products")

    op.drop_index(op.f("ix_stores_shopify_shop_id"), table_name="stores")
    op.drop_column("stores", "last_sync_error")
    op.drop_column("stores", "last_sync_at")
    op.drop_column("stores", "uninstalled_at")
    op.drop_column("stores", "installed_at")
    op.drop_column("stores", "sync_status")
    op.drop_column("stores", "scopes")
    op.drop_column("stores", "encrypted_access_token")
    op.drop_column("stores", "shopify_shop_id")
    op.alter_column("stores", "shop_domain", existing_type=sa.String(length=255), nullable=True)
