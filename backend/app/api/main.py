from fastapi import APIRouter

from app.api.routes import (
    academic_indicators,
    censusdata,
    items,
    login,
    private,
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
api_router.include_router(academic_indicators.router)


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
