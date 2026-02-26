from typing import Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse
from models import StandardApiResponse, StandardErrorResponse
from routers import image

app = FastAPI(
    title="Multi-Res API",
    description="Image processing API for Multi-Res",
    version="1.0.0",
    redoc_url=None,
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=StandardErrorResponse(message=str(exc.detail)).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    message = "; ".join(
        f"{' -> '.join(str(loc) for loc in e['loc'])}: {e['msg']}"
        for e in errors
    )
    return JSONResponse(
        status_code=422,
        content=StandardErrorResponse(message=message).model_dump(),
    )


app.include_router(image.router)


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    error_schema = {
        "type": "object",
        "properties": {
            "status": {"type": "boolean", "default": False},
            "message": {"type": "string"},
        },
        "required": ["status", "message"],
    }

    for path in schema.get("paths", {}).values():
        for operation in path.values():
            if "responses" in operation:
                operation["responses"]["422"] = {
                    "description": "Validation Error",
                    "content": {"application/json": {"schema": error_schema}},
                }
                for status_code in ("400", "413", "415"):
                    if status_code in operation["responses"]:
                        operation["responses"][status_code] = {
                            "description": operation["responses"][status_code].get("description", "Error"),
                            "content": {"application/json": {"schema": error_schema}},
                        }

    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi  # type: ignore[method-assign]


@app.get("/", response_model=StandardApiResponse[None])
async def root() -> StandardApiResponse[None]:
    """Root endpoint returning welcome message."""
    return StandardApiResponse(
        status=True,
        message="Welcome to the multi res api."
    )


@app.get("/redoc", include_in_schema=False, response_class=HTMLResponse)
async def redoc_html():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js",
    )
