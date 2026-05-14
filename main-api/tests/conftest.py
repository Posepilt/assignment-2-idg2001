import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.models.olympic_event import OlympicEvent
from main import app

TEST_ENGINE = create_engine(
    "sqlite:///./test.db",
    connect_args={"check_same_thread": False},
)
TestSession = sessionmaker(bind=TEST_ENGINE, autocommit=False, autoflush=False)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db  # swap real db with test db so tests dont touch real data


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=TEST_ENGINE)
    db = TestSession()
    db.add(OlympicEvent(
        name="Usain Bolt", sex="M", age=21.0, noc="JAM",
        sport="Athletics", event="100 metres", year=2008,
        season="Summer", city="Beijing", medal="Gold",
    ))
    db.add(OlympicEvent(
        name="Usain Bolt", sex="M", age=25.0, noc="JAM",
        sport="Athletics", event="100 metres", year=2012,
        season="Summer", city="London", medal="Gold",
    ))
    db.add(OlympicEvent(
        name="Petter Northug", sex="M", age=24.0, noc="NOR",
        sport="Skiing", event="50 km", year=2010,
        season="Winter", city="Vancouver", medal="Gold",
    ))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
