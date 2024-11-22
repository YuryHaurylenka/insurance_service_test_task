from fastapi import FastAPI
from starlette.responses import RedirectResponse

from app.api.router import router
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.project_name,
    description="Service for managing tariffs and calculating insurance",
    version=settings.version,
    debug=settings.debug,
)

app.include_router(router, prefix=settings.api_prefix)


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
