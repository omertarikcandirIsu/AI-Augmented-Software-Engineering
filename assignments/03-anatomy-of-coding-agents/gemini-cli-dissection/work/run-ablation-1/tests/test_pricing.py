import pytest

from shopcart.pricing import apply_discount, apply_tax, calculate_shipping, final_total


def test_apply_tax():
    assert apply_tax(1000) == 1080


def test_no_code_means_no_discount():
    assert apply_discount(1000, None) == 1000


def test_percent_discount():
    assert apply_discount(2000, "SAVE25") == 1500


def test_fixed_discount_never_negative():
    assert apply_discount(500, "TENOFF") == 0


def test_invalid_code_raises():
    with pytest.raises(ValueError):
        apply_discount(1000, "BOGUS")


def test_shipping_under_threshold_pays_flat_fee():
    assert calculate_shipping(4999) == 599
    assert calculate_shipping(1000) == 599
    assert calculate_shipping(0) == 599


def test_shipping_free_at_threshold():
    assert calculate_shipping(5000) == 0


def test_shipping_free_above_threshold():
    assert calculate_shipping(7500) == 0


def test_empty_cart_pays_no_shipping():
    assert calculate_shipping(0, is_empty=True) == 0
    assert calculate_shipping(2000, is_empty=True) == 0


def test_final_total_empty():
    assert final_total(0) == 0
    assert final_total(0, is_empty=True) == 0


def test_final_total_under_threshold():
    # 2000 + 8% tax (160) + 599 shipping = 2759
    assert final_total(2000) == 2759


def test_final_total_free_shipping():
    # 5000 + 8% tax (400) + 0 shipping = 5400
    assert final_total(5000) == 5400
