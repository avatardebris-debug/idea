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


class TestTableIntegration:
    """Test table CRUD operations."""

    def test_create_table(self, client):
        """Test creating a content table."""
        response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "Test Table",
            "column_definitions": [
                {"name": "title", "type": "string"},
                {"name": "content", "type": "text"},
                {"name": "status", "type": "string"}
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
            "column_definitions": [{"name": "title", "type": "string"}]
        })

        response = client.get("/api/tables/?workspace_id=1")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1


class TestRecordIntegration:
    """Test record CRUD operations."""

    def test_create_record(self, client):
        """Test creating a record."""
        response = client.post("/api/records/", json={
            "table_id": 1,
            "data": {
                "title": "Test Post",
                "content": "Test content",
                "status": "draft"
            }
        })
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == "Test Post"
        assert data["status"] == "draft"

    def test_list_records_with_filters(self, client):
        """Test listing records with filters."""
        # Create records first
        for i in range(3):
            client.post("/api/records/", json={
                "table_id": 1,
                "data": {
                    "title": f"Post {i}",
                    "status": "draft" if i < 2 else "published"
                }
            })

        # Filter by status
        response = client.get("/api/records/?table_id=1&filter=published")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "published"

    def test_update_record(self, client):
        """Test updating a record."""
        # Create record first
        create_response = client.post("/api/records/", json={
            "table_id": 1,
            "data": {
                "title": "Original Title",
                "status": "draft"
            }
        })
        record_id = create_response.json()["id"]

        response = client.put(f"/api/records/{record_id}", json={
            "data": {
                "title": "Updated Title"
            }
        })
        assert response.status_code == 200
        assert response.json()["data"]["title"] == "Updated Title"

    def test_delete_record(self, client):
        """Test deleting a record."""
        # Create record first
        create_response = client.post("/api/records/", json={
            "table_id": 1,
            "data": {
                "title": "Delete Me",
                "status": "draft"
            }
        })
        record_id = create_response.json()["id"]

        response = client.delete(f"/api/records/{record_id}")
        assert response.status_code == 204

        # Verify it's deleted
        response = client.get(f"/api/records/{record_id}")
        assert response.status_code == 404


class TestAccountIntegration:
    """Test account connection operations."""

    def test_connect_account(self, client):
        """Test connecting a social media account."""
        response = client.post("/api/accounts/connect/", json={
            "workspace_id": 1,
            "platform": "twitter",
            "access_token": "test_token_123",
            "refresh_token": "test_refresh_123",
            "expires_in": 3600
        })
        assert response.status_code == 201
        data = response.json()
        assert data["platform"] == "twitter"
        assert data["is_active"] is True

    def test_disconnect_account(self, client):
        """Test disconnecting a social media account."""
        # Connect account first
        client.post("/api/accounts/connect/", json={
            "workspace_id": 1,
            "platform": "instagram",
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "expires_in": 3600
        })

        response = client.post("/api/accounts/disconnect/", json={
            "workspace_id": 1,
            "platform": "instagram"
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Account disconnected"


class TestSchedulingIntegration:
    """Test content scheduling operations."""

    def test_schedule_content(self, client):
        """Test scheduling content for future publication."""
        response = client.post("/api/schedule/", json={
            "record_id": 1,
            "scheduled_date": "2024-01-01T10:00:00Z"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["record_id"] == 1
        assert data["status"] == "scheduled"

    def test_cancel_schedule(self, client):
        """Test canceling a scheduled post."""
        # Create schedule first
        client.post("/api/schedule/", json={
            "record_id": 1,
            "scheduled_date": "2024-01-01T10:00:00Z"
        })

        response = client.post("/api/schedule/cancel/", json={
            "record_id": 1
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Schedule canceled"


class TestAnalyticsIntegration:
    """Test analytics operations."""

    def test_get_analytics(self, client):
        """Test getting analytics data."""
        response = client.get("/api/analytics/?workspace_id=1&period=30d")
        assert response.status_code == 200
        data = response.json()
        assert "total_posts" in data
        assert "engagement_rate" in data
        assert "platform_breakdown" in data


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_workspace_not_found(self, client):
        """Test 404 for non-existent workspace."""
        response = client.get("/api/workspaces/999")
        assert response.status_code == 404

    def test_invalid_table_creation(self, client):
        """Test validation errors for table creation."""
        response = client.post("/api/tables/", json={
            "workspace_id": 1,
            "name": "",  # Invalid: empty name
            "column_definitions": []
        })
        assert response.status_code == 422  # Validation error

    def test_invalid_record_creation(self, client):
        """Test validation errors for record creation."""
        response = client.post("/api/records/", json={
            "table_id": 1,
            "data": {}  # Invalid: no required fields
        })
        assert response.status_code == 422  # Validation error

    def test_duplicate_account_connection(self, client):
        """Test preventing duplicate account connections."""
        # Connect account first
        client.post("/api/accounts/connect/", json={
            "workspace_id": 1,
            "platform": "twitter",
            "access_token": "token1",
            "refresh_token": "refresh1",
            "expires_in": 3600
        })

        # Try to connect again with same platform
        response = client.post("/api/accounts/connect/", json={
            "workspace_id": 1,
            "platform": "twitter",
            "access_token": "token2",
            "refresh_token": "refresh2",
            "expires_in": 3600
        })
        assert response.status_code == 400  # Conflict


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
