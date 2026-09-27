from __future__ import annotations

from typing import Any

from app.expert_knowledge.knowledge import EXPERT_KNOWLEDGE
from app.rules.financial_rules import FINANCIAL_RULES
from app.services.ai_analysis import analyze_temporal_signals, analyze_trends


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def run_decision_engine(dataframe: Any) -> dict[str, Any]:
    if dataframe is None or dataframe.empty:
        return {
            "summary": {"total_income": 0.0, "total_expenses": 0.0, "net_savings": 0.0, "transaction_count": 0},
            "risk": {"level": "low", "score": 0, "summary": "No financial data available yet."},
            "findings": [],
            "rule_hits": [],
            "expert_knowledge": [],
            "ai_insights": [],
            "narrative": "No financial data has been uploaded yet.",
        }

    income_total = _as_float(dataframe.loc[dataframe["type"].str.lower() == "income", "amount"].sum())
    expense_total = _as_float(dataframe.loc[dataframe["type"].str.lower() != "income", "amount"].sum())
    net_savings = income_total - expense_total
    savings_rate = (net_savings / income_total * 100) if income_total else 0.0

    loan_related = dataframe[dataframe["description"].str.lower().str.contains("emi|loan|mortgage|repayment|credit", na=False)]
    loan_total = _as_float(loan_related["amount"].sum())
    loan_ratio = (loan_total / income_total) if income_total else 0.0

    matched_rules: list[dict[str, Any]] = []
    for rule in FINANCIAL_RULES:
        triggered = False
        if rule["id"] == "RULE-01" and expense_total > income_total:
            triggered = True
        elif rule["id"] == "RULE-02" and loan_ratio >= 0.35:
            triggered = True
        elif rule["id"] == "RULE-03" and savings_rate < 10:
            triggered = True
        if triggered:
            matched_rules.append(
                {
                    "id": rule["id"],
                    "name": rule["name"],
                    "severity": rule["severity"],
                    "result": rule["result"],
                    "evidence": rule["evidence"],
                }
            )

    matched_expert = []
    if expense_total > income_total:
        matched_expert.append(EXPERT_KNOWLEDGE[0])
        matched_expert.append(EXPERT_KNOWLEDGE[1])
    if loan_ratio >= 0.35:
        matched_expert.append(EXPERT_KNOWLEDGE[2])
    if not matched_expert:
        matched_expert = [EXPERT_KNOWLEDGE[3]]

    temporal_signals = analyze_temporal_signals(dataframe)
    ai_insights = analyze_trends(dataframe)

    risk_score = 0
    if expense_total > income_total:
        risk_score += 35
    if loan_ratio >= 0.35:
        risk_score += 25
    if savings_rate < 10:
        risk_score += 20
    if len(ai_insights) > 1:
        risk_score += 10
    risk_score = min(risk_score, 100)

    if risk_score >= 75:
        risk_level = "critical"
        risk_summary = "The available financial data suggests a high likelihood of cash-flow stress and potential distress signals requiring human review."
    elif risk_score >= 45:
        risk_level = "high"
        risk_summary = "There are meaningful risk indicators, including cash-flow pressure and debt burden exposure."
    elif risk_score >= 20:
        risk_level = "moderate"
        risk_summary = "Some risk indicators are visible, but the current evidence is not yet severe enough to confirm a crisis."
    else:
        risk_level = "low"
        risk_summary = "No major concerns are visible in the current dataset, though the result remains dependent on data completeness."

    findings = []
    if expense_total > income_total:
        findings.append(
            {
                "title": "Cash-flow stress",
                "what_happened": "The expenses in the uploaded transactions exceed the recorded income.",
                "why": "This triggered the cash-flow deficit rule and indicates low monthly surplus or a recurring imbalance.",
                "evidence": {"income": round(income_total, 2), "expenses": round(expense_total, 2), "difference": round(expense_total - income_total, 2)},
                "why_it_matters": "Persistent deficits can lead to borrowing, missed obligations, and reduced financial resilience.",
                "what_to_do": "Reduce non-essential spending, review recurring commitments, and check whether income is under-reported or spending is overstated.",
                "human_review_required": True,
            }
        )
    if loan_ratio >= 0.35:
        findings.append(
            {
                "title": "Debt burden concern",
                "what_happened": "Recurring loan or EMI-like payments are a substantial part of reported income.",
                "why": "This matches the debt-burden rule and suggests the user may be carrying a heavy debt load relative to income.",
                "evidence": {"loan_related_amount": round(loan_total, 2), "income": round(income_total, 2), "debt_to_income_ratio": round(loan_ratio * 100, 2)},
                "why_it_matters": "A heavy EMI burden can limit monthly flexibility and increase the chance of a debt trap.",
                "what_to_do": "Review repayments, prioritize high-interest debt, and avoid adding new obligations until affordability improves.",
                "human_review_required": True,
            }
        )
    if not findings:
        findings.append(
            {
                "title": "No strong distress signal",
                "what_happened": "The current information does not show a major warning pattern.",
                "why": "The uploaded data is broadly balanced, and the rule checks did not trigger severe threshold conditions.",
                "evidence": {"income": round(income_total, 2), "expenses": round(expense_total, 2), "net_savings": round(net_savings, 2)},
                "why_it_matters": "This is a positive sign but still depends on data completeness and the inclusion of all obligations.",
                "what_to_do": "Upload all accounts and confirm any recurring loans, insurance, or business cash-flow details before making major decisions.",
                "human_review_required": False,
            }
        )

    narrative = (
        "The current financial picture shows a "
        f"{risk_level} risk profile with a reported net saving of Rs {net_savings:,.2f}. "
        "This result combines rule checks, expert knowledge, and AI trend indicators from the uploaded transaction data."
    )

    return {
        "summary": {
            "total_income": round(income_total, 2),
            "total_expenses": round(expense_total, 2),
            "net_savings": round(net_savings, 2),
            "transaction_count": len(dataframe),
            "savings_rate": round(savings_rate, 2),
            "loan_related_amount": round(loan_total, 2),
            "debt_to_income_ratio": round(loan_ratio * 100, 2),
        },
        "risk": {
            "level": risk_level,
            "score": risk_score,
            "summary": risk_summary,
        },
        "findings": findings,
        "rule_hits": matched_rules,
        "expert_knowledge": matched_expert,
        "ai_insights": ai_insights,
        "temporal_signals": temporal_signals,
        "narrative": narrative,
    }
