from fastapi import APIRouter, HTTPException, status

from app.db.health import check_database_connection

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "one-api"}


@router.get("/health/db")
def health_db() -> dict[str, str]:
    if not check_database_connection():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database_unavailable",
        )
    return {"status": "ok", "database": "connected"}
