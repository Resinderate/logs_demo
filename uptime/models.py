from datetime import datetime, date
from sqlalchemy import UniqueConstraint, func, Index
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    pass


class CustomerDailyStats(Base):
    """The stats for a company across a single day."""

    __tablename__ = "customer_daily_stats"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    customer: Mapped[str] = mapped_column(nullable=False)
    from_date: Mapped[date] = mapped_column(nullable=False)

    total_requests: Mapped[int] = mapped_column(nullable=False)
    failed_requests: Mapped[int] = mapped_column(nullable=False)
    successful_requests: Mapped[int] = mapped_column(nullable=False)
    # Defined as percentage of successful requests
    uptime: Mapped[float] = mapped_column(nullable=False)

    average_latency_ms: Mapped[int] = mapped_column(nullable=False)
    median_latency_ms: Mapped[int] = mapped_column(nullable=False)
    p99_latency_ms: Mapped[int] = mapped_column(nullable=False)

    __table_args__ = (
        Index("idx_customer_from_date", "customer", "from_date"),
        UniqueConstraint("customer", "from_date", name="uq_customer_from_date"),
    )
