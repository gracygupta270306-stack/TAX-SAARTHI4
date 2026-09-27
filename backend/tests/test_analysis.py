import pandas as pd

from app.services.analysis import analyze_transactions


def test_analyze_transactions_produces_summary_and_alerts():
    dataframe = pd.DataFrame(
        [
            {"date": "2026-01-01", "description": "Monthly Salary", "amount": 70000, "type": "income"},
            {"date": "2026-01-02", "description": "Apartment Rent", "amount": 20000, "type": "expense"},
            {"date": "2026-01-03", "description": "Shopping", "amount": 15000, "type": "expense"},
            {"date": "2026-01-04", "description": "EMI Payment", "amount": 12000, "type": "expense"},
        ]
    )

    result = analyze_transactions(dataframe)

    assert "summary" in result
    assert result["summary"]["total_income"] == 70000.0
    assert result["summary"]["total_expenses"] == 47000.0
    assert result["summary"]["net_savings"] == 23000.0
    assert "alerts" in result
    assert isinstance(result["alerts"], list)
    assert "risk" in result
    assert "findings" in result
