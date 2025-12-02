# app/routes/__init__.py
from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .habits import router as habits_router
from .settings import router as settings_router

__all__ = ["auth_router", "dashboard_router", "habits_router", "settings_router"]