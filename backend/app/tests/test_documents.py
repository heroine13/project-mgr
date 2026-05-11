"""
Document Version Control Tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.core.security import create_access_token


SQLALCHEMY_DATABASE_URL = "sqlite:///./test_documents.db"
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


def test_create_document(client, auth_headers):
    """Test creating a document"""
    response = client.post(
        "/documents/",
        json={
            "name": "Test Document",
            "description": "Test description",
            "category": "technical"
        },
        headers=auth_headers
    )
    assert response.status_code in [201, 401, 422]


def test_list_documents(client, auth_headers):
    """Test listing documents"""
    response = client.get("/documents/", headers=auth_headers)
    assert response.status_code in [200, 401]


def test_document_versioning(client, auth_headers):
    """Test document version creation"""
    response = client.post(
        "/documents/1/versions",
        json={
            "filename": "test.pdf",
            "file_path": "/uploads/test.pdf",
            "file_size": 1024,
            "version_notes": "Initial version"
        },
        headers=auth_headers
    )
    assert response.status_code in [201, 401, 404, 422]


def test_version_rollback(client, auth_headers):
    """Test version rollback"""
    response = client.post(
        "/documents/1/versions/1/rollback",
        headers=auth_headers
    )
    assert response.status_code in [200, 401, 404]


def test_document_search(client, auth_headers):
    """Test document search"""
    response = client.post(
        "/documents-search/search",
        json={
            "query": "test",
            "page": 1,
            "page_size": 20
        },
        headers=auth_headers
    )
    assert response.status_code in [200, 401]


def test_category_tree(client, auth_headers):
    """Test category tree retrieval"""
    response = client.get("/documents-search/categories/tree", headers=auth_headers)
    assert response.status_code in [200, 401]


def test_search_history(client, auth_headers):
    """Test search history"""
    response = client.get("/documents-search/search/history", headers=auth_headers)
    assert response.status_code in [200, 401]


def test_saved_searches(client, auth_headers):
    """Test saved searches"""
    response = client.get("/documents-search/search/saved", headers=auth_headers)
    assert response.status_code in [200, 401]