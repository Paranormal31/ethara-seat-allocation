from .employees import router as employees_router
from .projects import router as projects_router
from .seats import router as seats_router
from .dashboard import router as dashboard_router
from .ai import router as ai_router

__all__ = ["employees_router", "projects_router", "seats_router", "dashboard_router", "ai_router"]
