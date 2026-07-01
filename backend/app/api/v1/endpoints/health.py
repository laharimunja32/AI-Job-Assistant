from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Health check", response_description="Application health status")
def health_check() -> dict[str, str]:
    """Return a simple health status payload."""
    return {"status": "ok"}
