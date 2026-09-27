import pandas as pd

from app.services.analysis import analyze_transactions
from app.services.exporter import build_export_payload
from app.services.human_review import build_human_review_cases
from app.services.profiles import build_profile_summary


def test_temporal_signal_analysis_tracks_changes_over_time():
    dataframe = pd.DataFrame(
        [
            {"date": "2025-01-05", "description": "Salary", "amount": 90000, "type": "income"},
            {"date": "2025-01-10", "description": "Rent", "amount": 40000, "type": "expense"},
            {"date": "2025-01-12", "description": "Travel", "amount": 15000, "type": "expense"},
            {"date": "2025-02-03", "description": "Salary", "amount": 90000, "type": "income"},
            {"date": "2025-02-06", "description": "Rent", "amount": 42000, "type": "expense"},
            {"date": "2025-02-07", "description": "EMI", "amount": 26000, "type": "expense"},
            {"date": "2025-03-01", "description": "Salary", "amount": 95000, "type": "income"},
            {"date": "2025-03-04", "description": "Rent", "amount": 43000, "type": "expense"},
            {"date": "2025-03-05", "description": "EMI", "amount": 34000, "type": "expense"},
            {"date": "2025-03-12", "description": "Shopping", "amount": 22000, "type": "expense"},
        ]
    )

    analysis = analyze_transactions(dataframe)

    assert "temporal_signals" in analysis
    assert isinstance(analysis["temporal_signals"], list)
    assert analysis["temporal_signals"]
    assert any("trend" in signal["title"].lower() or "signal" in signal["title"].lower() for signal in analysis["temporal_signals"])


def test_profile_and_review_and_export_are_generated():
    dataframe = pd.DataFrame(
        [
            {"date": "2026-01-01", "description": "Monthly Salary", "amount": 70000, "type": "income"},
            {"date": "2026-01-02", "description": "Apartment Rent", "amount": 20000, "type": "expense"},
            {"date": "2026-01-03", "description": "Mutual Fund SIP", "amount": 5000, "type": "expense"},
            {"date": "2026-01-04", "description": "Home Loan EMI", "amount": 18000, "type": "expense"},
        ]
    )

    analysis = analyze_transactions(dataframe)
    profile = build_profile_summary(dataframe)
    review_cases = build_human_review_cases(analysis)
    export_payload = build_export_payload(analysis, profile, review_cases)

    assert "loan_profile" in profile
    assert "investment_profile" in profile
    assert isinstance(review_cases, list)
    assert review_cases
    assert export_payload["filename"].endswith(".txt")
    assert "Risk" in export_payload["content"]
