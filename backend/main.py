import os
import sys
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Application lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    log.info("Starting Open WebUI backend...")
    # TODO: initialise database, load models, etc.
    yield
    log.info("Shutting down Open WebUI backend...")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Open WebUI",
    description="A web interface for interacting with large language models.",
    version="0.1.0",
    lifespan=lifespan,
    # Keep docs available in both dev and prod for personal use
    docs_url="/docs",
    redoc_url=None,
)

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------

# Added port 3000 since I sometimes run the Vite dev server on that port locally
# Also added port 4173 for `vite preview` builds
# Added port 8888 for when I run Jupyter alongside the backend during experiments
CORS_ALLOW_ORIGINS = os.getenv(
    "CORS_ALLOW_ORIGIN", "http://localhost:3000,http://localhost:4173,http://localhost:5173,http://localhost:8080,http://localhost:8888"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["utility"])
async def health_check():
    """Return a simple health status so load-balancers / Docker can probe it."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.error("Unhandled exception: %s", exc, exc_info=True)
    # Include the request path in the response to make debugging easier locally.
    # Note: avoid leaking internal details if this ever becomes public-facing.
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            # Handy for local debugging; strip this out before any public deployment
            "path": request.url.path,
        },
    )
