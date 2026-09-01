from fastapi import APIRouter

from app.api.routes import (
    censusdata,
    dashboard,
    entities,
    ingest,
    items,
    local_indicators,
    login,
    private,
    reference,
    reports,
    schools,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(censusdata.router)
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
api_router.include_router(reference.router)
api_router.include_router(entities.router)
api_router.include_router(reports.router)
api_router.include_router(dashboard.router)
api_router.include_router(local_indicators.router)
api_router.include_router(ingest.router)

if settings.FASTAPI_ENV == "development":
    api_router.include_router(private.router)
