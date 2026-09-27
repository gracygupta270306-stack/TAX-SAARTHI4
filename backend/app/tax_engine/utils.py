from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("100")


def to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value)).quantize(Decimal("0.01"))


def money(value) -> Decimal:
    return to_decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def round_currency(value) -> Decimal:
    return money(value)


def apply_percentage(base: Decimal, rate: Decimal) -> Decimal:
    return (base * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def safe_divide(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator == 0:
        return Decimal("0")
    return (numerator / denominator).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
