"""add models

Revision ID: b82e90777c56
Revises:

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b82e90777c56"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "customer_daily_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("customer", sa.String(), nullable=False),
        sa.Column("from_date", sa.Date(), nullable=False),
        sa.Column("total_requests", sa.Integer(), nullable=False),
        sa.Column("failed_requests", sa.Integer(), nullable=False),
        sa.Column("successful_requests", sa.Integer(), nullable=False),
        sa.Column("uptime", sa.Float(), nullable=False),
        sa.Column("average_latency_ms", sa.Integer(), nullable=False),
        sa.Column("median_latency_ms", sa.Integer(), nullable=False),
        sa.Column("p99_latency_ms", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer", "from_date", name="uq_customer_from_date"),
    )


def downgrade() -> None:
    op.drop_table("customer_daily_stats")
