"""Product matching logic: match our catalog products to competitor results."""

import re


def normalize_upc(upc: str) -> str:
    """Normalize a UPC by stripping leading zeros and whitespace."""
    return upc.strip().lstrip("0")


def extract_model_number(item_name: str) -> str | None:
    """Extract model number from an item name (e.g. 'BE2108' from 'Burberry BE2108 Black')."""
    match = re.search(r"[A-Z]{2,}\d[\w/]*", item_name)
    return match.group(0) if match else None


def match_by_upc(our_upc: str, search_results: list[dict]) -> dict | None:
    """Try to match by UPC (barcode) across all search result variants.

    Returns the matched variant dict with parent product info, or None.
    """
    norm_upc = normalize_upc(our_upc)

    for product in search_results:
        for variant in product.get("variants", []):
            barcode = variant.get("barcode", "")
            if barcode and normalize_upc(str(barcode)) == norm_upc:
                return {
                    "match_type": "upc",
                    "competitor_title": product.get("title", ""),
                    "competitor_price": variant.get("price", 0) / 100,
                    "competitor_compare_price": variant.get("compare_at_price", 0) / 100
                    if variant.get("compare_at_price")
                    else None,
                    "matched_barcode": barcode,
                    "product_url": product.get("url", ""),
                }
    return None


def match_by_name(item_name: str, search_results: list[dict]) -> dict | None:
    """Fallback: match by model number in the product title.

    Returns the best match or None.
    """
    our_model = extract_model_number(item_name)
    if not our_model:
        return None

    for product in search_results:
        title = product.get("title", "")
        if our_model.lower() in title.lower():
            # Use the first variant's price (or product-level price)
            price = product.get("price", 0) / 100
            variants = product.get("variants", [])
            if variants:
                price = variants[0].get("price", 0) / 100

            return {
                "match_type": "name",
                "competitor_title": title,
                "competitor_price": price,
                "competitor_compare_price": None,
                "matched_barcode": None,
                "product_url": product.get("url", ""),
            }
    return None


def match_product(our_product: dict, search_results: list[dict]) -> dict | None:
    """Match our product to competitor search results.

    Tries UPC match first, then falls back to model number match.
    """
    # Primary: UPC match
    result = match_by_upc(our_product["upc"], search_results)
    if result:
        return result

    # Fallback: name/model match
    return match_by_name(our_product["item_name"], search_results)


if __name__ == "__main__":
    print("=== Matcher Standalone Test ===\n")

    # Test UPC normalization
    assert normalize_upc("0713132395233") == "713132395233"
    assert normalize_upc("713132395233") == "713132395233"
    print("UPC normalization: OK")

    # Test model extraction
    assert extract_model_number("Burberry BE2108 Black") == "BE2108"
    assert extract_model_number("Armani Exchange AX3016 Black") == "AX3016"
    assert extract_model_number("Michael Kors MK3056 Naxos Rose Gold") == "MK3056"
    assert extract_model_number("Coach HC6065 Tortoise") == "HC6065"
    print("Model extraction: OK")

    # Test UPC matching with sample data
    sample_results = [{
        "title": "Burberry BE2108 Eyeglasses",
        "price": 15100,
        "url": "/products/burberry-be2108",
        "variants": [
            {"barcode": "0713132395233", "price": 15100},
            {"barcode": "0713132395240", "price": 15100},
        ],
    }]

    our = {"upc": "713132395233", "item_name": "Burberry BE2108 Black"}
    m = match_product(our, sample_results)
    assert m is not None
    assert m["match_type"] == "upc"
    assert m["competitor_price"] == 151.00
    print(f"UPC match: OK — {m}")

    # Test name fallback
    our_no_upc = {"upc": "9999999999999", "item_name": "Burberry BE2108 Black"}
    m2 = match_product(our_no_upc, sample_results)
    assert m2 is not None
    assert m2["match_type"] == "name"
    print(f"Name match: OK — {m2}")

    # Test no match
    our_none = {"upc": "0000000000000", "item_name": "Unknown XY1234 Blue"}
    m3 = match_product(our_none, sample_results)
    assert m3 is None
    print("No match: OK")

    print("\nAll matcher tests passed!")
