from fastapi import APIRouter

from app.api.endpoints import insurance_router, tariffs_router

router = APIRouter()

router.include_router(tariffs_router, prefix="/tariffs", tags=["Tariffs"])
router.include_router(insurance_router, prefix="/insurance", tags=["Insurance"])
