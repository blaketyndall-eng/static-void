from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str]:
    return {"status": "ready"}


@router.get("/meta")
def meta() -> dict[str, str]:
    return {
        "service": "decision-intelligence-console",
        "surface": "foundation-scaffold",
    }
