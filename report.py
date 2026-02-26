"""Report generation: console summary, CSV, and JSON exports."""

import csv
import json


def generate_report(results: list[dict]) -> str:
    """Generate a console-friendly text report from pipeline results."""
    lines = []
    lines.append("=" * 80)
    lines.append("EYEWEAR PRICING MONITOR — COMPETITIVE ANALYSIS REPORT")
    lines.append("=" * 80)

    matched = [r for r in results if r.get("match")]
    unmatched = [r for r in results if not r.get("match")]

    lines.append(f"\nProducts analyzed: {len(results)}")
    lines.append(f"Matches found:     {len(matched)}")
    lines.append(f"No match:          {len(unmatched)}")

    # Matched products detail
    if matched:
        lines.append("\n" + "-" * 80)
        lines.append("MATCHED PRODUCTS")
        lines.append("-" * 80)

        price_changes = []
        for r in matched:
            m = r["match"]
            p = r.get("pricing", {})
            lines.append(f"\n  {r['item_name']} (UPC: {r['upc']})")
            lines.append(f"    Match type:       {m['match_type']}")
            lines.append(f"    Competitor:        {m['competitor_title']}")
            lines.append(f"    Competitor price:  ${m['competitor_price']:.2f}")
            lines.append(f"    Our price:         ${r['price']:.2f}")
            lines.append(f"    Our discount:      ${r['discount_price']:.2f}")

            if p:
                lines.append(f"    Suggested price:   ${p['suggested_price']:.2f}")
                lines.append(f"    Change:            ${p['change_amount']:+.2f} "
                             f"({p['change_percent']:+.1f}%)")
                lines.append(f"    Reasoning:         {p['reasoning']}")
                price_changes.append(p["change_amount"])

        # Summary stats
        if price_changes:
            decreases = [c for c in price_changes if c < 0]
            lines.append("\n" + "-" * 80)
            lines.append("SUMMARY")
            lines.append("-" * 80)
            lines.append(f"  Products needing price change: {len(decreases)} / {len(matched)}")
            if decreases:
                total_reduction = sum(decreases)
                avg_reduction = total_reduction / len(decreases)
                lines.append(f"  Average reduction:  ${avg_reduction:.2f}")
                lines.append(f"  Total reduction:    ${total_reduction:.2f}")

    # Unmatched products
    if unmatched:
        lines.append("\n" + "-" * 80)
        lines.append("UNMATCHED PRODUCTS (no competitor data found)")
        lines.append("-" * 80)
        for r in unmatched:
            lines.append(f"  - {r['item_name']} (UPC: {r['upc']})")

    lines.append("\n" + "=" * 80)
    return "\n".join(lines)


def export_csv(results: list[dict], filename: str) -> None:
    """Export results to a CSV file."""
    fieldnames = [
        "upc", "brand", "item_name", "our_price", "our_discount_price",
        "match_type", "competitor_title", "competitor_price",
        "suggested_price", "change_amount", "change_percent", "reasoning",
    ]

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for r in results:
            m = r.get("match") or {}
            p = r.get("pricing") or {}
            writer.writerow({
                "upc": r["upc"],
                "brand": r["brand"],
                "item_name": r["item_name"],
                "our_price": r["price"],
                "our_discount_price": r["discount_price"],
                "match_type": m.get("match_type", ""),
                "competitor_title": m.get("competitor_title", ""),
                "competitor_price": m.get("competitor_price", ""),
                "suggested_price": p.get("suggested_price", ""),
                "change_amount": p.get("change_amount", ""),
                "change_percent": p.get("change_percent", ""),
                "reasoning": p.get("reasoning", ""),
            })

    print(f"CSV report saved to {filename}")


def export_json(results: list[dict], filename: str) -> None:
    """Export results to a JSON file."""
    output = []
    for r in results:
        m = r.get("match") or {}
        p = r.get("pricing") or {}
        output.append({
            "upc": r["upc"],
            "brand": r["brand"],
            "item_name": r["item_name"],
            "our_price": r["price"],
            "our_discount_price": r["discount_price"],
            "match": {
                "match_type": m.get("match_type"),
                "competitor_title": m.get("competitor_title"),
                "competitor_price": m.get("competitor_price"),
            } if m else None,
            "pricing": {
                "suggested_price": p.get("suggested_price"),
                "change_amount": p.get("change_amount"),
                "change_percent": p.get("change_percent"),
                "reasoning": p.get("reasoning"),
            } if p else None,
        })

    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

    print(f"JSON report saved to {filename}")
