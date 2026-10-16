import pytest

from shopcart import Cart


def test_empty_cart_total_is_zero():
    assert Cart().total() == 0


def test_add_single_item():
    cart = Cart()
    cart.add_item("MUG")
    assert cart.items == {"MUG": 1}
    assert cart.subtotal() == 1200


def test_add_same_item_twice_increments_quantity():
    cart = Cart()
    cart.add_item("MUG")
    cart.add_item("MUG", 2)
    assert cart.items == {"MUG": 3}


def test_remove_item_decrements_then_deletes():
    cart = Cart()
    cart.add_item("CAP", 2)
    cart.remove_item("CAP")
    assert cart.items == {"CAP": 1}
    cart.remove_item("CAP")
    assert cart.items == {}


def test_unknown_sku_raises():
    with pytest.raises(ValueError):
        Cart().add_item("NOPE")


def test_invalid_code_raises():
    with pytest.raises(ValueError):
        Cart().apply_code("FREESTUFF")


def test_total_includes_tax():
    cart = Cart()
    cart.add_item("TEE")
    # Updated for flat shipping fee ($5.99 / 599 cents) on orders under $50.00
    assert cart.total() == 2759  # 2000 + 8% tax (2160) + 599 shipping


def test_percent_discount():
    cart = Cart()
    cart.add_item("MUG", 2)
    cart.apply_code("SAVE10")
    # Updated for flat shipping fee ($5.99 / 599 cents) on orders under $50.00
    assert cart.total() == 2932  # (2400 - 10%) + 8% tax (2333) + 599 shipping


def test_fixed_discount_applied_before_tax():
    cart = Cart()
    cart.add_item("TEE")
    cart.add_item("TEE")
    cart.apply_code("TENOFF")
    # Updated for flat shipping fee ($5.99 / 599 cents) on orders under $50.00
    assert cart.total() == 3839  # (4000 - 1000) + 8% tax (3240) + 599 shipping


def test_free_shipping_at_threshold():
    cart = Cart()
    # 1 TEE (2000) + 2 CAPs (3000) = 5000 cents ($50.00)
    cart.add_item("TEE")
    cart.add_item("CAP", 2)
    assert cart.subtotal() == 5000
    # Exactly $50.00 qualifies for free shipping: 5000 + 8% tax = 5400, no shipping fee
    assert cart.total() == 5400


def test_discount_drops_subtotal_below_threshold_incurs_shipping():
    cart = Cart()
    # 1 TEE (2000) + 2 CAPs (3000) = 5000 cents ($50.00)
    cart.add_item("TEE")
    cart.add_item("CAP", 2)
    cart.apply_code("SAVE10")
    # Discounted subtotal: 4500 cents (< 5000), incurs $5.99 shipping
    # Tax: 4500 * 1.08 = 4860; Total: 4860 + 599 = 5459
    assert cart.total() == 5459


def test_discount_retains_free_shipping_if_at_or_above_threshold():
    cart = Cart()
    # 3 TEEs = 6000 cents
    cart.add_item("TEE", 3)
    cart.apply_code("TENOFF")
    # Discounted subtotal: 6000 - 1000 = 5000 cents (>= 5000), qualifies for free shipping
    # Tax: 5000 * 1.08 = 5400; Total: 5400 + 0 = 5400
    assert cart.total() == 5400
