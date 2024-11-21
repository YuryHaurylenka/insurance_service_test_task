__all__ = (
    "tariffs_router",
    "insurance_router",
)

from .insurance import router as insurance_router
from .tariff import router as tariffs_router
