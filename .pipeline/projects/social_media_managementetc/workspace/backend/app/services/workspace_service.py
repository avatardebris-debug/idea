from sqlalchemy.orm import Session
from app.models import Workspace, User
from app.schemas import WorkspaceCreate


def get_user(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, email: str, name: str | None = None) -> User:
    user = User(email=email, name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_workspaces(db: Session, owner_id: int, skip: int = 0, limit: int = 100):
    return (
        db.query(Workspace)
        .filter(Workspace.owner_id == owner_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_workspace(db: Session, workspace_id: int) -> Workspace | None:
    return db.query(Workspace).filter(Workspace.id == workspace_id).first()


def create_workspace(db: Session, workspace_data: WorkspaceCreate, owner_id: int) -> Workspace:
    workspace = Workspace(
        name=workspace_data.name,
        description=workspace_data.description,
        owner_id=owner_id,
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


def update_workspace(db: Session, workspace_id: int, **kwargs) -> Workspace | None:
    workspace = get_workspace(db, workspace_id)
    if not workspace:
        return None
    for key, value in kwargs.items():
        if hasattr(workspace, key):
            setattr(workspace, key, value)
    db.commit()
    db.refresh(workspace)
    return workspace


def delete_workspace(db: Session, workspace_id: int) -> bool:
    workspace = get_workspace(db, workspace_id)
    if not workspace:
        return False
    db.delete(workspace)
    db.commit()
    return True
