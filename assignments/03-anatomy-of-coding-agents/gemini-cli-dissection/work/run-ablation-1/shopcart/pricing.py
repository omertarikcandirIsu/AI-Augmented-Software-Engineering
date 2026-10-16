"""Pricing rules: discounts and tax. All amounts are integer cents."""
from __future__ import annotations

TAX_RATE = 0.08
SHIPPING_FEE = 599
FREE_SHIPPING_THRESHOLD = 5000

# code -> (kind, value). "percent" values are whole percents; "fixed" values are cents.
DISCOUNT_CODES = {
    "SAVE10": ("percent", 10),
    "SAVE25": ("percent", 25),
    "TENOFF": ("fixed", 1000),
}


def validate_code(code: str) -> None:
    if code not in DISCOUNT_CODES:
        raise ValueError(f"invalid discount code: {code}")


def apply_discount(amount_cents: int, code: str | None) -> int:
    """Return the amount after applying a discount code. Never goes below zero."""
    if code is None:
        return amount_cents
    validate_code(code)
    kind, value = DISCOUNT_CODES[code]
    if kind == "percent":
        return round(amount_cents * (100 - value) / 100)
    return max(0, amount_cents - value)


def apply_tax(amount_cents: int) -> int:
    return round(amount_cents * (1 + TAX_RATE))


def calculate_shipping(subtotal_after_discount: int, is_empty: bool = False) -> int:
    """Return shipping fee in cents.

    Orders pay a flat $5.99 shipping fee (599 cents).
    Shipping is free when the subtotal after discount, before tax is $50.00 or more (5000 cents).
    An empty cart pays no shipping.
    """
    if is_empty or subtotal_after_discount >= FREE_SHIPPING_THRESHOLD:
        return 0
    return SHIPPING_FEE


def final_total(subtotal_cents: int, code: str | None = None, is_empty: bool | None = None) -> int:
    """Total the customer pays for a given subtotal and optional discount code."""
    if is_empty is None:
        is_empty = (subtotal_cents == 0)
    if is_empty:
        return 0
    # Discount is applied before tax, per store policy.
    discounted = apply_discount(subtotal_cents, code)
    shipping = calculate_shipping(discounted, is_empty=is_empty)
    return apply_tax(discounted) + shipping
