from fastapi import APIRouter, HTTPException

from app.services.analysis import analyze_transactions
from app.services.human_review import build_human_review_cases
from app.services.session_store import get_transactions

router = APIRouter(prefix="/api", tags=["review"])


@router.get("/review")
def get_human_review_cases() -> dict:
    try:
        transactions = get_transactions()
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    analysis = analyze_transactions(transactions)
    return {
        "cases": build_human_review_cases(analysis),
        "count": len(build_human_review_cases(analysis)),
    }
