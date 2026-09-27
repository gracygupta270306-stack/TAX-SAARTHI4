from fastapi import APIRouter, HTTPException

from app.services.analysis import analyze_transactions
from app.services.exporter import build_export_payload
from app.services.human_review import build_human_review_cases
from app.services.profiles import build_profile_summary
from app.services.session_store import get_transactions

router = APIRouter(prefix="/api", tags=["export"])


@router.get("/export")
def export_report() -> dict:
    try:
        transactions = get_transactions()
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error

    analysis = analyze_transactions(transactions)
    profile = build_profile_summary(transactions)
    review_cases = build_human_review_cases(analysis)
    return build_export_payload(analysis, profile, review_cases)
