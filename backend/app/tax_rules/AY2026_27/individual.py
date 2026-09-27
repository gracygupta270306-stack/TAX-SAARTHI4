ASSESSMENT_YEAR = "2026-27"
FINANCIAL_YEAR = "2025-26"

OLD_REGIME_SLABS = [
    {"limit": 250000, "rate": 0.00},
    {"limit": 500000, "rate": 0.05},
    {"limit": 1000000, "rate": 0.10},
    {"limit": 2000000, "rate": 0.15},
    {"limit": 5000000, "rate": 0.20},
    {"limit": None, "rate": 0.30},
]

NEW_REGIME_SLABS = [
    {"limit": 400000, "rate": 0.00},
    {"limit": 800000, "rate": 0.05},
    {"limit": 1200000, "rate": 0.10},
    {"limit": 1600000, "rate": 0.15},
    {"limit": 2000000, "rate": 0.20},
    {"limit": 2400000, "rate": 0.25},
    {"limit": None, "rate": 0.30},
]

STANDARD_DEDUCTION = {
    "old": {"amount": 50000, "section": "16(ia)", "source": "Income Tax Department"},
    "new": {"amount": 75000, "section": "16(ia)", "source": "Income Tax Department"},
}

REBATE_87A = {
    "old": {"amount": 12500, "incomeLimit": 500000, "source": "Income Tax Department"},
    "new": {"amount": 60000, "incomeLimit": 1200000, "source": "Income Tax Department"},
}

SURCHARGE = [
    {"threshold": 5000000, "rate": 0.10},
    {"threshold": 10000000, "rate": 0.15},
    {"threshold": 20000000, "rate": 0.25},
    {"threshold": 50000000, "rate": 0.30},
]

CESS = {"rate": 0.04, "source": "Income Tax Department"}
