from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Workspace
from app.schemas import WorkspaceCreate, WorkspaceResponse, PaginatedResponse
from app.services import workspace_service

router = APIRouter()


@router.post("/", response_model=WorkspaceResponse, status_code=201)
def create_workspace(workspace_data: WorkspaceCreate, db: Session = Depends(get_db)):
    # For MVP, use a fixed owner_id (1). In production, this would come from auth.
    owner_id = 1
    workspace = workspace_service.create_workspace(db, workspace_data, owner_id)
    return workspace


@router.get("/", response_model=dict)
def list_workspaces(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    owner_id = 1
    workspaces = workspace_service.get_workspaces(db, owner_id, skip, limit)
    total = workspace_service.get_workspaces(db, owner_id, 0, 1000000000)
    total_count = len(total)
    return {
        "items": workspaces,
        "total": total_count,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit if limit > 0 else 0,
    }


@router.get("/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(workspace_id: int, db: Session = Depends(get_db)):
    workspace = workspace_service.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.put("/{workspace_id}", response_model=WorkspaceResponse)
def update_workspace(workspace_id: int, workspace_data: WorkspaceCreate, db: Session = Depends(get_db)):
    workspace = workspace_service.update_workspace(db, workspace_id, name=workspace_data.name, description=workspace_data.description)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.delete("/{workspace_id}", status_code=204)
def delete_workspace(workspace_id: int, db: Session = Depends(get_db)):
    success = workspace_service.delete_workspace(db, workspace_id)
    if not success:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return None
