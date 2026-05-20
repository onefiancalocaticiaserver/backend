from fastapi import APIRouter

from app.api.v1.endpoints import admin, health, publico

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(publico.router)
api_router.include_router(admin.router)
