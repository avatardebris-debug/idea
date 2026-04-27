"""Custom field management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TableMetadata, TableField, FieldTypeId
from ..schemas import FieldCreate, FieldResponse

router = APIRouter(prefix="/api/tables", tags=["fields"])


def _get_table(db: Session, table_id: str) -> TableMetadata:
    """Get table by ID or raise 404."""
    table = db.query(TableMetadata).filter(TableMetadata.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.get("/{table_id}/fields", response_model=list[FieldResponse])
def list_fields(table_id: str, db: Session = Depends(get_db)):
    """List all fields (built-in + custom) for a table."""
    table = _get_table(db, table_id)

    # Built-in fields
    builtin_fields = [
        FieldResponse(
            id="id",
            name="ID",
            field_type=FieldTypeId.TEXT,
            options=None,
            is_required=True,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="title",
            name="Title",
            field_type=FieldTypeId.TEXT,
            options=None,
            is_required=True,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="description",
            name="Description",
            field_type=FieldTypeId.TEXT,
            options=None,
            is_required=False,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="status",
            name="Status",
            field_type=FieldTypeId.SELECT,
            options=["draft", "scheduled", "publishing", "published", "failed"],
            is_required=False,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="tags",
            name="Tags",
            field_type=FieldTypeId.TAGS,
            options=None,
            is_required=False,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="publish_date",
            name="Publish Date",
            field_type=FieldTypeId.DATE,
            options=None,
            is_required=False,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="thumbnail_url",
            name="Thumbnail URL",
            field_type=FieldTypeId.URL,
            options=None,
            is_required=False,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="youtube_video_id",
            name="YouTube Video ID",
            field_type=FieldTypeId.TEXT,
            options=None,
            is_required=False,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="custom_fields",
            name="Custom Fields",
            field_type=FieldTypeId.OBJECT,
            options=None,
            is_required=False,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="created_at",
            name="Created At",
            field_type=FieldTypeId.DATE,
            options=None,
            is_required=False,
            is_deleted=False,
            created_at=table.created_at,
        ),
        FieldResponse(
            id="updated_at",
            name="Updated At",
            field_type=FieldTypeId.DATE,
            options=None,
            is_required=False,
            is_deleted=False,
            created_at=table.created_at,
        ),
    ]

    # Custom fields (not deleted)
    custom_fields = [
        FieldResponse.model_validate(f)
        for f in table.fields
        if not f.is_deleted
    ]

    return builtin_fields + custom_fields


@router.post("/{table_id}/fields", response_model=FieldResponse, status_code=201)
def add_field(table_id: str, field_data: FieldCreate, db: Session = Depends(get_db)):
    """Add a custom field to a table."""
    table = _get_table(db, table_id)

    # Check name uniqueness (case-insensitive)
    existing = [
        f for f in table.fields
        if not f.is_deleted and f.name.lower() == field_data.name.lower()
    ]
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Field '{field_data.name}' already exists",
        )

    field = TableField(
        table_id=table_id,
        name=field_data.name,
        field_type=field_data.field_type,
        options=field_data.options,
        is_required=field_data.is_required,
    )
    db.add(field)
    db.commit()
    db.refresh(field)
    return FieldResponse.model_validate(field)


@router.delete("/{table_id}/fields/{field_id}", status_code=204)
def remove_field(table_id: str, field_id: str, db: Session = Depends(get_db)):
    """Soft-delete a custom field (data preserved, column hidden)."""
    field = db.query(TableField).filter(TableField.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")

    field.is_deleted = True
    db.commit()
