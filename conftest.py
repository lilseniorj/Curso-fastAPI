import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel

from app.main import app
from db import get_session
from models import Customer

sqlite_name = "db.sqlite3"
sqlite_url = "sqlite://"

engine = create_engine(
    sqlite_url,
    connect_args={
    "check_same_thread": False,},
    poolclass=StaticPool
)

@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_seesion_override():
        return session

    app.dependency_overrides[get_session] = get_seesion_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="customer")
def customer_fixture(session: Session):
    customer = Customer(
        name= "Cliente de prueba",
        description= "Creado por la prueba",
        email= "fixture-test@ejemplo.com",
        age= 33,
    )
    session.add(customer)
    session.commit()
    session.refresh(customer)
    yield customer