from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import ContentRecord, ContentTable
from app.schemas import RecordCreate, RecordUpdate
from typing import Optional


def get_records(
    db: Session,
    table_id: int,
    skip: int = 0,
    limit: int = 50,
    filter_status: Optional[str] = None,
    filter_tags: Optional[str] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: str = "asc",
) -> tuple[list[ContentRecord], int]:
    """Get paginated records with optional filtering and sorting."""
    query = db.query(ContentRecord).filter(ContentRecord.table_id == table_id)

    # Apply filters
    if filter_status:
        query = query.filter(ContentRecord.status == filter_status)
    if filter_tags:
        # Simple tag filtering - checks if any tag in the filter matches
        query = query.filter(ContentRecord.data["tags"].contains(filter_tags))

    # Get total count before pagination
    total = query.count()

    # Apply sorting
    sort_column = getattr(ContentRecord, sort_by, ContentRecord.created_at)
    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    query = query.order_by(sort_column)

    # Apply pagination
    records = query.offset(skip).limit(limit).all()

    return records, total


def get_record(db: Session, record_id: int) -> ContentRecord | None:
    return db.query(ContentRecord).filter(ContentRecord.id == record_id).first()


def create_record(db: Session, record_data: RecordCreate) -> ContentRecord:
    record = ContentRecord(
        table_id=record_data.table_id,
        data=record_data.data,
        status=record_data.status or "draft",
        scheduled_date=record_data.scheduled_date,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_record(db: Session, record_id: int, record_data: RecordUpdate) -> ContentRecord | None:
    record = get_record(db, record_id)
    if not record:
        return None

    if record_data.data is not None:
        record.data = record_data.data
    if record_data.status is not None:
        record.status = record_data.status
    if record_data.scheduled_date is not None:
        record.scheduled_date = record_data.scheduled_date

    db.commit()
    db.refresh(record)
    return record


def delete_record(db: Session, record_id: int) -> bool:
    record = get_record(db, record_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def bulk_create_records(db: Session, records_data: list[RecordCreate]) -> list[ContentRecord]:
    """Create multiple records in a single transaction."""
    records = []
    for record_data in records_data:
        record = ContentRecord(
            table_id=record_data.table_id,
            data=record_data.data,
            status=record_data.status or "draft",
            scheduled_date=record_data.scheduled_date,
        )
        records.append(record)
    db.add_all(records)
    db.commit()
    for record in records:
        db.refresh(record)
    return records
