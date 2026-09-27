from fastapi import APIRouter, HTTPException

from app.tax_engine.calculator import calculate_tax

router = APIRouter(prefix="/api", tags=["tax"])


@router.post("/tax/calculate")
def calculate_tax_endpoint(payload: dict) -> dict:
    try:
        result = calculate_tax(payload)
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("warnings", ["Tax calculation failed."])[0])
        return result
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc)) from exc
