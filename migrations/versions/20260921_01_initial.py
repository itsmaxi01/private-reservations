"""Initial application schema."""

from alembic import op
import sqlalchemy as sa


revision = "20260921_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("auth_subject", sa.String(128), nullable=True, unique=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("display_name", sa.String(100), nullable=False),
        sa.Column("role", sa.String(6), nullable=False, server_default="MEMBER"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("role IN ('ADMIN', 'MEMBER')", name="user_role"),
    )
    op.create_index("uq_users_normalized_email", "users", [sa.text("lower(btrim(email))")], unique=True)

    op.create_table(
        "watch_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("type", sa.String(5), nullable=False),
        sa.Column("status", sa.String(7), nullable=False, server_default="PENDING"),
        sa.Column("added_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("type IN ('MOVIE', 'ANIME')", name="content_type"),
        sa.CheckConstraint("status IN ('PENDING', 'WATCHED')", name="watch_status"),
    )
    op.create_index("ix_watch_items_title", "watch_items", ["title"])
    op.create_index("ix_watch_items_added_by", "watch_items", ["added_by"])
    op.create_index(
        "uq_watch_items_normalized_title_type",
        "watch_items",
        [sa.text("lower(btrim(title))"), "type"],
        unique=True,
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_messages_created_by", "messages", ["created_by"])

    op.create_table(
        "reservations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(5), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("time", sa.Time(), nullable=False),
        sa.Column("watch_item_id", sa.Integer(), sa.ForeignKey("watch_items.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("type IN ('DATE', 'WATCH')", name="reservation_type"),
        sa.CheckConstraint(
            "(type = 'DATE' AND title IS NOT NULL AND reason IS NOT NULL AND watch_item_id IS NULL) OR "
            "(type = 'WATCH' AND title IS NULL AND reason IS NULL AND watch_item_id IS NOT NULL)",
            name="valid_shape",
        ),
    )
    for column in ("type", "date", "watch_item_id", "created_by"):
        op.create_index(f"ix_reservations_{column}", "reservations", [column])


def downgrade() -> None:
    op.drop_table("reservations")
    op.drop_table("messages")
    op.drop_table("watch_items")
    op.drop_table("users")
