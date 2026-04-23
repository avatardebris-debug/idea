from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import workspaces, tables, records, auth

app = FastAPI(title="Social Media Management Platform", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
Base.metadata.create_all(bind=engine)

app.include_router(workspaces.router, prefix="/api/workspaces", tags=["workspaces"])
app.include_router(tables.router, prefix="/api/tables", tags=["tables"])
app.include_router(records.router, prefix="/api/records", tags=["records"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
