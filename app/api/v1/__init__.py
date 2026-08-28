from fastapi import APIRouter

from app.api.v1.borrowings import router as borrowings_router
from app.api.v1.items import router as items_router
from app.api.v1.plans import router as plans_router
from app.api.v1.users import router as users_router

api_router = APIRouter()
api_router.include_router(plans_router)
api_router.include_router(users_router)
api_router.include_router(items_router)
api_router.include_router(borrowings_router)

__all__ = ["api_router"]
