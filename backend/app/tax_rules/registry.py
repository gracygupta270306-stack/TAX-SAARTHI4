from __future__ import annotations

from typing import Any

TAX_RULES = {
    "2026-27": {
        "assessmentYear": "2026-27",
        "financialYear": "2025-26",
        "oldRegime": {
            "slabs": [
                {"limit": 250000, "rate": 0},
                {"limit": 500000, "rate": 0.05},
                {"limit": 1000000, "rate": 0.10},
                {"limit": 2000000, "rate": 0.15},
                {"limit": 5000000, "rate": 0.20},
                {"limit": None, "rate": 0.30},
            ],
            "standardDeduction": {"amount": 50000, "source": "Income Tax Department"},
            "rebate87A": {"amount": 12500, "incomeLimit": 500000, "source": "Income Tax Department"},
        },
        "newRegime": {
            "slabs": [
                {"limit": 400000, "rate": 0},
                {"limit": 800000, "rate": 0.05},
                {"limit": 1200000, "rate": 0.10},
                {"limit": 1600000, "rate": 0.15},
                {"limit": 2000000, "rate": 0.20},
                {"limit": 2400000, "rate": 0.25},
                {"limit": None, "rate": 0.30},
            ],
            "standardDeduction": {"amount": 75000, "source": "Income Tax Department"},
            "rebate87A": {"amount": 60000, "incomeLimit": 1200000, "source": "Income Tax Department"},
        },
        "surcharge": {
            "thresholds": [
                {"threshold": 5000000, "rate": 0.10},
                {"threshold": 10000000, "rate": 0.15},
                {"threshold": 20000000, "rate": 0.25},
                {"threshold": 50000000, "rate": 0.30},
            ],
            "source": "Income Tax Department",
        },
        "cess": {"rate": 0.04, "source": "Income Tax Department"},
        "deductions": {
            "80C": {"limit": 150000, "regime": ["old"], "source": "Income Tax Department"},
            "80D": {"limit": 25000, "regime": ["old"], "source": "Income Tax Department"},
            "80CCD1": {"limit": 150000, "regime": ["old", "new"], "source": "Income Tax Department"},
            "80CCD1B": {"limit": 50000, "regime": ["old", "new"], "source": "Income Tax Department"},
            "80CCD2": {"limit": None, "regime": ["old", "new"], "source": "Income Tax Department"},
            "24b": {"limit": 200000, "regime": ["old"], "source": "Income Tax Department"},
            "standardDeduction": {"limit": 75000, "regime": ["new", "old"], "source": "Income Tax Department"},
        },
        "notes": "Rule set is aligned to the current AY 2026-27 configuration and must be reviewed against the latest official notification before use.",
    }
}


def get_tax_rule_set(assessment_year: str) -> dict[str, Any]:
    if assessment_year not in TAX_RULES:
        raise ValueError(f"Tax rules for Assessment Year {assessment_year} are not configured.")
    return TAX_RULES[assessment_year]
