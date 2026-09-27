from fastapi import APIRouter

from app.services.profiles import build_profile_summary
from app.services.session_store import get_transactions

router = APIRouter(prefix="/api", tags=["profiles"])


@router.get("/profiles")
def get_profiles() -> dict:
    transactions = get_transactions()
    return build_profile_summary(transactions)
