from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AccountCreate, AccountResponse
from app.services import workspace_service

router = APIRouter()


@router.post("/twitter/connect", response_model=AccountResponse, status_code=201)
def connect_twitter_account(workspace_id: int, db: Session = Depends(get_db)):
    """Initiate Twitter OAuth2 connection. Returns authorization URL."""
    workspace = workspace_service.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # For MVP, simulate OAuth flow
    # In production, redirect to Twitter OAuth URL
    return {
        "id": 0,
        "workspace_id": workspace_id,
        "platform": "twitter",
        "account_name": None,
        "account_id": None,
        "is_connected": False,
        "created_at": None,
        "_auth_url": f"https://twitter.com/i/oauth2/authorize?workspace={workspace_id}",
    }


@router.post("/twitter/callback", response_model=AccountResponse)
def twitter_oauth_callback(workspace_id: int, code: str, db: Session = Depends(get_db)):
    """Handle Twitter OAuth2 callback. Exchange code for tokens."""
    workspace = workspace_service.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    # For MVP, simulate token exchange
    # In production, exchange code for access_token and refresh_token
    return {
        "id": 0,
        "workspace_id": workspace_id,
        "platform": "twitter",
        "account_name": "demo_user",
        "account_id": "demo_twitter_id",
        "is_connected": True,
        "created_at": None,
    }


@router.post("/instagram/connect", response_model=AccountResponse, status_code=201)
def connect_instagram_account(workspace_id: int, db: Session = Depends(get_db)):
    """Initiate Instagram OAuth2 connection."""
    workspace = workspace_service.get_workspace(db, workspace_id)
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    return {
        "id": 0,
        "workspace_id": workspace_id,
        "platform": "instagram",
        "account_name": None,
        "account_id": None,
        "is_connected": False,
        "created_at": None,
        "_auth_url": f"https://instagram.com/oauth/authorize?workspace={workspace_id}",
    }


@router.delete("/{account_id}", status_code=204)
def disconnect_account(account_id: int, db: Session = Depends(get_db)):
    """Disconnect a social media account."""
    # For MVP, just return success
    return None
