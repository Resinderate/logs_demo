from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, date

import bytewax.operators as op
from bytewax.operators.windowing import (
    EventClock,
    TumblingWindower,
    collect_window,
    UTC_MIN,
)
from bytewax.connectors.files import FileSource
from bytewax.dataflow import Dataflow
from bytewax.outputs import DynamicSink, StatelessSinkPartition
from dateutil.parser import parse
import numpy as np

from uptime.stores import DailyStatsStore
from uptime.models import CustomerDailyStats


@dataclass
class Request:
    from_date: date
    timestamp: datetime
    client_id: str
    status_code: int
    response_time_ms: int


@dataclass
class Stats:
    customer_id: str
    from_date: date
    total_requests: int
    failed_requests: int
    successful_requests: int
    uptime: float
    average_latency_ms: int
    median_latency_ms: int
    p99_latency_ms: int


class StatsSinkPartition(StatelessSinkPartition[Stats]):
    def __init__(self):
        super().__init__()
        self.stats_store = DailyStatsStore()

    def _stats_dont_exist(self, customer_id: str, from_date: date) -> bool:
        # Ideally do this in some kind of batch too, of use upsert semantics instead.
        return self.stats_store.get_by_customer_and_date(customer=customer_id, from_date=from_date) is None

    def write_batch(self, stats: list[Stats]) -> None:
        stats_to_create = [s for s in stats if self._stats_dont_exist(s.customer_id, s.from_date)]
        stat_models_to_create = [
            CustomerDailyStats(
                customer=stat.customer_id,
                from_date=stat.from_date,
                total_requests=stat.total_requests,
                failed_requests=stat.failed_requests,
                successful_requests=stat.successful_requests,
                uptime=stat.uptime,
                average_latency_ms=stat.average_latency_ms,
                median_latency_ms=stat.median_latency_ms,
                p99_latency_ms=stat.p99_latency_ms,
            )
            for stat in stats_to_create
        ]
        self.stats_store.create_batch(stat_models_to_create)


class StatsDBSink(DynamicSink):
    def build(self, step_id, worker_index, worker_count):
        return StatsSinkPartition()


def parse_line(line: str) -> Request:
    (
        timestamp_date,
        timestamp_time,
        client_id,
        resource,
        status_code_str,
        response_time_seconds,
    ) = line.split()
    timestamp = parse(f"{timestamp_date} {timestamp_time}").replace(tzinfo=timezone.utc)
    status_code = int(status_code_str)
    response_time_ms = int(float(response_time_seconds) * 1000)
    return Request(
        from_date=timestamp.date(),
        timestamp=timestamp,
        client_id=client_id,
        status_code=status_code,
        response_time_ms=response_time_ms,
    )


def count_requests(requests: list[Request]) -> tuple[int, int, int]:
    """Counts the total, successful, and failed requests in the list.

    Returns as tuple of (total, successful, failed)
    """
    successful_requests = 0
    failed_requests = 0
    for request in requests:
        if request.status_code < 500:
            successful_requests += 1
        else:
            failed_requests += 1
    total_requests = successful_requests + failed_requests
    return total_requests, successful_requests, failed_requests


def calculate_stats(items: tuple[str, tuple[int, list[Request]]]) -> Stats:
    customer_id, (_, requests) = items
    # Just take the date from the first item, they all have the same date in the window.
    from_date = requests[0].from_date
    response_times_ms = [request.response_time_ms for request in requests]
    total_requests, successful_requests, failed_requests = count_requests(requests)
    uptime = successful_requests / total_requests

    response_times_ms.sort()
    # Truncating to nearest ms for avg/p99 for simplicity.
    average_latency_ms = int(np.mean(response_times_ms))
    median_latency_ms = int(np.median(response_times_ms))
    p99_latency_ms = int(np.percentile(response_times_ms, 99))

    return Stats(
        customer_id,
        from_date,
        total_requests,
        failed_requests,
        successful_requests,
        uptime,
        average_latency_ms,
        median_latency_ms,
        p99_latency_ms,
    )


clock: EventClock = EventClock(
    ts_getter=lambda request: request.timestamp,
    wait_for_system_duration=timedelta(seconds=10),
)
windower = TumblingWindower(length=timedelta(days=1), align_to=UTC_MIN)

flow = Dataflow("uptime")
input_ = op.input("input", flow, FileSource("data/api_requests.log"))
parsed_lines = op.map("parsed_lines", input_, parse_line)
keyed_by_client = op.key_on("keyed_by_client", parsed_lines, lambda request: request.client_id)
windowed_requests = collect_window("windowed_requests", keyed_by_client, clock=clock, windower=windower)
calculated_stats = op.map("calculated_stats", windowed_requests.down, mapper=calculate_stats)
op.output("out", calculated_stats, StatsDBSink())
