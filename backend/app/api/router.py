"""HTTP API routers."""

from fastapi import APIRouter

from app.api.routes import health, patients, reports

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
