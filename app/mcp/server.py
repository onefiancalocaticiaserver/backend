from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from app.core.config import get_settings

settings = get_settings()
app = FastAPI(title="one-fianca-mcp", version=settings.app_version)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "one-mcp"}


@app.post("/mcp")
def mcp_placeholder() -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        content={"detail": "mcp_tools_not_implemented_in_marco_1"},
    )
