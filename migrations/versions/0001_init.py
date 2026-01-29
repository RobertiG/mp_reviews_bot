"""init

Revision ID: 0001
Revises: 
Create Date: 2025-01-28 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_user_id", sa.String(), nullable=False, unique=True),
        sa.Column("is_owner", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "project_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "cabinets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("marketplace", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("api_token_encrypted", sa.Text(), nullable=False),
        sa.Column("api_token_masked", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "sku_maps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("marketplace", sa.String(), nullable=False),
        sa.Column("seller_sku", sa.String(), nullable=False),
        sa.Column("marketplace_item_id", sa.String(), nullable=False),
        sa.Column("internal_sku", sa.String(), nullable=False),
        sa.Column("product_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "kb_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("internal_sku", sa.String(), nullable=True),
        sa.Column("rule_type", sa.String(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("cabinet_id", sa.Integer(), sa.ForeignKey("cabinets.id"), nullable=False),
        sa.Column("marketplace", sa.String(), nullable=False),
        sa.Column("marketplace_event_id", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=True),
        sa.Column("sentiment", sa.String(), nullable=True),
        sa.Column("internal_sku", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=False),
        sa.Column("media_links", sa.JSON(), nullable=True),
        sa.Column("suggested_reply", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("kb_rule_ids", sa.JSON(), nullable=True),
        sa.Column("conflict", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "project_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("autogen_positive", sa.Boolean(), default=False),
        sa.Column("autosend_positive", sa.Boolean(), default=False),
        sa.Column("autogen_negative", sa.Boolean(), default=False),
        sa.Column("autosend_negative", sa.Boolean(), default=False),
        sa.Column("autogen_questions", sa.Boolean(), default=False),
        sa.Column("autosend_questions", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "balances",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tokens", sa.Integer(), default=0),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "token_ledger",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("delta", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=True),
        sa.Column("actor_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("model", sa.String(), nullable=True),
        sa.Column("model_version", sa.String(), nullable=True),
        sa.Column("kb_rule_ids", sa.JSON(), nullable=True),
        sa.Column("raw_payload", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("token_ledger")
    op.drop_table("balances")
    op.drop_table("project_settings")
    op.drop_table("events")
    op.drop_table("kb_rules")
    op.drop_table("sku_maps")
    op.drop_table("cabinets")
    op.drop_table("project_members")
    op.drop_table("projects")
    op.drop_table("users")
