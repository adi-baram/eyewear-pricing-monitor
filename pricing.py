"""Pricing algorithm: suggest optimal prices based on competitor data."""

import config


def suggest_price(
    our_price: float,
    our_discount_price: float,
    competitor_price: float,
) -> dict:
    """Suggest a price based on competitor pricing.

    Strategy:
    - If competitor is cheaper than our discounted price -> undercut them by UNDERCUT_PERCENT
    - If we're already cheaper -> keep our discounted price
    - Never go below MIN_PRICE_FLOOR_PERCENT of our original price

    Returns a dict with suggested_price, change_amount, change_percent, reasoning.
    """
    floor = our_price * (config.MIN_PRICE_FLOOR_PERCENT / 100)

    if competitor_price < our_discount_price:
        # Competitor is cheaper — undercut them
        suggested = competitor_price * (1 - config.UNDERCUT_PERCENT / 100)
        suggested = round(suggested, 2)

        if suggested < floor:
            suggested = round(floor, 2)
            reasoning = (
                f"Competitor at ${competitor_price:.2f} is cheaper. "
                f"Undercut would be ${competitor_price * (1 - config.UNDERCUT_PERCENT / 100):.2f}, "
                f"but capped at floor ${floor:.2f} ({config.MIN_PRICE_FLOOR_PERCENT}% of original)."
            )
        else:
            reasoning = (
                f"Competitor at ${competitor_price:.2f} is cheaper than our "
                f"${our_discount_price:.2f}. Suggest undercutting by {config.UNDERCUT_PERCENT}%."
            )
    else:
        # We're already competitive
        suggested = our_discount_price
        reasoning = (
            f"Our price ${our_discount_price:.2f} is already at or below "
            f"competitor's ${competitor_price:.2f}. No change needed."
        )

    change_amount = round(suggested - our_discount_price, 2)
    change_percent = round(
        (change_amount / our_discount_price * 100) if our_discount_price else 0, 2
    )

    return {
        "suggested_price": suggested,
        "change_amount": change_amount,
        "change_percent": change_percent,
        "reasoning": reasoning,
    }


if __name__ == "__main__":
    print("=== Pricing Algorithm Tests ===\n")

    # Test 1: Competitor is cheaper — should undercut
    r = suggest_price(our_price=304, our_discount_price=274, competitor_price=200)
    assert r["suggested_price"] == 194.0  # 200 * 0.97
    assert r["change_amount"] < 0
    print(f"Test 1 (undercut): ${r['suggested_price']:.2f}, "
          f"change: {r['change_percent']:.1f}% — {r['reasoning']}")

    # Test 2: We're already cheaper — no change
    r = suggest_price(our_price=304, our_discount_price=150, competitor_price=200)
    assert r["suggested_price"] == 150.0
    assert r["change_amount"] == 0
    print(f"Test 2 (already cheaper): ${r['suggested_price']:.2f}, "
          f"change: {r['change_percent']:.1f}% — {r['reasoning']}")

    # Test 3: Undercut would go below floor — cap at floor
    r = suggest_price(our_price=300, our_discount_price=270, competitor_price=50)
    assert r["suggested_price"] == 60.0  # floor = 300 * 0.20 = 60
    print(f"Test 3 (floor cap): ${r['suggested_price']:.2f}, "
          f"change: {r['change_percent']:.1f}% — {r['reasoning']}")

    # Test 4: Equal prices — no change
    r = suggest_price(our_price=200, our_discount_price=180, competitor_price=180)
    assert r["suggested_price"] == 180.0
    assert r["change_amount"] == 0
    print(f"Test 4 (equal): ${r['suggested_price']:.2f}, "
          f"change: {r['change_percent']:.1f}% — {r['reasoning']}")

    print("\nAll pricing tests passed!")
