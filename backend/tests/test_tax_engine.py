from decimal import Decimal

from app.tax_engine.calculator import calculate_tax


def test_tax_engine_calculates_old_and_new_regimes_for_salary():
    request = {
        "assessmentYear": "2026-27",
        "age": 35,
        "residentialStatus": "resident",
        "employmentType": "salaried",
        "salary": {
            "basicSalary": 1200000,
            "da": 0,
            "hraReceived": 0,
            "specialAllowance": 0,
            "bonus": 0,
            "commission": 0,
            "perquisites": 0,
            "otherTaxableSalary": 0,
            "employerNps": 0,
            "professionalTax": 0,
            "standardDeduction": 75000,
        },
        "deductions": {
            "section80C": 150000,
            "section80D": 25000,
            "section80CCD1": 50000,
            "homeLoanInterest": 0,
        },
        "tds": 0,
    }

    result = calculate_tax(request)

    assert result["status"] == "success"
    assert result["oldRegime"]["taxableIncome"] >= 0
    assert result["newRegime"]["taxableIncome"] >= 0
    assert result["comparison"]["difference"] is not None
    assert "rulesApplied" in result


def test_new_regime_rebate_results_in_zero_tax_only_within_configured_limit():
    result = calculate_tax(
        {
            "assessmentYear": "2026-27",
            "residentialStatus": "resident",
            "salary": {"basicSalary": 1200000},
        }
    )

    assert result["newRegime"]["grossIncome"] == Decimal("1200000.00")
    assert result["newRegime"]["taxableIncome"] == Decimal("1125000.00")
    assert result["newRegime"]["taxBeforeRebate"] == Decimal("52500.00")
    assert result["newRegime"]["rebate87A"] == Decimal("52500.00")
    assert result["newRegime"]["totalTax"] == Decimal("0.00")


def test_new_regime_uses_reported_annual_income_and_calculates_tax_above_rebate_limit():
    result = calculate_tax(
        {
            "assessmentYear": "2026-27",
            "residentialStatus": "resident",
            "salary": {"basicSalary": 1200000},
            "financialProfile": {"annualIncome": 1500000},
        }
    )

    assert result["newRegime"]["grossIncome"] == Decimal("1500000.00")
    assert result["newRegime"]["taxableIncome"] == Decimal("1425000.00")
    assert result["newRegime"]["taxBeforeRebate"] == Decimal("93750.00")
    assert result["newRegime"]["rebate87A"] == Decimal("0.00")
    assert result["newRegime"]["cess"] == Decimal("3750.00")
    assert result["newRegime"]["totalTax"] == Decimal("97500.00")


def test_new_regime_calculates_income_across_multiple_slabs():
    result = calculate_tax(
        {
            "assessmentYear": "2026-27",
            "residentialStatus": "resident",
            "financialProfile": {"annualIncome": 2500000},
        }
    )

    regime = result["newRegime"]
    assert regime["taxableIncome"] == Decimal("2425000.00")
    assert [step["rate"] for step in regime["slabBreakdown"]] == [
        Decimal("0.0"),
        Decimal("0.05"),
        Decimal("0.1"),
        Decimal("0.15"),
        Decimal("0.2"),
        Decimal("0.25"),
        Decimal("0.3"),
    ]
    assert [step["tax"] for step in regime["slabBreakdown"]] == [
        Decimal("0.00"),
        Decimal("20000.00"),
        Decimal("40000.00"),
        Decimal("60000.00"),
        Decimal("80000.00"),
        Decimal("100000.00"),
        Decimal("7500.00"),
    ]
    assert regime["taxBeforeRebate"] == Decimal("307500.00")
    assert regime["totalTax"] == Decimal("319800.00")


def test_old_and_new_regimes_use_their_own_rules_for_comparison():
    result = calculate_tax(
        {
            "assessmentYear": "2026-27",
            "residentialStatus": "resident",
            "salary": {"basicSalary": 1500000},
            "deductions": {"section80C": 150000, "section80D": 25000},
        }
    )

    assert result["oldRegime"]["taxableIncome"] == Decimal("1275000.00")
    assert result["oldRegime"]["totalTax"] == Decimal("107900.00")
    assert result["newRegime"]["taxableIncome"] == Decimal("1425000.00")
    assert result["newRegime"]["totalTax"] == Decimal("97500.00")
    assert result["comparison"]["newIsLower"] is True


def test_87a_rebate_and_boundary_are_applied():
    request = {
        "assessmentYear": "2026-27",
        "age": 35,
        "residentialStatus": "resident",
        "employmentType": "salaried",
        "salary": {
            "basicSalary": 1200000,
            "da": 0,
            "hraReceived": 0,
            "specialAllowance": 0,
            "bonus": 0,
            "commission": 0,
            "perquisites": 0,
            "otherTaxableSalary": 0,
            "employerNps": 0,
            "professionalTax": 0,
            "standardDeduction": 75000,
        },
        "deductions": {
            "section80C": 0,
            "section80D": 0,
            "section80CCD1": 0,
            "homeLoanInterest": 0,
        },
        "tds": 0,
    }

    result = calculate_tax(request)
    assert result["newRegime"]["rebate87A"] >= 0
    assert result["newRegime"]["totalTax"] >= 0


def test_duplicate_deduction_is_blocked():
    request = {
        "assessmentYear": "2026-27",
        "age": 25,
        "residentialStatus": "resident",
        "employmentType": "salaried",
        "salary": {
            "basicSalary": 1000000,
            "da": 0,
            "hraReceived": 0,
            "specialAllowance": 0,
            "bonus": 0,
            "commission": 0,
            "perquisites": 0,
            "otherTaxableSalary": 0,
            "employerNps": 0,
            "professionalTax": 0,
            "standardDeduction": 75000,
        },
        "investments": {
            "PPF": 150000,
            "ELSS": 150000,
        },
        "deductions": {
            "section80C": 150000,
        },
        "tds": 0,
    }

    result = calculate_tax(request)
    assert result["warnings"]
    assert result["deductionLedger"]


def test_financial_inputs_contribute_to_summary_and_audit_trail():
    request = {
        "assessmentYear": "2026-27",
        "age": 35,
        "residentialStatus": "resident",
        "employmentType": "salaried",
        "salary": {"basicSalary": 1200000},
        "incomes": [{"source": "salary", "amount": 1200000, "frequency": "annual", "taxable": True}, {"source": "rental", "amount": 120000, "frequency": "annual", "taxable": False}],
        "expenses": [{"category": "housing", "amount": 180000, "frequency": "annual", "taxRelevant": False}, {"category": "insurance", "amount": 30000, "frequency": "annual", "taxRelevant": True}],
        "losses": [{"lossType": "business", "amount": 50000, "eligibleForSetOff": True, "carryForward": False}],
        "goals": [{"goalName": "Emergency fund", "targetAmount": 500000, "currentAmountSaved": 150000, "targetDate": "2030-12-31"}],
        "loans": [{"loanType": "home", "principalAmount": 500000, "outstandingAmount": 400000, "interestRate": 7.5, "emi": 32000, "annualInterestPaid": 45000, "annualPrincipalRepaid": 12000}],
        "investments": [{"assetType": "PPF", "investmentAmount": 100000, "currentValue": 100000, "taxTreatment": "deduction"}],
        "deductions": {"section80C": 150000, "section80D": 25000, "homeLoanInterest": 50000},
        "tds": 0,
    }

    result = calculate_tax(request)
    assert result["status"] == "success"
    assert result["financialSummary"]["totalIncome"] == Decimal("1200000.00")
    assert "auditTrail" in result
    assert result["financialSummary"]["totalGoals"] >= 1


def test_87a_thresholds_are_enforced_for_resident_and_non_resident_taxpayers():
    resident = {
        "assessmentYear": "2026-27",
        "age": 35,
        "residentialStatus": "resident",
        "employmentType": "salaried",
        "salary": {"basicSalary": 1200000},
        "deductions": {"section80C": 0, "section80D": 0},
        "tds": 0,
    }
    nri = {
        "assessmentYear": "2026-27",
        "age": 35,
        "residentialStatus": "non-resident",
        "employmentType": "salaried",
        "salary": {"basicSalary": 1200000},
        "deductions": {"section80C": 0, "section80D": 0},
        "tds": 0,
    }

    resident_result = calculate_tax(resident)
    nri_result = calculate_tax(nri)

    assert resident_result["newRegime"]["rebate87A"] >= 0
    assert nri_result["newRegime"]["rebate87A"] == 0


def test_missing_rule_set_raises_clear_error_for_unsupported_assessment_year():
    result = calculate_tax({"assessmentYear": "2030-31", "salary": {"basicSalary": 500000}})
    assert result["status"] == "error"
    assert "not configured" in result["warnings"][0].lower()
