"""FastAPI application entry point.

Creates the :class:`FastAPI` application instance, configures CORS
middleware, registers the API router, and defines the application
lifespan for startup/shutdown hooks.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.scripts.initial_data import main as init_data_main

# Candidate locations for the built frontend, in priority order.  The first is
# the single-container layout used by the main application repository, where the
# build output is copied into the backend package at image build time.  The
# second is this repository's layout, where Vite writes to ``frontend/dist`` at
# the repository root.  Neither is required: this repository is development-only
# and serves the Sphinx docs in production, so a missing build is not an error.
_FRONTEND_CANDIDATES = (
    Path(__file__).parent / "frontend",
    Path(__file__).parents[2] / "frontend" / "dist",
)


def resolve_frontend_dir() -> Path | None:
    """Locate the built frontend to serve, if one is present.

    Returns:
        The first existing directory in :data:`_FRONTEND_CANDIDATES`, or
        ``None`` when no frontend build is available.
    """
    return next((path for path in _FRONTEND_CANDIDATES if path.is_dir()), None)


def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate a deterministic OpenAPI operation ID for a route.

    The ID is formed as ``"{tag}-{route_name}"``, using the first tag
    assigned to the route or ``"default"`` when no tags are present.

    Args:
        route: The :class:`APIRoute` to generate an ID for.

    Returns:
        A unique string identifier for the route's OpenAPI operation.
    """
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


if settings.SENTRY_DSN and settings.FASTAPI_ENV != "development":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:  # noqa: ARG001
    """Manage application startup and shutdown events.

    On startup the data-import pipeline is triggered (subject to
    environment-variable flags).  Shutdown is currently a no-op.

    Args:
        app: The :class:`FastAPI` application instance.

    Yields:
        Control to the running application between startup and shutdown.
    """
    init_data_main()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

FRONTEND_DIR = resolve_frontend_dir()
if FRONTEND_DIR is not None:
    app.frontend("/", directory=FRONTEND_DIR, check_dir=True)
