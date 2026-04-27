"""Integration tests for the social media management tool."""
import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import User, Workspace, Account, ContentTable, ContentRecord
from app.schemas import WorkspaceCreate, TableCreate, RecordCreate, RecordUpdate
from app.services import workspace_service, table_service, record_service
from app.main import app
from fastapi.testclient import TestClient


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_integration.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    """Create test database with all tables."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db(test_db):
    """Provide a transactional database session."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """Provide test client with overridden database dependency."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


class TestWorkspaceIntegration:
    """Test workspace CRUD operations."""

    def test_create_workspace(self, client):
        """Test creating a workspace."""
        response = client.post("/api/workspaces/", json={
            "name": "Test Workspace",
            "description": "Test description"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Workspace"
        assert data["description"] == "Test description"
        assert data["owner_id"] == 1

    def test_list_workspaces(self, client):
        """Test listing workspaces."""
        # Create workspace first
        client.post("/api/workspaces/", json={
            "name": "List Test",
            "description": "For listing"
        })

        response = client.get("/api/workspaces/")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    def test_get_workspace(self, client):
        """Test getting a single workspace."""
        # Create workspace first
        create_response = client.post("/api/workspaces/", json={
            "name": "Get Test",
            "description": "For getting"
        })
        workspace_id = create_response.json()["id"]

        response = client.get(f"/api/workspaces/{workspace_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Get Test"

    def test_update_workspace(self, client):
        """Test updating a workspace."""
        # Create workspace first
        create_response = client.post("/api/workspaces/", json={
            "name": "Update Test",
            "description": "Original"
        })
        workspace_id = create_response.json()["id"]

        response = client.put(f"/api/workspaces/{workspace_id}", json={
            "name": "Updated Name",
            "description": "Updated description"
        })
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_delete_workspace(self, client):
        """Test deleting a workspace."""
        # Create workspace first
        create_response = client.post("/api/workspaces/", json={
            "name": "Delete Test",
            "description": "Will be deleted"
        })
        workspace_id = create_response.json()["id"]

        response = client.delete(f"/api/workspaces/{workspace_id}")
        assert response.status_code == 204

    def test_workspace_not_found(self, client):
        """Test 404 for non-existent workspace."""
        response = client.get("/api/workspaces/999")
        assert response.status_code == 404


class TestTableIntegration:
    """Test table CRUD operations."""

    def test_create_table(self, client):
        """Test creating a content table."""
        response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"},
                {"name": "content", "type": "text"},
                {"name": "status", "type": "status"}
            ]
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Table"
        assert len(data["column_definitions"]) == 3

    def test_list_tables(self, client):
        """Test listing tables."""
        # Create table first
        client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "List Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"}
            ]
        })

        response = client.get("/api/tables/?workspace_id=1")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    def test_get_table(self, client):
        """Test getting a single table."""
        # Create table first
        create_response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Get Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"}
            ]
        })
        table_id = create_response.json()["id"]

        response = client.get(f"/api/tables/{table_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Get Test Table"

    def test_update_table(self, client):
        """Test updating a table."""
        # Create table first
        create_response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Update Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"}
            ]
        })
        table_id = create_response.json()["id"]

        response = client.put(f"/api/tables/{table_id}", json={
            "name": "Updated Table Name"
        })
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Table Name"

    def test_delete_table(self, client):
        """Test deleting a table."""
        # Create table first
        create_response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Delete Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"}
            ]
        })
        table_id = create_response.json()["id"]

        response = client.delete(f"/api/tables/{table_id}")
        assert response.status_code == 204

    def test_invalid_table_creation(self, client):
        """Test validation errors for table creation."""
        response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "",  # Invalid: empty name
            "column_definitions": []
        })
        assert response.status_code == 422  # Validation error


class TestRecordIntegration:
    """Test record CRUD operations."""

    def test_create_record(self, client):
        """Test creating a content record."""
        # Create table first
        table_response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Record Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"},
                {"name": "content", "type": "text"}
            ]
        })
        table_id = table_response.json()["id"]

        response = client.post("/api/records/", json={
            "table_id": table_id,
            "data": {
                "title": "Test Title",
                "content": "Test Content"
            }
        })
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == "Test Title"

    def test_list_records(self, client):
        """Test listing records."""
        # Create table and record first
        table_response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "List Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"}
            ]
        })
        table_id = table_response.json()["id"]

        client.post("/api/records/", json={
            "table_id": table_id,
            "data": {"title": "List Test"}
        })

        response = client.get(f"/api/records/?table_id={table_id}")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) >= 1

    def test_get_record(self, client):
        """Test getting a single record."""
        # Create table and record first
        table_response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Get Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"}
            ]
        })
        table_id = table_response.json()["id"]

        record_response = client.post("/api/records/", json={
            "table_id": table_id,
            "data": {"title": "Get Test"}
        })
        record_id = record_response.json()["id"]

        response = client.get(f"/api/records/{record_id}")
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Get Test"

    def test_update_record(self, client):
        """Test updating a record."""
        # Create table and record first
        table_response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Update Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"}
            ]
        })
        table_id = table_response.json()["id"]

        record_response = client.post("/api/records/", json={
            "table_id": table_id,
            "data": {"title": "Original"}
        })
        record_id = record_response.json()["id"]

        response = client.put(f"/api/records/{record_id}", json={
            "data": {"title": "Updated"}
        })
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated"

    def test_delete_record(self, client):
        """Test deleting a record."""
        # Create table and record first
        table_response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Delete Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"}
            ]
        })
        table_id = table_response.json()["id"]

        record_response = client.post("/api/records/", json={
            "table_id": table_id,
            "data": {"title": "Delete Test"}
        })
        record_id = record_response.json()["id"]

        response = client.delete(f"/api/records/{record_id}")
        assert response.status_code == 204

    def test_invalid_record_creation(self, client):
        """Test validation errors for record creation."""
        # Create table first
        table_response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Invalid Test Table",
            "column_definitions": [
                {"name": "title", "type": "text"}
            ]
        })
        table_id = table_response.json()["id"]

        response = client.post("/api/records/", json={
            "table_id": table_id,
            "data": {}  # Missing required field
        })
        assert response.status_code == 422  # Validation error


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_workspace_not_found(self, client):
        """Test 404 for non-existent workspace."""
        response = client.get("/api/workspaces/999")
        assert response.status_code == 404

    def test_table_not_found(self, client):
        """Test 404 for non-existent table."""
        response = client.get("/api/tables/999")
        assert response.status_code == 404

    def test_record_not_found(self, client):
        """Test 404 for non-existent record."""
        response = client.get("/api/records/999")
        assert response.status_code == 404
