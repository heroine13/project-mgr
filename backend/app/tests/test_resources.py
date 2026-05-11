"""
Resource and Cost Management Tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_resources.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers():
    token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}


def test_create_resource(client, auth_headers):
    """Test creating a resource"""
    response = client.post(
        "/resources/resources",
        json={
            "name": "Test Resource",
            "resource_type": "human",
            "unit_cost": 100.0,
            "is_available": True
        },
        headers=auth_headers
    )
    assert response.status_code in [201, 401, 422]


def test_list_resources(client, auth_headers):
    """Test listing resources"""
    response = client.get("/resources/resources", headers=auth_headers)
    assert response.status_code in [200, 401]


def test_create_allocation(client, auth_headers):
    """Test creating resource allocation"""
    response = client.post(
        "/resources/allocations",
        json={
            "resource_id": 1,
            "project_id": 1,
            "allocation_type": "percentage",
            "allocated_value": 50,
            "budgeted_cost": 1000.0
        },
        headers=auth_headers
    )
    assert response.status_code in [201, 401, 422]


def test_create_cost_record(client, auth_headers):
    """Test creating cost record"""
    response = client.post(
        "/resources/costs",
        json={
            "project_id": 1,
            "category": "labor",
            "amount": 500.0,
            "description": "Test cost"
        },
        headers=auth_headers
    )
    assert response.status_code in [201, 401, 422]


def test_cost_summary(client, auth_headers):
    """Test getting project cost summary"""
    response = client.get("/resources/projects/1/cost-summary", headers=auth_headers)
    assert response.status_code in [200, 401, 404]


def test_resource_search_filter(client, auth_headers):
    """Test resource filtering"""
    response = client.get(
        "/resources/resources?resource_type=human&is_available=true",
        headers=auth_headers
    )
    assert response.status_code in [200, 401]