"""
apps/scribeswell/backend/main.py — FastAPI application entry point

Run locally:
    cd apps/scribeswell/backend
    uvicorn main:app --reload --port 8000

OpenAPI docs:
    http://localhost:8000/docs
    http://localhost:8000/redoc
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
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


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
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

from routers import bible as bible_router  # noqa: E402

app.include_router(bible_router.router, prefix="/api/bible", tags=["bible"])
