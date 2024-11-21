from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings

app = FastAPI(
    title=settings.project_name,
    description="Service for managing tariffs and calculating insurance",
    version=settings.version,
    debug=settings.debug,
)

app.include_router(router, prefix=settings.api_prefix)
