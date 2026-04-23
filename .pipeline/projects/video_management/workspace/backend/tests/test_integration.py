"""Integration tests for the video management backend."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import VideoStatus, FieldTypeId

# ── Test database setup ──────────────────────────────────────────────

SQLALCHEMY_DATABASE_URL = "sqlite:///./test_video_management.db"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override the database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ── Fixtures ───────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Create tables before each test and drop them after."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_client():
    """Return the test client."""
    return client


@pytest.fixture
def sample_table(test_client):
    """Create a default table via the API."""
    # The default table is auto-created on first access
    response = test_client.get("/api/videos")
    assert response.status_code == 200
    return response.json()


# ── Health check ───────────────────────────────────────────────────────────

def test_health_check(test_client):
    response = test_client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# ── Video CRUD tests ────────────────────────────────────────────────────────

def test_create_video(test_client):
    """Test creating a video record."""
    payload = {
        "title": "Test Video",
        "description": "A test video description",
        "tags": ["python", "tutorial"],
        "custom_fields": {"episode": 1},
    }
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Video"
    assert data["status"] == "draft"
    assert data["tags"] == ["python", "tutorial"]
    assert data["id"] is not None


def test_create_video_missing_title(test_client):
    """Test that creating a video without a title fails."""
    payload = {"description": "No title"}
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 422  # Validation error


def test_get_video(test_client):
    """Test retrieving a video by ID."""
    # Create first
    create_resp = test_client.post("/api/videos", json={"title": "Get Me"})
    video_id = create_resp.json()["id"]

    # Retrieve
    response = test_client.get(f"/api/videos/{video_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Get Me"


def test_get_video_not_found(test_client):
    """Test retrieving a non-existent video."""
    response = test_client.get("/api/videos/nonexistent-id")
    assert response.status_code == 404


def test_update_video(test_client):
    """Test updating a video."""
    # Create
    create_resp = test_client.post("/api/videos", json={"title": "Old Title"})
    video_id = create_resp.json()["id"]

    # Update
    update_resp = test_client.put(
        f"/api/videos/{video_id}",
        json={"title": "New Title", "description": "Updated desc"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "New Title"
    assert update_resp.json()["description"] == "Updated desc"


def test_update_video_partial(test_client):
    """Test partial update of a video."""
    create_resp = test_client.post("/api/videos", json={"title": "Full Title", "description": "Full desc"})
    video_id = create_resp.json()["id"]

    update_resp = test_client.put(f"/api/videos/{video_id}", json={"title": "Partial"})
    assert update_resp.status_code == 200
    assert update_resp.json()["title"] == "Partial"
    assert update_resp.json()["description"] == "Full desc"  # Unchanged


def test_delete_video(test_client):
    """Test deleting a video."""
    create_resp = test_client.post("/api/videos", json={"title": "Delete Me"})
    video_id = create_resp.json()["id"]

    delete_resp = test_client.delete(f"/api/videos/{video_id}")
    assert delete_resp.status_code == 204

    # Verify deletion
    get_resp = test_client.get(f"/api/videos/{video_id}")
    assert get_resp.status_code == 404


def test_delete_video_not_found(test_client):
    """Test deleting a non-existent video."""
    response = test_client.delete("/api/videos/nonexistent-id")
    assert response.status_code == 404


def test_list_videos(test_client):
    """Test listing videos with pagination."""
    # Create a few videos
    for i in range(5):
        test_client.post("/api/videos", json={"title": f"Video {i}"})

    response = test_client.get("/api/videos?page=1&page_size=3")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 3
    assert len(data["items"]) == 3


def test_list_videos_filter_by_status(test_client):
    """Test filtering videos by status."""
    test_client.post("/api/videos", json={"title": "Draft Video", "status": "draft"})
    test_client.post("/api/videos", json={"title": "Published Video", "status": "published"})
    test_client.post("/api/videos", json={"title": "Scheduled Video", "status": "scheduled"})

    response = test_client.get("/api/videos?status=published")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Published Video"


def test_list_videos_search(test_client):
    """Test searching videos by title."""
    test_client.post("/api/videos", json={"title": "Python Tutorial"})
    test_client.post("/api/videos", json={"title": "JavaScript Basics"})
    test_client.post("/api/videos", json={"title": "Python Advanced"})

    response = test_client.get("/api/videos?search=python")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


# ── Field management tests ────────────────────────────────────────────────────────

def test_list_builtin_fields(test_client, sample_table):
    """Test listing built-in fields."""
    # Get table ID from videos list
    videos_resp = test_client.get("/api/videos")
    table_id = videos_resp.json()["items"][0]["table_id"] if videos_resp.json()["items"] else None
    assert table_id is not None

    response = test_client.get(f"/api/tables/{table_id}/fields")
    assert response.status_code == 200
    fields = response.json()
    field_names = [f["name"] for f in fields]
    assert "title" in field_names
    assert "description" in field_names
    assert "status" in field_names
    assert "tags" in field_names


def test_add_custom_field(test_client, sample_table):
    """Test adding a custom field to a table."""
    videos_resp = test_client.get("/api/videos")
    table_id = videos_resp.json()["items"][0]["table_id"] if videos_resp.json()["items"] else None
    assert table_id is not None

    payload = {
        "name": "episode_number",
        "field_type": "number",
        "is_required": True,
    }
    response = test_client.post(f"/api/tables/{table_id}/fields", json=payload)
    assert response.status_code == 201
    assert response.json()["name"] == "episode_number"
    assert response.json()["field_type"] == "number"


def test_add_duplicate_field(test_client, sample_table):
    """Test that adding a duplicate field name fails."""
    videos_resp = test_client.get("/api/videos")
    table_id = videos_resp.json()["items"][0]["table_id"] if videos_resp.json()["items"] else None
    assert table_id is not None

    payload = {"name": "episode_number", "field_type": "number"}
    test_client.post(f"/api/tables/{table_id}/fields", json=payload)

    response = test_client.post(f"/api/tables/{table_id}/fields", json=payload)
    assert response.status_code == 400


def test_remove_custom_field(test_client, sample_table):
    """Test removing a custom field."""
    videos_resp = test_client.get("/api/videos")
    table_id = videos_resp.json()["items"][0]["table_id"] if videos_resp.json()["items"] else None
    assert table_id is not None

    # Add a field
    add_resp = test_client.post(
        f"/api/tables/{table_id}/fields",
        json={"name": "temp_field", "field_type": "text"},
    )
    field_id = add_resp.json()["id"]

    # Remove it
    delete_resp = test_client.delete(f"/api/tables/{table_id}/fields/{field_id}")
    assert delete_resp.status_code == 204

    # Verify it's gone
    list_resp = test_client.get(f"/api/tables/{table_id}/fields")
    field_names = [f["name"] for f in list_resp.json()]
    assert "temp_field" not in field_names


# ── Custom field validation tests ────────────────────────────────────────────────────────

def test_create_video_with_custom_fields(test_client):
    """Test creating a video with custom fields."""
    payload = {
        "title": "Custom Fields Test",
        "custom_fields": {
            "episode_number": 42,
            "is_featured": True,
            "duration_minutes": 15.5,
        },
    }
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 201
    assert response.json()["custom_fields"]["episode_number"] == 42


def test_update_video_custom_fields(test_client):
    """Test updating custom fields on a video."""
    create_resp = test_client.post("/api/videos", json={"title": "Update CF Test"})
    video_id = create_resp.json()["id"]

    update_resp = test_client.put(
        f"/api/videos/{video_id}",
        json={"custom_fields": {"episode_number": 99}},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["custom_fields"]["episode_number"] == 99


def test_list_videos_with_custom_fields(test_client):
    """Test that custom fields are returned in list response."""
    test_client.post("/api/videos", json={
        "title": "CF List Test",
        "custom_fields": {"episode": 7},
    })

    response = test_client.get("/api/videos")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["custom_fields"]["episode"] == 7


# ── Edge cases ────────────────────────────────────────────────────────

def test_create_video_empty_tags(test_client):
    """Test that empty tags are handled correctly."""
    payload = {"title": "Empty Tags", "tags": []}
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 201
    assert response.json()["tags"] == []


def test_create_video_with_tags_whitespace(test_client):
    """Test that tag whitespace is trimmed."""
    payload = {"title": "Whitespace Tags", "tags": ["  python  ", "  ", "javascript"]}
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 201
    assert response.json()["tags"] == ["python", "javascript"]


def test_create_video_with_youtube_id(test_client):
    """Test creating a video with a YouTube ID."""
    payload = {
        "title": "YT Video",
        "youtube_video_id": "dQw4w9WgXcQ",
        "status": "published",
    }
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 201
    assert response.json()["youtube_video_id"] == "dQw4w9WgXcQ"


def test_create_video_with_publish_date(test_client):
    """Test creating a video with a publish date."""
    payload = {
        "title": "Scheduled Video",
        "publish_date": "2025-06-15T10:00:00",
        "status": "scheduled",
    }
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 201
    assert response.json()["publish_date"] == "2025-06-15T10:00:00"


def test_pagination_bounds(test_client):
    """Test pagination at boundaries."""
    for i in range(5):
        test_client.post("/api/videos", json={"title": f"Page Test {i}"})

    # Page 1
    response = test_client.get("/api/videos?page=1&page_size=2")
    assert len(response.json()["items"]) == 2

    # Page 2
    response = test_client.get("/api/videos?page=2&page_size=2")
    assert len(response.json()["items"]) == 2

    # Page 3 (last page)
    response = test_client.get("/api/videos?page=3&page_size=2")
    assert len(response.json()["items"]) == 1

    # Page 4 (empty)
    response = test_client.get("/api/videos?page=4&page_size=2")
    assert response.json()["total"] == 5
    assert len(response.json()["items"]) == 0


def test_pagination_invalid_page(test_client):
    """Test that invalid page numbers are rejected."""
    response = test_client.get("/api/videos?page=0")
    assert response.status_code == 422

    response = test_client.get("/api/videos?page=-1")
    assert response.status_code == 422


def test_pagination_invalid_page_size(test_client):
    """Test that invalid page sizes are rejected."""
    response = test_client.get("/api/videos?page=1&page_size=0")
    assert response.status_code == 422

    response = test_client.get("/api/videos?page=1&page_size=101")
    assert response.status_code == 422


def test_update_nonexistent_video(test_client):
    """Test updating a non-existent video."""
    response = test_client.put(
        "/api/videos/nonexistent-id",
        json={"title": "Ghost"},
    )
    assert response.status_code == 404


def test_cors_headers(test_client):
    """Test that CORS headers are present."""
    response = test_client.options("/api/videos")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_video_status_enum(test_client):
    """Test that status values are properly validated."""
    payload = {"title": "Bad Status", "status": "invalid_status"}
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 422


def test_video_title_too_long(test_client):
    """Test that overly long titles are rejected."""
    payload = {"title": "x" * 501}
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 422


def test_video_title_min_length(test_client):
    """Test that empty titles are rejected."""
    payload = {"title": ""}
    response = test_client.post("/api/videos", json=payload)
    assert response.status_code == 422
