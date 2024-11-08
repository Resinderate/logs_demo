from pydantic import BaseModel
from datetime import date, datetime


class DailyStats(BaseModel):
    """The schema for reading stats for a comapny for a given day."""

    id: int
    created_at: datetime
    updated_at: datetime

    customer: str
    from_date: date

    total_requests: int
    failed_requests: int
    successful_requests: int
    # Defined here as percentage of successful requests.
    uptime: float

    average_latency_ms: int
    median_latency_ms: int
    p99_latency_ms: int
