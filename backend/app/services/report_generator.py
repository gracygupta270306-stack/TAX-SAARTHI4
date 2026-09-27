from __future__ import annotations

from typing import Any


def build_report(analysis_result: dict[str, Any]) -> dict[str, Any]:
    summary = analysis_result.get("summary", {})
    risk = analysis_result.get("risk", {})
    findings = analysis_result.get("findings", [])
    ai_insights = analysis_result.get("ai_insights", [])
    temporal_signals = analysis_result.get("temporal_signals", [])
    expert_sources = analysis_result.get("expert_knowledge", [])

    executive_summary = (
        f"The uploaded data shows a {risk.get('level', 'low')} financial-risk profile. "
        f"Net savings are Rs {summary.get('net_savings', 0):,.2f} and the main risk drivers are "
        f"{', '.join(item.get('title', 'financial review') for item in findings[:2]) or 'data quality and routine review'}."
    )

    return {
        "report_type": "financial_decision_support",
        "executive_summary": executive_summary,
        "financial_health": {
            "total_income": summary.get("total_income", 0),
            "total_expenses": summary.get("total_expenses", 0),
            "net_savings": summary.get("net_savings", 0),
            "risk_level": risk.get("level", "low"),
        },
        "findings": findings,
        "ai_trends": ai_insights + temporal_signals,
        "temporal_signals": temporal_signals,
        "expert_sources": expert_sources,
        "recommendations": [
            item.get("what_to_do", "Review the details with a qualified professional before taking major financial steps.")
            for item in findings
        ],
        "human_review_required": any(item.get("human_review_required") for item in findings),
    }
