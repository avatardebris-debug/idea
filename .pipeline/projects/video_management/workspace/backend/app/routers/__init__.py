from .videos import router as videos_router
from .fields import router as fields_router
from .tables import router as tables_router

__all__ = ["videos_router", "fields_router", "tables_router"]
