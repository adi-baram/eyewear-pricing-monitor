"""Pricing algorithm: tiered competitive pricing based on gap size."""

import config


def suggest_price(
    our_price: float,
    our_discount_price: float,
    competitor_price: float,
) -> dict:
    """Suggest a price based on competitor pricing.

    Tiered strategy:
    - Already cheaper       -> keep our price
    - Gap < 5%              -> match competitor price (small gap, stay close)
    - Gap 5-20%             -> undercut competitor by 3% (moderate competition)
    - Gap > 20%             -> undercut competitor by 5% (aggressive repositioning)
    - Floor: never below 20% of our original price (margin protection)

    Returns a dict with suggested_price, change_amount, change_percent, reasoning.
    """
    floor = our_price * (config.MIN_PRICE_FLOOR_PERCENT / 100)

    if competitor_price >= our_discount_price:
        # We're already cheaper or equal
        suggested = our_discount_price
        reasoning = (
            f"Our price ${our_discount_price:.2f} is already at or below "
            f"competitor's ${competitor_price:.2f}. No change needed."
        )
    else:
        # Competitor is cheaper — determine gap and tier
        gap_percent = (
            (our_discount_price - competitor_price) / our_discount_price * 100
        )

        if gap_percent < config.SMALL_GAP_THRESHOLD:
            # Small gap: just match
            suggested = round(competitor_price, 2)
            reasoning = (
                f"Competitor at ${competitor_price:.2f} is {gap_percent:.1f}% cheaper "
                f"(small gap). Matching their price."
            )
        elif gap_percent <= config.LARGE_GAP_THRESHOLD:
            # Medium gap: moderate undercut
            undercut = config.UNDERCUT_MODERATE
            suggested = round(competitor_price * (1 - undercut / 100), 2)
            reasoning = (
                f"Competitor at ${competitor_price:.2f} is {gap_percent:.1f}% cheaper "
                f"(moderate gap). Undercutting by {undercut}%."
            )
        else:
            # Large gap: aggressive undercut
            undercut = config.UNDERCUT_AGGRESSIVE
            suggested = round(competitor_price * (1 - undercut / 100), 2)
            reasoning = (
                f"Competitor at ${competitor_price:.2f} is {gap_percent:.1f}% cheaper "
                f"(large gap). Aggressively undercutting by {undercut}%."
            )

        # Apply floor
        if suggested < floor:
            suggested = round(floor, 2)
            reasoning += (
                f" Capped at floor ${floor:.2f} "
                f"({config.MIN_PRICE_FLOOR_PERCENT}% of original ${our_price:.2f})."
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

    # Test 1: Large gap — aggressive undercut (5%)
    r = suggest_price(our_price=304, our_discount_price=274, competitor_price=200)
    assert r["suggested_price"] == 190.0  # 200 * 0.95
    print(f"Test 1 (large gap): ${r['suggested_price']:.2f} — {r['reasoning']}")

    # Test 2: Already cheaper — no change
    r = suggest_price(our_price=304, our_discount_price=150, competitor_price=200)
    assert r["suggested_price"] == 150.0
    print(f"Test 2 (already cheaper): ${r['suggested_price']:.2f} — {r['reasoning']}")

    # Test 3: Floor cap
    r = suggest_price(our_price=300, our_discount_price=270, competitor_price=50)
    assert r["suggested_price"] == 60.0  # floor = 300 * 0.20
    print(f"Test 3 (floor cap): ${r['suggested_price']:.2f} — {r['reasoning']}")

    # Test 4: Equal prices — no change
    r = suggest_price(our_price=200, our_discount_price=180, competitor_price=180)
    assert r["suggested_price"] == 180.0
    print(f"Test 4 (equal): ${r['suggested_price']:.2f} — {r['reasoning']}")

    # Test 5: Small gap — match competitor
    r = suggest_price(our_price=200, our_discount_price=100, competitor_price=97)
    assert r["suggested_price"] == 97.0  # gap 3%, just match
    print(f"Test 5 (small gap): ${r['suggested_price']:.2f} — {r['reasoning']}")

    # Test 6: Medium gap — moderate undercut (3%)
    r = suggest_price(our_price=200, our_discount_price=100, competitor_price=90)
    assert r["suggested_price"] == 87.3  # 90 * 0.97, gap=10%
    print(f"Test 6 (medium gap): ${r['suggested_price']:.2f} — {r['reasoning']}")

    print("\nAll pricing tests passed!")
