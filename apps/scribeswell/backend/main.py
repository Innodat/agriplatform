"""
apps/scribeswell/backend/main.py — FastAPI application entry point

Run locally:
    cd apps/scribeswell/backend
    uvicorn main:app --reload --port 8000

OpenAPI docs:
    http://localhost:8000/docs
    http://localhost:8000/redoc
"""
import logging
from contextlib import asynccontextmanager
from database import open_database, close_database, DatabaseUnavailable

from config import settings
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# ── App ───────────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app):
    open_database()
    try:
        yield
    finally:
        close_database()


app = FastAPI(
    lifespan=lifespan,
    title="Scribeswell API",
    description="Hebrew Bible study API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ── CORS ──────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Error handlers ────────────────────────────────────────────────────────────

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
        },
    )


@app.exception_handler(DatabaseUnavailable)
async def database_exception_handler(request: Request, exc: DatabaseUnavailable):
    logging.getLogger(__name__).error('{"service":"scribeswell","action":"database","outcome":"failed","code":"database_unavailable"}')
    return JSONResponse(status_code=503, content={"error": "Database temporarily unavailable", "code": "database_unavailable"})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).error('{"service":"scribeswell","action":"request","outcome":"failed","code":"unhandled_error"}')
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health():
    """Liveness probe — returns 200 when the server is running."""
    return {"status": "ok", "env": settings.app_env}


@app.get("/", tags=["system"])
async def root():
    return {"message": "Scribeswell API", "docs": "/docs"}

# ── Routers ───────────────────────────────────────────────────────────────────

from routers import bible as bible_router

app.include_router(bible_router.router, prefix="/api/bible", tags=["bible"])

# Private routes are absent by default; no schema work runs at startup.
if settings.scribeswell_studies_enabled:
    from personal_notes_access import StudiesAccess
    from personal_notes_storage import PersonalNotesStorage
    from personal_notes_router import build_router
    app.include_router(build_router(
        StudiesAccess(settings.scribeswell_studies_access_url, settings.scribeswell_studies_service_key.get_secret_value()),
        PersonalNotesStorage(settings.scribeswell_studies_database_url.get_secret_value())))

    @app.middleware("http")
    async def contain_private_errors(request: Request, call_next):
        private = request.url.path == '/api/studies' or request.url.path.startswith(('/api/studies/', '/api/operations/'))
        try:
            response = await call_next(request)
        except Exception:
            if not private:
                raise
            return JSONResponse({'error':'Request could not be completed','code':'studies_storage_unavailable','details':None},status_code=503,headers={'Cache-Control':'private, no-store'})
        if private:
            if response.status_code in (404,405,422):
                return JSONResponse({'error':'Request could not be completed','code':'resource_unavailable' if response.status_code in (404,405) else 'scribeswell_personal_notes_input_invalid','details':None},status_code=404 if response.status_code in (404,405) else 400,headers={'Cache-Control':'private, no-store'})
            response.headers['Cache-Control']='private, no-store'
        return response
