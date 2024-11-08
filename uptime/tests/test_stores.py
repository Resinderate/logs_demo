from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from uptime.stores import DailyStatsStore
from uptime.models import CustomerDailyStats


class TestDailyStatsStore:
    def test_missing(self, session):
        store = DailyStatsStore(session=session)
        stats = store.get_by_customer_and_date("doesnt_exist", from_date=date(2024, 1, 1))
        assert stats is None

    def test_crate_stats(self, session):
        store = DailyStatsStore(session=session)
        stats = CustomerDailyStats(
            customer="customer-1",
            from_date=date(2024, 1, 3),
            total_requests=10,
            failed_requests=1,
            successful_requests=9,
            uptime=0.9,
            average_latency_ms=50,
            median_latency_ms=55,
            p99_latency_ms=120,
        )

        store.create(stats)

        stats = store.get_by_customer_and_date("customer-1", from_date=date(2024, 1, 3))
        assert stats is not None
        assert stats.uptime == 0.9

    def test_create_batch(self, session):
        store = DailyStatsStore(session=session)
        details = {
            "customer": "customer-1",
            "total_requests": 10,
            "failed_requests": 1,
            "successful_requests": 9,
            "uptime": 0.9,
            "average_latency_ms": 50,
            "median_latency_ms": 55,
            "p99_latency_ms": 120,
        }
        stats = [
            CustomerDailyStats(**details, from_date=date(2024, 1, 5)),
            CustomerDailyStats(**details, from_date=date(2024, 1, 6)),
        ]

        store.create_batch(stats)

        stats = store.get_by_customer_and_date("customer-1", from_date=date(2024, 1, 5))
        assert stats is not None
        stats = store.get_by_customer_and_date("customer-1", from_date=date(2024, 1, 6))
        assert stats is not None

    def test_duplicates(self, session):
        store = DailyStatsStore(session=session)
        details = {
            "customer": "customer-1",
            "from_date": date(2024, 1, 3),
            "total_requests": 10,
            "failed_requests": 1,
            "successful_requests": 9,
            "uptime": 0.9,
            "average_latency_ms": 50,
            "median_latency_ms": 55,
            "p99_latency_ms": 120,
        }
        stats = CustomerDailyStats(**details)
        stats_dupe = CustomerDailyStats(**details)

        store.create(stats)

        with pytest.raises(IntegrityError):
            store.create(stats_dupe)
