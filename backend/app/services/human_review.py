from __future__ import annotations

from typing import Any


def build_human_review_cases(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    findings = analysis.get("findings", [])
    risk = analysis.get("risk", {})

    if findings:
        for item in findings:
            if item.get("human_review_required"):
                cases.append(
                    {
                        "case_id": f"HR-{len(cases) + 1:03d}",
                        "title": item.get("title", "Review required"),
                        "summary": item.get("what_happened", "Potential financial concern detected."),
                        "reason": item.get("why", "Please validate against actual obligations and context."),
                        "recommended_action": item.get("what_to_do", "Review with a qualified professional."),
                        "severity": "high" if risk.get("level") in {"high", "critical"} else "medium",
                    }
                )

    if not cases:
        cases.append(
            {
                "case_id": "HR-001",
                "title": "Routine financial review",
                "summary": "No urgent concern was triggered by the current transaction history.",
                "reason": "This is a low-risk case based on available evidence.",
                "recommended_action": "Continue to upload all accounts for better completeness and decision-making confidence.",
                "severity": "low",
            }
        )

    return cases
