"""Web scraper for designeroptics.com product data."""

import json
import re
import time

import requests

import config


def _detect_product_type(model: str) -> str:
    """Detect if a product is sunglasses based on /S suffix."""
    if model.endswith("/S"):
        return "sunglasses"
    return "eyeglasses"


def _extract_brand_and_model(item_name: str) -> tuple[str, str] | None:
    """Extract (brand, model) from item name, stripping colors after comma."""
    # Strip color info after the first comma
    name = item_name.split(",")[0].strip()

    # Try alphanumeric model pattern: "Coach HC6065", "Kate Spade Avaline2/S"
    match = re.match(r"^(.+?\s+([A-Z][A-Za-z]*\d[\w/]*))", name)
    if match:
        return match.group(1).rsplit(maxsplit=1)[0], match.group(2)

    # Fallback for purely alphabetical model names: "Kate Spade Luella Pink"
    # Take everything before common color words as brand+model
    color_pattern = (
        r"\s+(?:Black|Tortoise|Gold|Pink|Clear|Blue|Beige|Brown|White|Red|"
        r"Gray|Grey|Purple|Green|Rose|Shiny|Matte|Multicolor|Eggplant|Bronze)\b"
    )
    cleaned = re.split(color_pattern, name, maxsplit=1)[0].strip()
    parts = cleaned.split()
    if len(parts) >= 3:
        # Assume last word is model, rest is brand: "Kate Spade Luella"
        return " ".join(parts[:-1]), parts[-1]

    return None


def extract_search_queries(item_name: str) -> list[str]:
    """Extract search queries from a product name, ordered by specificity.

    Returns multiple query variants to try. Handles:
    - Brand prefix stripping (TY2129U -> 2129U)
    - Slash in model numbers (Avaline2/S -> Avaline2, AOM001O/N -> AOM001O)
    - Sunglasses detection (/S suffix)
    - Alphabetical model names (Luella, Renne, Emilyn)
    """
    queries = []
    seen = set()

    def add(q: str) -> None:
        if q not in seen:
            seen.add(q)
            queries.append(q)

    result = _extract_brand_and_model(item_name)
    if not result:
        parts = item_name.split()
        add((" ".join(parts[:2]) if len(parts) >= 2 else item_name) + " eyeglasses")
        return queries

    brand, model = result
    product_type = _detect_product_type(model)

    # 1. Full brand + model + product type
    add(f"{brand} {model} {product_type}")

    # 2. If model has a slash, try without the slash portion
    if "/" in model:
        base_model = model.split("/")[0]
        add(f"{brand} {base_model} {product_type}")

    # 3. Strip brand prefix (TY from TY2129U, MU from MU01YV)
    stripped = re.sub(r"^[A-Z]{2}", "", model)
    if stripped != model:
        add(f"{brand} {stripped} {product_type}")
        if "/" in stripped:
            add(f"{brand} {stripped.split('/')[0]} {product_type}")

    # 4. Try without product type suffix as last resort
    add(f"{brand} {model}")

    return queries


def parse_search_results(html: str) -> list[dict]:
    """Parse searchResult.push({...}) blocks from HTML into dicts."""
    results = []
    pattern = r"searchResult\.push\((\{.*?\})\);"
    for match in re.finditer(pattern, html, re.DOTALL):
        json_str = match.group(1)
        try:
            data = json.loads(json_str)
            results.append(data)
        except json.JSONDecodeError:
            continue
    return results


def search_product(query: str) -> list[dict]:
    """Search designeroptics.com for a product query.

    Returns a list of product dicts parsed from the page.
    """
    url = config.SEARCH_URL_TEMPLATE.format(query=requests.utils.quote(query))
    headers = {"User-Agent": config.USER_AGENT}

    for attempt in range(config.MAX_RETRIES):
        try:
            resp = requests.get(url, headers=headers, timeout=config.REQUEST_TIMEOUT)
            resp.raise_for_status()
            return parse_search_results(resp.text)
        except requests.RequestException as e:
            if attempt < config.MAX_RETRIES - 1:
                wait = config.RETRY_BACKOFF_BASE ** attempt
                print(f"  Retry {attempt + 1}/{config.MAX_RETRIES} for '{query}' "
                      f"(waiting {wait}s): {e}")
                time.sleep(wait)
            else:
                print(f"  Failed after {config.MAX_RETRIES} attempts for '{query}': {e}")
                return []


if __name__ == "__main__":
    import csv

    print("=== Scraper Standalone Test ===\n")

    with open("test_products.csv", newline="") as f:
        reader = csv.DictReader(f)
        catalog = []
        for row in reader:
            catalog.append({
                "upc": row["upc"],
                "brand": row["brand"],
                "item_name": row["item name"],
            })

    print("Query extraction examples:")
    for p in catalog[:5]:
        print(f"  {p['item_name']!r} -> {extract_search_queries(p['item_name'])}")
    print()

    # Scrape a small sample
    for p in catalog[:3]:
        query = extract_search_queries(p["item_name"])[0]
        print(f"Searching: {query}")
        results = search_product(query)
        print(f"  Found {len(results)} result(s)")
        for r in results[:3]:
            print(f"    - {r.get('title', '?')}")
        time.sleep(config.RATE_LIMIT_DELAY)
