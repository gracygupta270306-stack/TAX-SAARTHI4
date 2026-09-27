import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.routes.upload import router as upload_router
from app.routes.analysis import router as analysis_router
from app.routes.profile import router as profile_router
from app.routes.review import router as review_router
from app.routes.export import router as export_router
from app.routes.tax import router as tax_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="TaxSaarthi API",
    description="AI-powered financial decision support prototype",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1):(4173|4174|5173|3000|9000|9001|9002)(?:\:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(analysis_router)
app.include_router(profile_router)
app.include_router(review_router)
app.include_router(export_router)
app.include_router(tax_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exception: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exception.status_code,
        content={"detail": exception.detail},
        headers=exception.headers,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exception: Exception) -> JSONResponse:
    logger.error(
        "Unhandled API exception",
        exc_info=(type(exception), exception, exception.__traceback__),
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred."},
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
