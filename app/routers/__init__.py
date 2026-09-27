from fastapi import APIRouter

from app.routers.auth import router as auth_router
from app.routers.config import router as config_router
from app.routers.messages import router as messages_router
from app.routers.reservations import router as reservations_router
from app.routers.watch_items import router as watch_items_router

api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(config_router)
api_router.include_router(messages_router)
api_router.include_router(reservations_router)
api_router.include_router(watch_items_router)
