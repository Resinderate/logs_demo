from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from uptime.models import CustomerDailyStats

engine = create_engine("sqlite:///uptime.db")
SessionMaker = sessionmaker(bind=engine)


class DailyStatsStore:
    def __init__(self, session: Session | None = None):
        self.session = session or SessionMaker()

    def create(self, daily_stats: CustomerDailyStats) -> None:
        self.session.add(daily_stats)
        self.session.commit()

    def create_batch(self, daily_stats_batch: list[CustomerDailyStats]) -> None:
        for stats in daily_stats_batch:
            self.session.add(stats)
        self.session.commit()

    def get_by_customer_and_date(self, customer: str, from_date: date) -> CustomerDailyStats | None:
        return self.session.query(CustomerDailyStats).filter_by(customer=customer, from_date=from_date).first()
