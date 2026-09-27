from collections import Counter

import pandas as pd

from app.services.decision_engine import run_decision_engine
from app.services.report_generator import build_report

CATEGORY_RULES = {
    "Food": ["food", "grocery", "groceries", "restaurant", "cafe", "swiggy", "zomato"],
    "Shopping": ["amazon", "flipkart", "shopping", "mall", "clothing"],
    "Travel": ["uber", "ola", "flight", "hotel", "travel", "fuel", "petrol"],
    "Bills": ["electricity", "water", "internet", "mobile", "rent", "utility"],
    "Healthcare": ["hospital", "doctor", "pharmacy", "medicine", "health"],
    "Investment": ["mutual fund", "stock", "sip", "investment", "zerodha"],
    "Loan/EMI": ["loan", "emi", "mortgage", "repayment"],
}


def categorize_transaction(description: str, transaction_type: str) -> tuple[str, str]:
    if transaction_type == "income":
        return "Income", "The transaction type is marked as income."

    text = description.lower()
    for category, keywords in CATEGORY_RULES.items():
        for keyword in keywords:
            if keyword in text:
                return category, f"Description matched the keyword '{keyword}'."

    return "Other", "No configured category keyword matched the description."


def analyze_transactions(dataframe: pd.DataFrame) -> dict:
    enriched = dataframe.copy()
    if enriched.empty:
        return {"summary": {"total_income": 0.0, "total_expenses": 0.0, "net_savings": 0.0, "transaction_count": 0}, "category_breakdown": [], "transactions": [], "alerts": [], "risk": {"level": "low", "score": 0, "summary": "No transactions uploaded yet."}, "findings": [], "rule_hits": [], "expert_knowledge": [], "ai_insights": [], "narrative": "No transactions uploaded yet.", "steps": []}

    enriched["amount"] = pd.to_numeric(enriched["amount"], errors="coerce").fillna(0)
    enriched["description"] = enriched["description"].fillna("").astype(str).str.strip()
    enriched["type"] = enriched["type"].fillna("").astype(str).str.strip().str.lower()

    categorized = enriched.apply(
        lambda row: categorize_transaction(row["description"], row["type"]), axis=1
    )
    enriched["category"] = [result[0] for result in categorized]
    enriched["category_reason"] = [result[1] for result in categorized]

    income = float(enriched.loc[enriched["type"] == "income", "amount"].sum())
    expenses = float(enriched.loc[enriched["type"] != "income", "amount"].sum())
    category_totals = (
        enriched.loc[enriched["type"] != "income"]
        .groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
    )

    alerts: list[dict] = []
    expense_values = enriched.loc[enriched["type"] != "income", "amount"]
    if not expense_values.empty:
        high_expense_limit = max(float(expense_values.mean() * 3), 10000)
        high_expenses = enriched[
            (enriched["type"] != "income") & (enriched["amount"] >= high_expense_limit)
        ]
        for _, row in high_expenses.iterrows():
            alerts.append({
                "title": "Potentially high expense",
                "reason": f"This expense is at least three times the average expense or exceeds Rs {high_expense_limit:,.0f}.",
                "evidence": {"description": row["description"], "amount": row["amount"]},
                "next_step": "Review the transaction and confirm that it is expected.",
                "severity": "medium",
            })

    duplicate_counts = Counter(
        enriched.loc[enriched["type"] != "income", "description"].str.lower()
    )
    for description, count in duplicate_counts.items():
        if count > 1:
            alerts.append({
                "title": "Repeated transaction description",
                "reason": "The same description appears multiple times in the uploaded records.",
                "evidence": {"description": description, "occurrences": count},
                "next_step": "Check whether these are expected recurring payments.",
                "severity": "low",
            })

    decision = run_decision_engine(enriched)

    result = {
        "summary": {
            "total_income": round(float(income), 2),
            "total_expenses": round(float(expenses), 2),
            "net_savings": round(float(income - expenses), 2),
            "transaction_count": len(enriched),
        },
        "category_breakdown": [
            {"category": category, "amount": round(float(amount), 2)}
            for category, amount in category_totals.items()
        ],
        "transactions": enriched.to_dict(orient="records"),
        "alerts": alerts,
        "risk": decision["risk"],
        "findings": decision["findings"],
        "rule_hits": decision["rule_hits"],
        "expert_knowledge": decision["expert_knowledge"],
        "ai_insights": decision["ai_insights"],
        "temporal_signals": decision.get("temporal_signals", []),
        "narrative": decision["narrative"],
        "report": build_report({
            "summary": {
                "total_income": round(float(income), 2),
                "total_expenses": round(float(expenses), 2),
                "net_savings": round(float(income - expenses), 2),
            },
            "risk": decision["risk"],
            "findings": decision["findings"],
            "ai_insights": decision["ai_insights"],
            "expert_knowledge": decision["expert_knowledge"],
        }),
        "steps": [
            {"name": "Transaction categorization", "status": "completed", "finding": f"Categorized {len(enriched)} transactions."},
            {"name": "Expense analysis", "status": "completed", "finding": f"Found {len(category_totals)} expense categories."},
            {"name": "Rule and risk checks", "status": "completed", "finding": f"Found {len(decision['rule_hits'])} triggered rule(s) and {len(alerts)} alert(s)."},
        ],
    }
    return result
