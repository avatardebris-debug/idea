from sqlalchemy.orm import Session
from app.models import ContentTable, ColumnDefinition
from app.schemas import TableCreate
import json


def get_tables(db: Session, workspace_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(ContentTable)
        .filter(ContentTable.workspace_id == workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_table(db: Session, table_id: int) -> ContentTable | None:
    return db.query(ContentTable).filter(ContentTable.id == table_id).first()


def create_table(db: Session, table_data: TableCreate) -> ContentTable:
    # Validate column definitions
    valid_types = {"text", "tags", "status", "date", "media_url"}
    for col in table_data.column_definitions:
        if col.type not in valid_types:
            raise ValueError(f"Invalid column type: {col.type}. Must be one of {valid_types}")

    table = ContentTable(
        name=table_data.name,
        workspace_id=table_data.workspace_id,
        column_definitions=[col.model_dump() for col in table_data.column_definitions],
    )
    db.add(table)
    db.commit()
    db.refresh(table)
    return table


def update_table(db: Session, table_id: int, **kwargs) -> ContentTable | None:
    table = get_table(db, table_id)
    if not table:
        return None
    for key, value in kwargs.items():
        if hasattr(table, key):
            setattr(table, key, value)
    db.commit()
    db.refresh(table)
    return table


def delete_table(db: Session, table_id: int) -> bool:
    table = get_table(db, table_id)
    if not table:
        return False
    db.delete(table)
    db.commit()
    return True
