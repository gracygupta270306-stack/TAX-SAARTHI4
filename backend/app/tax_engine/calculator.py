from __future__ import annotations

from decimal import Decimal
from typing import Any

from app.tax_rules.registry import get_tax_rule_set
from app.tax_engine.utils import apply_percentage, money, round_currency, safe_divide, to_decimal


def _normalized_salary(data: dict[str, Any]) -> dict[str, Any]:
    defaults = {
        "basicSalary": 0,
        "da": 0,
        "hraReceived": 0,
        "specialAllowance": 0,
        "bonus": 0,
        "commission": 0,
        "perquisites": 0,
        "otherTaxableSalary": 0,
        "employerNps": 0,
        "professionalTax": 0,
        "standardDeduction": 0,
    }
    merged = {**defaults, **(data or {})}
    for key in merged:
        merged[key] = to_decimal(merged[key])
    return merged


def _numeric_amount(value: Any) -> Decimal:
    return to_decimal(value)


def _sum_amount(items: list[dict[str, Any]] | None, key: str) -> Decimal:
    total = Decimal("0")
    for item in items or []:
        if isinstance(item, dict):
            total += _numeric_amount(item.get(key, 0))
    return total


def _calculate_gross_income(
    salary: dict[str, Any],
    income_entries: list[dict[str, Any]],
    financial_profile: dict[str, Any],
) -> Decimal:
    salary_income = sum(
        (
            salary[key]
            for key in (
                "basicSalary",
                "da",
                "hraReceived",
                "specialAllowance",
                "bonus",
                "commission",
                "perquisites",
                "otherTaxableSalary",
            )
        ),
        Decimal("0"),
    )
    other_taxable_income = Decimal("0")
    for entry in income_entries:
        if not isinstance(entry, dict) or entry.get("taxable", True) is False:
            continue
        if salary_income > 0 and str(entry.get("source", "")).strip().lower() == "salary":
            continue
        other_taxable_income += _numeric_amount(entry.get("amount", 0))

    itemized_income = salary_income + other_taxable_income
    reported_annual_income = _numeric_amount(financial_profile.get("annualIncome", 0))
    return max(itemized_income, reported_annual_income)


def _calculate_tax_by_slabs(taxable_income: Decimal, slabs: list[dict[str, Any]]) -> tuple[Decimal, list[dict[str, Any]], list[str]]:
    tax_before_rebate = Decimal("0")
    steps: list[dict[str, Any]] = []
    previous_limit = Decimal("0")
    current = taxable_income

    for slab in slabs:
        limit = slab["limit"]
        rate = Decimal(str(slab["rate"]))
        if limit is None:
            taxable_segment = max(current - previous_limit, Decimal("0"))
            segment_tax = taxable_segment * rate
            tax_before_rebate += segment_tax
            steps.append({
                "from": previous_limit,
                "to": current,
                "rate": rate,
                "tax": round_currency(segment_tax),
            })
            break

        if current <= previous_limit:
            break

        to_amount = min(current, Decimal(str(limit)))
        taxable_segment = max(to_amount - previous_limit, Decimal("0"))
        segment_tax = taxable_segment * rate
        if taxable_segment > 0:
            tax_before_rebate += segment_tax
            steps.append({
                "from": previous_limit,
                "to": to_amount,
                "rate": rate,
                "tax": round_currency(segment_tax),
            })
        previous_limit = Decimal(str(limit))

    return round_currency(tax_before_rebate), steps, []


def _calculate_surcharge(taxable_income: Decimal, tax_before_cess: Decimal, assessment_year: str) -> tuple[Decimal, dict[str, Any]]:
    rule_set = get_tax_rule_set(assessment_year)
    surcharge_rule = rule_set.get("surcharge", {})
    thresholds = surcharge_rule.get("thresholds", [])
    tax_amount = tax_before_cess
    surcharge = Decimal("0")
    applied = None

    for threshold in sorted(thresholds, key=lambda item: item["threshold"]):
        limit = Decimal(str(threshold["threshold"]))
        if taxable_income > limit:
            surcharge = tax_amount * Decimal(str(threshold["rate"]))
            applied = threshold
    if applied is None:
        return Decimal("0"), {"threshold": None, "rate": Decimal("0")}
    return round_currency(surcharge), {"threshold": applied["threshold"], "rate": Decimal(str(applied["rate"]))}


def _calculate_marginal_relief(taxable_income: Decimal, tax_before_marginal_relief: Decimal, regime: str, assessment_year: str) -> Decimal:
    if regime != "newRegime":
        return Decimal("0")
    rule_set = get_tax_rule_set(assessment_year)
    threshold = Decimal(str(rule_set["newRegime"]["rebate87A"]["incomeLimit"]))
    if taxable_income <= threshold:
        return Decimal("0")
    additional_income = taxable_income - threshold
    relief = max(Decimal("0"), tax_before_marginal_relief - additional_income)
    return min(relief, tax_before_marginal_relief)


def _determine_87a_rebate(taxable_income: Decimal, regime: str, assessment_year: str, residential_status: str, tax_before_rebate: Decimal) -> tuple[Decimal, str, Decimal, bool, str]:
    rule_set = get_tax_rule_set(assessment_year)
    rebate_rules = rule_set[regime]["rebate87A"]
    rebate_limit = Decimal(str(rebate_rules["amount"]))
    income_limit = Decimal(str(rebate_rules["incomeLimit"]))
    eligible = residential_status == "resident" and taxable_income <= income_limit
    if not eligible:
        return Decimal("0"), f"Section 87A not applicable for {regime} regime in AY {assessment_year}", rebate_limit, False, "Resident individual threshold not met or taxpayer is not eligible."
    actual = min(tax_before_rebate, rebate_limit)
    return actual, f"Section 87A rebate for {regime} regime in AY {assessment_year}", rebate_limit, True, f"Eligible resident individual with taxable income of {round_currency(taxable_income)} and threshold {round_currency(income_limit)}."


def _calculate_cess(base: Decimal, assessment_year: str) -> Decimal:
    rule_set = get_tax_rule_set(assessment_year)
    rate = Decimal(str(rule_set["cess"]["rate"]))
    return round_currency(base * rate)


def _sum_deductions(deductions: dict[str, Any], regime: str) -> Decimal:
    allowed_sections = {
        "80C": Decimal(str(deductions.get("section80C", 0) or 0)),
        "80D": Decimal(str(deductions.get("section80D", 0) or 0)),
        "80CCD1": Decimal(str(deductions.get("section80CCD1", 0) or 0)),
        "80CCD1B": Decimal(str(deductions.get("section80CCD1B", 0) or 0)),
        "80CCD2": Decimal(str(deductions.get("section80CCD2", 0) or 0)),
        "24b": Decimal(str(deductions.get("homeLoanInterest", 0) or 0)),
    }
    total = Decimal("0")
    for _, value in allowed_sections.items():
        total += value
    return total


def _build_financial_summary(request: dict[str, Any], total_taxable_income: Decimal, total_income: Decimal, total_expenses: Decimal, total_losses: Decimal) -> dict[str, Any]:
    goals = request.get("goals") or []
    contribution_total = sum(_numeric_amount(item.get("currentMonthlyContribution", 0)) for item in goals if isinstance(item, dict))
    progress = Decimal("0")
    if goals:
        progress = sum(
            _numeric_amount(item.get("currentAmountSaved", 0))
            for item in goals if isinstance(item, dict)
        ) / sum(_numeric_amount(item.get("targetAmount", 0)) for item in goals if isinstance(item, dict) if _numeric_amount(item.get("targetAmount", 0)) > 0)
    savings_rate = Decimal("0")
    if total_income > 0:
        savings_rate = ((total_income - total_expenses) / total_income) * Decimal("100")
    investment_rate = Decimal("0")
    if total_income > 0:
        investment_rate = (sum(_numeric_amount(item.get("investmentAmount", 0)) for item in (request.get("investments") or []) if isinstance(item, dict)) / total_income) * Decimal("100")
    return {
        "totalIncome": round_currency(total_income),
        "totalExpenses": round_currency(total_expenses),
        "totalLosses": round_currency(total_losses),
        "netIncome": round_currency(total_income - total_expenses),
        "taxableIncome": round_currency(total_taxable_income),
        "totalGoals": len(goals),
        "totalGoalSavings": round_currency(sum(_numeric_amount(item.get("currentAmountSaved", 0)) for item in goals if isinstance(item, dict))),
        "goalProgress": round_currency(progress * Decimal("100")) if goals else Decimal("0"),
        "availableCashFlow": round_currency(total_income - total_expenses - sum(_numeric_amount(item.get("emi", 0)) for item in (request.get("loans") or []) if isinstance(item, dict))),
        "savingsRate": round_currency(savings_rate),
        "investmentRate": round_currency(investment_rate),
        "currentMonthlyContribution": round_currency(contribution_total),
    }


def calculate_tax(request: dict[str, Any]) -> dict[str, Any]:
    request = request or {}
    try:
        assessment_year = request.get("assessmentYear", "2026-27")
        rule_set = get_tax_rule_set(assessment_year)
    except ValueError as error:
        return {
            "status": "error",
            "assessmentYear": request.get("assessmentYear"),
            "warnings": [str(error)],
            "assumptions": [],
            "rulesApplied": [],
            "oldRegime": {},
            "newRegime": {},
            "comparison": {},
            "deductionOpportunities": [],
            "deductionLedger": [],
            "auditTrail": [{"step": "rule_validation", "message": str(error)}],
        }

    age = int(request.get("age", 0) or 0)
    residential_status = (request.get("residentialStatus") or "resident").lower()
    employment_type = (request.get("employmentType") or "salaried").lower()
    salary = _normalized_salary(request.get("salary") or {})
    deductions = request.get("deductions") or {}
    tds = to_decimal(request.get("tds", 0))
    warnings: list[str] = []
    assumptions: list[str] = []
    deduction_ledger: list[dict[str, Any]] = []
    audit_trail: list[dict[str, Any]] = [{
        "step": "input_validation",
        "message": "Collected tax inputs and eligibility metadata.",
        "assessmentYear": assessment_year,
        "residentialStatus": residential_status,
        "age": age,
    }]

    if age < 0:
        warnings.append("Age cannot be negative.")
    if residential_status not in {"resident", "non-resident", "rnor"}:
        warnings.append("Residential status is not recognized.")
    if employment_type not in {"salaried", "freelancer", "self-employed", "business", "professional", "pensioner", "other"}:
        warnings.append("Employment type is not recognized.")

    income_entries = request.get("incomes") or []
    expense_entries = request.get("expenses") or []
    loss_entries = request.get("losses") or []
    goals = request.get("goals") or []
    loan_entries = request.get("loans") or []
    investment_entries = request.get("investments") or []

    financial_profile = request.get("financialProfile") or {}
    total_income = _calculate_gross_income(salary, income_entries, financial_profile)

    total_expenses = _sum_amount(expense_entries, "amount")
    total_losses = _sum_amount(loss_entries, "amount")

    standard_deduction_old = Decimal(str(rule_set["oldRegime"]["standardDeduction"]["amount"]))
    standard_deduction_new = Decimal(str(rule_set["newRegime"]["standardDeduction"]["amount"]))

    old_regime_taxable = max(total_income - standard_deduction_old - _sum_deductions(deductions, "old"), Decimal("0"))
    new_regime_taxable = max(total_income - standard_deduction_new, Decimal("0"))

    old_tax_before_rebate, old_steps, _ = _calculate_tax_by_slabs(old_regime_taxable, rule_set["oldRegime"]["slabs"])
    new_tax_before_rebate, new_steps, _ = _calculate_tax_by_slabs(new_regime_taxable, rule_set["newRegime"]["slabs"])

    old_rebate_amount, old_rule, old_rebate_limit, old_eligible, old_reason = _determine_87a_rebate(old_regime_taxable, "oldRegime", assessment_year, residential_status, old_tax_before_rebate)
    new_rebate_amount, new_rule, new_rebate_limit, new_eligible, new_reason = _determine_87a_rebate(new_regime_taxable, "newRegime", assessment_year, residential_status, new_tax_before_rebate)
    old_tax_after_rebate = max(old_tax_before_rebate - old_rebate_amount, Decimal("0"))
    new_tax_after_rebate = max(new_tax_before_rebate - new_rebate_amount, Decimal("0"))

    old_surcharge, old_surcharge_meta = _calculate_surcharge(old_regime_taxable, old_tax_after_rebate, assessment_year)
    new_surcharge, new_surcharge_meta = _calculate_surcharge(new_regime_taxable, new_tax_after_rebate, assessment_year)

    old_marginal_relief = Decimal("0")
    new_marginal_relief = _calculate_marginal_relief(new_regime_taxable, new_tax_after_rebate, "newRegime", assessment_year)
    old_tax_plus_surcharge = old_tax_after_rebate + old_surcharge
    new_tax_plus_surcharge = new_tax_after_rebate + new_surcharge
    old_total_tax = max(old_tax_plus_surcharge - old_marginal_relief, Decimal("0"))
    new_total_tax = max(new_tax_plus_surcharge - new_marginal_relief, Decimal("0"))

    old_cess = _calculate_cess(old_total_tax, assessment_year)
    new_cess = _calculate_cess(new_total_tax, assessment_year)
    old_final_tax = old_total_tax + old_cess
    new_final_tax = new_total_tax + new_cess
    old_balance = max(old_final_tax - tds, Decimal("0"))
    new_balance = max(new_final_tax - tds, Decimal("0"))

    deduction_ledger.extend([
        {
            "deductionId": "deduction-1",
            "section": "standardDeduction",
            "source": "salary",
            "amountEntered": float(standard_deduction_old),
            "eligibleAmount": float(standard_deduction_old),
            "amountApplied": float(standard_deduction_old),
            "regime": "old",
            "assessmentYear": assessment_year,
        },
        {
            "deductionId": "deduction-2",
            "section": "standardDeduction",
            "source": "salary",
            "amountEntered": float(standard_deduction_new),
            "eligibleAmount": float(standard_deduction_new),
            "amountApplied": float(standard_deduction_new),
            "regime": "new",
            "assessmentYear": assessment_year,
        },
    ])

    audit_trail.extend([
        {
            "step": "section87A",
            "section": "87A",
            "regime": "oldRegime",
            "taxBeforeRebate": round_currency(old_tax_before_rebate),
            "maximumRebate": round_currency(old_rebate_limit),
            "actualRebate": round_currency(old_rebate_amount),
            "taxAfterRebate": round_currency(old_tax_after_rebate),
            "eligible": old_eligible,
            "reason": old_reason,
        },
        {
            "step": "section87A",
            "section": "87A",
            "regime": "newRegime",
            "taxBeforeRebate": round_currency(new_tax_before_rebate),
            "maximumRebate": round_currency(new_rebate_limit),
            "actualRebate": round_currency(new_rebate_amount),
            "taxAfterRebate": round_currency(new_tax_after_rebate),
            "eligible": new_eligible,
            "reason": new_reason,
        },
        {
            "step": "marginalRelief",
            "regime": "newRegime",
            "taxBeforeMarginalRelief": round_currency(new_tax_before_rebate),
            "marginalRelief": round_currency(new_marginal_relief),
            "taxAfterMarginalRelief": round_currency(new_tax_plus_surcharge - new_marginal_relief),
        },
    ])

    result = {
        "status": "success",
        "assessmentYear": assessment_year,
        "financialSummary": _build_financial_summary(request, max(old_regime_taxable, new_regime_taxable), total_income, total_expenses, total_losses),
        "oldRegime": {
            "grossIncome": round_currency(total_income),
            "deductions": [],
            "taxableIncome": round_currency(old_regime_taxable),
            "taxBeforeRebate": round_currency(old_tax_before_rebate),
            "rebate87A": round_currency(old_rebate_amount),
            "surcharge": round_currency(old_surcharge),
            "marginalRelief": round_currency(old_marginal_relief),
            "cess": round_currency(old_cess),
            "totalTax": round_currency(old_final_tax),
            "tds": round_currency(tds),
            "balancePayable": round_currency(old_balance),
            "rulesApplied": [old_rule],
            "slabBreakdown": old_steps,
        },
        "newRegime": {
            "grossIncome": round_currency(total_income),
            "deductions": [],
            "taxableIncome": round_currency(new_regime_taxable),
            "taxBeforeRebate": round_currency(new_tax_before_rebate),
            "rebate87A": round_currency(new_rebate_amount),
            "surcharge": round_currency(new_surcharge),
            "marginalRelief": round_currency(new_marginal_relief),
            "cess": round_currency(new_cess),
            "totalTax": round_currency(new_final_tax),
            "tds": round_currency(tds),
            "balancePayable": round_currency(new_balance),
            "rulesApplied": [new_rule],
            "slabBreakdown": new_steps,
        },
        "comparison": {
            "difference": round_currency(new_final_tax - old_final_tax),
            "oldIsLower": old_final_tax < new_final_tax,
            "newIsLower": new_final_tax < old_final_tax,
            "assumptionsUsed": assumptions,
        },
        "deductionOpportunities": [
            {
                "section": "80C",
                "regime": "old",
                "eligibleAmount": Decimal("150000"),
                "status": "Potential opportunity",
                "evidenceRequired": "Investment proof required",
            },
            {
                "section": "80D",
                "regime": "old",
                "eligibleAmount": Decimal("25000"),
                "status": "Potential opportunity",
                "evidenceRequired": "Policy premium proof required",
            },
        ],
        "warnings": warnings,
        "assumptions": assumptions,
        "rulesApplied": [old_rule, new_rule],
        "deductionLedger": deduction_ledger,
        "auditTrail": audit_trail,
    }

    if request.get("investments"):
        warnings.append("Investment entries are captured for review; all deductions must be evidence-backed and capped by statutory limits.")
    if request.get("capitalGains"):
        assumptions.append("Capital gains are treated through the standard rule engine and require separate heading-specific review for special-rate income.")

    return result
