from datetime import date

from fastapi import APIRouter, Query, HTTPException
from typing import Annotated

from uptime.stores import DailyStatsStore
from uptime.schemas import DailyStats

router = APIRouter()


@router.get("/customers/{customer_id}/stats")
async def customer_stats(
    customer_id: str,
    # `from` is reserved, so need to alias it.
    from_date: Annotated[date | None, Query(alias="from")] = None,
) -> DailyStats:
    store = DailyStatsStore()
    stats = store.get_by_customer_and_date(customer=customer_id, from_date=from_date)
    if stats is None:
        raise HTTPException(status_code=404, detail="Could not find stats for customer and date.")
    return stats
