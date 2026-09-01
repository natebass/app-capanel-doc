"""FastAPI application entry point.

Creates the :class:`FastAPI` application instance, configures CORS
middleware, registers the API router, and defines the application
lifespan for startup/shutdown hooks.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from app.api.main import api_router
from app.core.config import settings
from app.scripts.initial_data import main as init_data_main


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
        Control the running application between startup and shutdown.
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
    allow_origins=settings.all_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


def api_links() -> dict[str, str]:
    """Collect the paths worth pointing a lost caller at.

    Returns:
        A mapping of link name to path, derived from
        :data:`Settings.API_V1_STR` so the two stay in step.
    """
    return {
        "interactiveDocs": "/docs",
        "referenceDocs": "/redoc",
        "openapiSchema": f"{settings.API_V1_STR}/openapi.json",
        "healthCheck": f"{settings.API_V1_STR}/utils/health-check/",
    }


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str | dict[str, str]]:
    """Welcome a caller at the API root instead of returning a bare 404.

    The API itself is served under :data:`Settings.API_V1_STR`, so a
    request to ``/`` would otherwise match no route.  Introduce the
    project and point the caller at the documentation instead.

    Returns:
        A greeting, a short description of the project, and the links
        from :func:`api_links`.
    """
    return {
        "message": f"You have successfully connected to the {settings.PROJECT_NAME} API! The endpoints live under {settings.API_V1_STR}. Browse them "
        "interactively at /docs, or read the reference at /redoc.",
        "links": api_links(),
    }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Answer an unmatched path with directions rather than ``Not Found``.

    A 404 raised by a route carries its own message (``"School not
    found"`` and friends), so that detail is passed through untouched.
    Only Starlette's generic "no route matched" 404 is replaced with the
    friendlier body.

    Args:
        request: The request that matched no route.
        exc: The 404 being handled.

    Returns:
        A :class:`JSONResponse` carrying either the route's own detail or
        a welcome message with the links from :func:`api_links`.
    """
    detail = getattr(exc, "detail", "Not Found")
    if detail != "Not Found":
        return JSONResponse(
            status_code=404,
            content={"detail": detail},
            headers=getattr(exc, "headers", None),
        )
    return JSONResponse(
        status_code=404,
        content={
            "message": (
                f"Sorry, there is nothing at {request.url.path} — but you have successfully connected "
                f"to the {settings.PROJECT_NAME} API!"
            ),
        },
    )
