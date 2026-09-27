from __future__ import annotations

from typing import Any

import pandas as pd


def build_profile_summary(dataframe: pd.DataFrame) -> dict[str, Any]:
    if dataframe is None or dataframe.empty:
        return {
            "loan_profile": {"status": "not_available", "monthly_emi": 0.0, "debt_to_income_ratio": 0.0, "recommended_action": "Add transaction history to assess borrowing risk."},
            "investment_profile": {"status": "not_available", "monthly_investment": 0.0, "asset_allocation": {}, "recommended_action": "Add investment or SIP entries to see allocation insights."},
            "summary": "No profile data available yet.",
        }

    income = float(dataframe.loc[dataframe["type"].str.lower() == "income", "amount"].sum())
    expenses = dataframe.loc[dataframe["type"].str.lower() != "income"].copy()
    loan_related = expenses[expenses["description"].str.lower().str.contains("emi|loan|mortgage|repayment|credit", na=False)]
    investment_related = expenses[expenses["description"].str.lower().str.contains("sip|mutual|investment|stock|fd|ppf|nps|gold", na=False)]

    monthly_emi = float(loan_related["amount"].sum())
    debt_to_income_ratio = (monthly_emi / income * 100) if income else 0.0
    required_action = "Within healthy range for a typical borrower." if debt_to_income_ratio < 35 else "Needs review; EMI burden is high relative to income."

    investment_total = float(investment_related["amount"].sum())
    allocation = {
        "SIP / Mutual Funds": float(investment_related[investment_related["description"].str.lower().str.contains("sip|mutual", na=False)]["amount"].sum()),
        "Equity / Stocks": float(investment_related[investment_related["description"].str.lower().str.contains("stock|equity", na=False)]["amount"].sum()),
        "Fixed Income / Gold / PPF": float(investment_related[investment_related["description"].str.lower().str.contains("fd|gold|ppf|nps", na=False)]["amount"].sum()),
    }

    return {
        "loan_profile": {
            "status": "active" if monthly_emi > 0 else "not_available",
            "monthly_emi": round(monthly_emi, 2),
            "debt_to_income_ratio": round(debt_to_income_ratio, 2),
            "recommended_action": required_action,
        },
        "investment_profile": {
            "status": "active" if investment_total > 0 else "not_available",
            "monthly_investment": round(investment_total, 2),
            "asset_allocation": {key: round(value, 2) for key, value in allocation.items() if value > 0},
            "recommended_action": "Maintain diversification across volatility and fixed-income allocations." if investment_total > 0 else "Add regular investment or SIP entries to improve the profile.",
        },
        "summary": "The profile summarizes borrowing and wealth-building behavior from the uploaded financial activity.",
    }
