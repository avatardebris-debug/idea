"""Table management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import TableMetadata, TableField, FieldTypeId
from ..schemas import TableRequest, TableResponse

router = APIRouter(prefix="/api/tables", tags=["tables"])


@router.post("", response_model=TableResponse)
def create_table(table_request: TableRequest, db: Session = Depends(get_db)):
    """Create a new table."""
    # Check if table name already exists
    existing = db.query(TableMetadata).filter(
        TableMetadata.name == table_request.name
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Table name already exists")

    table = TableMetadata(
        name=table_request.name,
        description=table_request.description,
    )
    db.add(table)
    db.commit()
    db.refresh(table)

    # Add built-in fields
    builtin_fields = [
        TableField(table_id=table.id, name="title", field_type=FieldTypeId.TEXT, is_required=True),
        TableField(table_id=table.id, name="description", field_type=FieldTypeId.TEXT, is_required=False),
        TableField(table_id=table.id, name="status", field_type=FieldTypeId.SELECT, is_required=True, options=["draft", "published", "scheduled"]),
        TableField(table_id=table.id, name="tags", field_type=FieldTypeId.TAGS, is_required=False),
        TableField(table_id=table.id, name="publish_date", field_type=FieldTypeId.DATE, is_required=False),
        TableField(table_id=table.id, name="thumbnail_url", field_type=FieldTypeId.URL, is_required=False),
        TableField(table_id=table.id, name="youtube_video_id", field_type=FieldTypeId.TEXT, is_required=False),
        TableField(table_id=table.id, name="custom_fields", field_type=FieldTypeId.OBJECT, is_required=False),
        TableField(table_id=table.id, name="created_at", field_type=FieldTypeId.DATE, is_required=False),
        TableField(table_id=table.id, name="updated_at", field_type=FieldTypeId.DATE, is_required=False),
    ]
    db.add_all(builtin_fields)
    db.commit()
    db.refresh(table)

    return TableResponse.model_validate(table)


@router.get("", response_model=list[TableResponse])
def list_tables(db: Session = Depends(get_db)):
    """List all tables."""
    tables = db.query(TableMetadata).all()
    return [TableResponse.model_validate(t) for t in tables]


@router.get("/{table_id}", response_model=TableResponse)
def get_table(table_id: str, db: Session = Depends(get_db)):
    """Get a specific table by ID."""
    table = db.query(TableMetadata).filter(TableMetadata.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return TableResponse.model_validate(table)


@router.delete("/{table_id}", status_code=204)
def delete_table(table_id: str, db: Session = Depends(get_db)):
    """Delete a table (hard delete)."""
    table = db.query(TableMetadata).filter(TableMetadata.id == table_id).first()
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    db.delete(table)
    db.commit()
