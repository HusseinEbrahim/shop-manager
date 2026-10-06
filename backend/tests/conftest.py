import os

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
if not TEST_DATABASE_URL or TEST_DATABASE_URL == os.getenv("DATABASE_URL"):
    raise RuntimeError("TEST_DATABASE_URL must be set and different from DATABASE_URL")

from database import Base, get_db
from main import app
from auth import hash_password
import models

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())


@pytest.fixture
def client():
    return TestClient(app)


def create_user(username, password, role):
    db = TestingSessionLocal()
    db.add(models.User(username=username, hashed_password=hash_password(password), role=role))
    db.commit()
    db.close()


def login(client, username, password):
    res = client.post("/auth/login", data={"username": username, "password": password})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture
def owner_headers(client):
    create_user("owner", "owner12345", "owner")
    return login(client, "owner", "owner12345")


@pytest.fixture
def staff_headers(client):
    create_user("staff", "staff12345", "staff")
    return login(client, "staff", "staff12345")


def create_product(client, headers, **overrides):
    data = {"name": "Safety Helmet", "price": 250, "stock_quantity": 40, "low_stock_threshold": 10}
    data.update(overrides)
    res = client.post("/products/", json=data, headers=headers)
    assert res.status_code == 201
    return res.json()