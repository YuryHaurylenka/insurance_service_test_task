from fastapi import APIRouter
from app.api.endpoints import tariffs_router, insurance_router

router = APIRouter()

router.include_router(tariffs_router, prefix="/tariffs", tags=["Tariffs"])
router.include_router(insurance_router, prefix="/insurance", tags=["Insurance"])
