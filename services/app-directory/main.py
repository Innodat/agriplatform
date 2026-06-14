"""
services/app-directory/main.py — App Directory FastAPI service.

Run locally:
    cd services/app-directory
    uvicorn main:app --reload --port 8001

OpenAPI docs:
    http://localhost:8001/docs
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings
from routers import apps as apps_router

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="App Directory API",
    description="Cross-app entitlement and discovery service. Returns the apps a user can access.",
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
    allow_methods=["GET", "OPTIONS"],
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
        content={"error": "Validation error", "details": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health():
    """Liveness probe."""
    return {"status": "ok", "env": settings.app_env, "service": "app-directory"}


@app.get("/", tags=["system"])
async def root():
    return {"message": "App Directory API", "docs": "/docs"}

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(apps_router.router, prefix="/api")
