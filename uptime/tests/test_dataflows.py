from datetime import date, datetime, timezone
import pytest
from uptime.dataflows import parse_line, Request, calculate_stats, Stats


class TestParseLine:
    def test_parse_line(self):
        line = "2024-10-20 09:40:23 cust_36 /api/v1/resource3 400 1.700"
        request = parse_line(line)

        assert request == Request(
            from_date=date(2024, 10, 20),
            timestamp=datetime(2024, 10, 20, 9, 40, 23, tzinfo=timezone.utc),
            client_id="cust_36",
            status_code=400,
            response_time_ms=1700,
        )

    def test_malformed_line(self):
        bad_line = "This doesn't seem right"
        with pytest.raises(ValueError):
            parse_line(bad_line)


class TestCalculateStats:
    def test_asd(self):
        common_details = {
            "from_date": date(2024, 1, 17),
            "client_id": "cust_4",
        }
        requests = [
            Request(
                **common_details,
                timestamp=datetime(2024, 1, 17, 9, 40, tzinfo=timezone.utc),
                status_code=200,
                response_time_ms=100,
            ),
            Request(
                **common_details,
                timestamp=datetime(2024, 1, 17, 10, 40, tzinfo=timezone.utc),
                status_code=200,
                response_time_ms=200,
            ),
            Request(
                **common_details,
                timestamp=datetime(2024, 1, 17, 11, 40, tzinfo=timezone.utc),
                status_code=500,
                response_time_ms=300,
            ),
            Request(
                **common_details,
                timestamp=datetime(2024, 1, 17, 12, 40, tzinfo=timezone.utc),
                status_code=401,
                response_time_ms=400,
            ),
            Request(
                **common_details,
                timestamp=datetime(2024, 1, 17, 13, 40, tzinfo=timezone.utc),
                status_code=200,
                response_time_ms=500,
            ),
        ]
        items = ("cust_4", (1, requests))

        stats = calculate_stats(items)

        assert stats == Stats(
            customer_id="cust_4",
            from_date=date(2024, 1, 17),
            total_requests=5,
            failed_requests=1,
            successful_requests=4,
            uptime=0.8,
            average_latency_ms=300,
            median_latency_ms=300,
            p99_latency_ms=496,
        )
