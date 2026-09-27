from __future__ import annotations

from typing import Any

import pandas as pd


def analyze_temporal_signals(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    if dataframe is None or dataframe.empty:
        return []

    enriched = dataframe.copy()
    if "date" not in enriched.columns:
        return []

    enriched["date"] = pd.to_datetime(enriched["date"], errors="coerce")
    enriched = enriched.dropna(subset=["date"]).copy()
    if enriched.empty:
        return []

    enriched["type"] = enriched["type"].fillna("").astype(str).str.lower()
    enriched["amount"] = pd.to_numeric(enriched["amount"], errors="coerce").fillna(0)

    monthly_summary: list[dict[str, Any]] = []
    for month, group in enriched.groupby(enriched["date"].dt.to_period("M").astype(str)):
        income_total = float(group.loc[group["type"] == "income", "amount"].sum())
        expense_total = float(group.loc[group["type"] != "income", "amount"].sum())
        net_savings = income_total - expense_total
        monthly_summary.append(
            {
                "period": month,
                "income": income_total,
                "expenses": expense_total,
                "net_savings": net_savings,
                "savings_rate": ((net_savings / income_total) * 100) if income_total else 0.0,
            }
        )

    monthly_summary.sort(key=lambda item: item["period"])
    if len(monthly_summary) < 2:
        return []

    current = monthly_summary[-1]
    previous = monthly_summary[-2]
    recent_periods = monthly_summary[-3:]

    signals: list[dict[str, Any]] = []

    if current["net_savings"] < 0 and previous["net_savings"] >= 0:
        signals.append(
            {
                "title": "Trend reversal to cash-flow pressure",
                "summary": (
                    f"The latest period shifted from a positive net balance of Rs {previous['net_savings']:,.2f} to a negative balance "
                    f"of Rs {current['net_savings']:,.2f}, indicating a recent deterioration in cash flow."
                ),
                "confidence": "high",
                "time_window": {"current_period": current["period"], "previous_period": previous["period"]},
                "current_evidence": current,
                "historical_evidence": recent_periods[:-1],
                "evidence": {
                    "previous_net_savings": round(previous["net_savings"], 2),
                    "current_net_savings": round(current["net_savings"], 2),
                    "change": round(current["net_savings"] - previous["net_savings"], 2),
                },
                "weighting": "Current evidence is weighted most heavily; older monthly balances are treated as background context.",
            }
        )

    if all(period["net_savings"] < 0 for period in recent_periods):
        signals.append(
            {
                "title": "Persistent deficit pattern",
                "summary": "The last three periods have all produced negative net savings, suggesting a persistent contradiction between income and obligations.",
                "confidence": "medium",
                "time_window": {"recent_periods": [period["period"] for period in recent_periods]},
                "current_evidence": current,
                "historical_evidence": recent_periods[:-1],
                "evidence": {"recent_net_savings": [round(period["net_savings"], 2) for period in recent_periods]},
                "weighting": "Older evidence is down-weighted and the current trend is now the dominant signal.",
            }
        )

    if current["expenses"] > current["income"] and current["expenses"] > previous["expenses"]:
        signals.append(
            {
                "title": "Emerging expense-led risk",
                "summary": "Recent spending has accelerated beyond the prior period and is now exceeding income, which suggests the risk picture is worsening.",
                "confidence": "medium",
                "time_window": {"current_period": current["period"], "previous_period": previous["period"]},
                "current_evidence": current,
                "historical_evidence": recent_periods[:-1],
                "evidence": {
                    "current_income": round(current["income"], 2),
                    "current_expenses": round(current["expenses"], 2),
                    "previous_expenses": round(previous["expenses"], 2),
                    "expense_delta": round(current["expenses"] - previous["expenses"], 2),
                },
                "weighting": "The latest period carries the strongest weight, while older spending patterns are treated as historical context.",
            }
        )

    if not signals:
        signals.append(
            {
                "title": "Stable multi-period trend",
                "summary": "Recent periods remain broadly consistent and the current assessment is not being materially contradicted by older evidence.",
                "confidence": "low",
                "time_window": {"current_period": current["period"], "prior_periods": [period["period"] for period in monthly_summary[:-1]]},
                "current_evidence": current,
                "historical_evidence": monthly_summary[:-1],
                "evidence": {"current_net_savings": round(current["net_savings"], 2), "previous_net_savings": round(previous["net_savings"], 2)},
                "weighting": "The latest period is considered primary evidence and earlier months are intentionally down-weighted.",
            }
        )

    return signals


def analyze_trends(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    if dataframe is None or dataframe.empty:
        return []

    enriched = dataframe.copy()
    enriched["type"] = enriched["type"].fillna("").astype(str).str.lower()
    enriched["amount"] = pd.to_numeric(enriched["amount"], errors="coerce").fillna(0)

    income_total = float(enriched.loc[enriched["type"] == "income", "amount"].sum())
    expense_total = float(enriched.loc[enriched["type"] != "income", "amount"].sum())
    average_expense = float(enriched.loc[enriched["type"] != "income", "amount"].mean()) if not enriched.empty else 0.0
    max_expense = float(enriched.loc[enriched["type"] != "income", "amount"].max()) if not enriched.empty else 0.0

    insights: list[dict[str, Any]] = []
    if expense_total > income_total:
        insights.append(
            {
                "title": "Cash-flow pressure detected",
                "summary": "Expenses in the uploaded data exceed recorded income, which suggests a negative monthly balance.",
                "confidence": "medium",
                "evidence": {
                    "income": income_total,
                    "expenses": expense_total,
                    "difference": expense_total - income_total,
                },
            }
        )
    if average_expense > 0 and max_expense > average_expense * 2:
        insights.append(
            {
                "title": "Large outlier spending",
                "summary": "At least one expense is significantly above the typical transaction size for this dataset.",
                "confidence": "medium",
                "evidence": {
                    "average_expense": average_expense,
                    "largest_expense": max_expense,
                },
            }
        )
    if not insights:
        insights.append(
            {
                "title": "Stable pattern observed",
                "summary": "The uploaded transactions currently show a balanced pattern without a clear distress signal, though the result remains sensitive to missing information.",
                "confidence": "low",
                "evidence": {
                    "income": income_total,
                    "expenses": expense_total,
                },
            }
        )

    temporal = analyze_temporal_signals(enriched)
    insights.extend(temporal)
    return insights
