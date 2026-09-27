from __future__ import annotations

from typing import Any


def build_export_payload(analysis: dict[str, Any], profile: dict[str, Any], review_cases: list[dict[str, Any]]) -> dict[str, Any]:
    summary = analysis.get("summary", {})
    risk = analysis.get("risk", {})
    findings = analysis.get("findings", [])
    temporal_signals = analysis.get("temporal_signals", [])

    content_lines = [
        "TaxSaarthi Financial Decision Support Report",
        "===========================================",
        "",
        f"Risk level: {risk.get('level', 'low')}",
        f"Risk score: {risk.get('score', 0)}/100",
        f"Total income: Rs {summary.get('total_income', 0):,.2f}",
        f"Total expenses: Rs {summary.get('total_expenses', 0):,.2f}",
        f"Net savings: Rs {summary.get('net_savings', 0):,.2f}",
        "",
        "Loan profile:",
        f"- Monthly EMI: Rs {profile.get('loan_profile', {}).get('monthly_emi', 0):,.2f}",
        f"- Debt-to-income ratio: {profile.get('loan_profile', {}).get('debt_to_income_ratio', 0):.2f}%",
        "",
        "Investment profile:",
        f"- Monthly investment: Rs {profile.get('investment_profile', {}).get('monthly_investment', 0):,.2f}",
        "",
        "Key findings:",
    ]

    if findings:
        for item in findings:
            content_lines.append(f"- {item.get('title', 'Financial finding')}: {item.get('what_happened', '')}")
    else:
        content_lines.append("- No major findings detected.")

    if temporal_signals:
        content_lines.extend(["", "Temporal signal analysis:"])
        for signal in temporal_signals:
            content_lines.append(f"- {signal.get('title', 'Trend signal')}: {signal.get('summary', '')}")

    content_lines.extend(["", "Human review cases:"])
    for case in review_cases:
        content_lines.append(f"- {case['case_id']} | {case['title']} | {case['severity']}")

    content = "\n".join(content_lines)
    return {
        "filename": "taxsaarthi_report.txt",
        "content": content,
        "mime_type": "text/plain",
    }
