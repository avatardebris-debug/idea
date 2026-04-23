from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import RecordCreate, RecordUpdate, RecordResponse
from app.services import record_service
from typing import Optional

router = APIRouter()


@router.post("/", response_model=RecordResponse, status_code=201)
def create_record(record_data: RecordCreate, db: Session = Depends(get_db)):
    record = record_service.create_record(db, record_data)
    return record


@router.get("/", response_model=dict)
def list_records(
    table_id: int,
    skip: int = 0,
    limit: int = 50,
    filter_status: Optional[str] = Query(None, alias="filter"),
    filter_tags: Optional[str] = None,
    sort_by: str = Query("created_at"),
    sort_order: str = Query("asc"),
    db: Session = Depends(get_db),
):
    records, total = record_service.get_records(
        db,
        table_id,
        skip=skip,
        limit=limit,
        filter_status=filter_status,
        filter_tags=filter_tags,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {
        "items": records,
        "total": total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
    }


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = record_service.get_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.put("/{record_id}", response_model=RecordResponse)
def update_record(record_id: int, record_data: RecordUpdate, db: Session = Depends(get_db)):
    record = record_service.update_record(db, record_id, record_data)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.delete("/{record_id}", status_code=204)
def delete_record(record_id: int, db: Session = Depends(get_db)):
    success = record_service.delete_record(db, record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    return None
