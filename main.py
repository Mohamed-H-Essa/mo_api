import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import async_session_maker, engine
from routers import collections, bookmarks

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(
    title="Bookmarks API",
    description="A simple link-saving service with collections",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "not_found", "detail": str(exc.detail) if hasattr(exc, "detail") else "Resource not found"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Let FastAPI's default 422 behavior pass through
    errors = exc.errors()
    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )


@app.exception_handler(Exception)
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(f"Internal error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": "An unexpected error occurred"},
    )


@app.get("/health")
async def health_check():
    try:
        async with async_session_maker() as session:
            await session.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except SQLAlchemyError as e:
        logger.error(f"Health check DB error: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "degraded", "db": "unreachable"},
        )


app.include_router(collections.router, prefix="/collections", tags=["collections"])
app.include_router(bookmarks.router, tags=["bookmarks"])
