"""Orchestrator: load catalog, scrape, match, price, report."""

import argparse
import csv
import time

import config
from scraper import extract_search_queries, search_product
from matcher import match_product
from pricing import suggest_price
from report import generate_report, export_csv, export_json


def load_catalog(filepath: str) -> list[dict]:
    """Load product catalog from CSV."""
    products = []
    with open(filepath, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("upc"):
                continue
            products.append({
                "upc": row["upc"].strip(),
                "brand": row["brand"].strip(),
                "item_name": row["item name"].strip(),
                "price": float(row["price"]),
                "discount_price": float(row["price after discount"]),
            })
    return products


def process_product(product: dict, index: int, total: int) -> dict:
    """Search, match, and price a single product.

    Tries query variants in order. Stops as soon as a match is found
    to minimize HTTP requests.
    """
    queries = extract_search_queries(product["item_name"])
    match = None

    for qi, query in enumerate(queries):
        print(f"[{index}/{total}] Searching: {query}")
        search_results = search_product(query)
        print(f"  Found {len(search_results)} result(s)")

        match = match_product(product, search_results)
        if match:
            print(f"  Matched: {match['competitor_title']} "
                  f"(${match['competitor_price']:.2f}, {match['match_type']})")
            break

        if qi < len(queries) - 1:
            print("  No match, trying next query...")
            time.sleep(config.RATE_LIMIT_DELAY)

    pricing = None
    if match:
        pricing = suggest_price(
            our_price=product["price"],
            our_discount_price=product["discount_price"],
            competitor_price=match["competitor_price"],
        )

    return {**product, "match": match, "pricing": pricing}


def run_pipeline(catalog_path: str, limit: int | None = None) -> list[dict]:
    """Run the full pipeline: load -> search -> match -> price."""
    catalog = load_catalog(catalog_path)
    if limit:
        catalog = catalog[:limit]
    print(f"Loaded {len(catalog)} products from {catalog_path}\n")

    results = []
    total = len(catalog)

    for i, product in enumerate(catalog, 1):
        result = process_product(product, i, total)
        results.append(result)

        if i < total:
            time.sleep(config.RATE_LIMIT_DELAY)

    return results


def main():
    parser = argparse.ArgumentParser(description="Eyewear Pricing Monitor")
    parser.add_argument(
        "--catalog", default="test_products.csv",
        help="Path to product catalog CSV (default: test_products.csv)",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit number of products to process (for testing)",
    )
    parser.add_argument(
        "--output-csv", default=config.OUTPUT_CSV,
        help=f"Output CSV filename (default: {config.OUTPUT_CSV})",
    )
    parser.add_argument(
        "--output-json", default=config.OUTPUT_JSON,
        help=f"Output JSON filename (default: {config.OUTPUT_JSON})",
    )
    args = parser.parse_args()

    results = run_pipeline(args.catalog, args.limit)

    # Generate reports
    report = generate_report(results)
    print("\n" + report)

    export_csv(results, args.output_csv)
    export_json(results, args.output_json)


if __name__ == "__main__":
    main()
