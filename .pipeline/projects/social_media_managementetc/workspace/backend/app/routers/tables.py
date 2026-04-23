from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import TableCreate, TableResponse
from app.services import table_service

router = APIRouter()


@router.post("/", response_model=TableResponse, status_code=201)
def create_table(table_data: TableCreate, db: Session = Depends(get_db)):
    try:
        table = table_service.create_table(db, table_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return table


@router.get("/", response_model=dict)
def list_tables(workspace_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    tables = table_service.get_tables(db, workspace_id, skip, limit)
    total = len(table_service.get_tables(db, workspace_id, 0, 1000000000))
    return {
        "items": tables,
        "total": total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "limit": limit,
        "total_pages": (total + limit - 1) // limit if limit > 0 else 0,
    }


@router.get("/{table_id}", response_model=TableResponse)
def get_table(table_id: int, db: Session = Depends(get_db)):
    table = table_service.get_table(db, table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.put("/{table_id}", response_model=TableResponse)
def update_table(table_id: int, table_data: TableCreate, db: Session = Depends(get_db)):
    table = table_service.update_table(db, table_id, name=table_data.name, column_definitions=table_data.column_definitions)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    return table


@router.delete("/{table_id}", status_code=204)
def delete_table(table_id: int, db: Session = Depends(get_db)):
    success = table_service.delete_table(db, table_id)
    if not success:
        raise HTTPException(status_code=404, detail="Table not found")
    return None
