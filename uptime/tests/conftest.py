import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from uptime.models import Base


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    yield session

    session.close()
    Base.metadata.drop_all(engine)
