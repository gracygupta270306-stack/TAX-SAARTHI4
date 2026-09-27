from fastapi import APIRouter, HTTPException

from app.services.analysis import analyze_transactions
from app.services.session_store import get_transactions

router = APIRouter(prefix="/api", tags=["analysis"])


@router.get("/analyze")
def analyze() -> dict:
    try:
        transactions = get_transactions()
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    return analyze_transactions(transactions)
