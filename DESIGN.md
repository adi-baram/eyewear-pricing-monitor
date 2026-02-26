# Design Document — Eyewear Pricing Monitor

## System Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌──────────────┐
│  test_products   │     │   scraper    │     │ designeroptics│
│     .csv         │────▶│   .py        │────▶│   .com       │
│  (50 products)   │     │              │◀────│  (HTTP GET)  │
└─────────────────┘     └──────┬───────┘     └──────────────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   matcher    │
                        │   .py        │
                        │ (UPC + name) │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐
                        │   pricing    │
                        │   .py        │
                        │ (undercut %) │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐     ┌──────────────┐
                        │   report     │────▶│  results.csv │
                        │   .py        │────▶│  results.json│
                        │              │────▶│  (console)   │
                        └──────────────┘     └──────────────┘
```

## Data Flow

1. **Load**: Read `test_products.csv` with UPC, brand, name, price, discount price
2. **Scrape**: For each product, search designeroptics.com using `{brand} {model} eyeglasses`
3. **Parse**: Extract product data from `searchResult.push({...})` JSON blocks in HTML
4. **Match**: Compare UPC codes (primary) or model numbers (fallback) to find the same product
5. **Price**: Apply pricing strategy to suggest optimal prices
6. **Report**: Output console summary + CSV/JSON exports

## Technology Choices

| Choice | Rationale |
|--------|-----------|
| **Python 3.11** | Modern features (type hints, match), wide ecosystem |
| **requests** | Simple, reliable HTTP client — sufficient since no JS rendering needed |
| **No browser automation** | Product data is in the HTML as JSON — no Selenium/Playwright needed |
| **stdlib only** (besides requests) | Minimal dependencies = easier deployment, fewer security risks |
| **regex parsing** | `searchResult.push({...})` blocks are well-structured; regex is fast and sufficient |
| **unittest** | Built-in, no extra dependencies; pytest-compatible for better output |

## Pricing Strategy

**Smart Competitive Pricing:**

- If competitor price < our discounted price → undercut competitor by 3%
- If we're already cheaper → keep our price (no change)
- Floor: never go below 20% of our original price (margin protection)

This balances competitiveness with profitability. The undercut percentage and floor are configurable in `config.py`.

## Product Matching

Two-tier matching strategy:

1. **UPC Match (primary)**: Compare our UPC against `barcode` fields in competitor product variants. UPCs are normalized by stripping leading zeros.
2. **Model Number Match (fallback)**: Extract model numbers (e.g., "BE2108", "HC6065") from product names and search for them in competitor titles.

UPC matching is preferred because it's exact. Name matching is fuzzy and may produce false positives for products that share a model but differ in color/variant.

## Scalability Considerations

- **Rate limiting**: 1.5s delay between requests to be respectful to the target site
- **Retry with backoff**: Exponential backoff (2^attempt seconds) for transient failures
- **Stateless design**: Each run is independent; no database or state to manage
- **Parallelism potential**: The current sequential approach could be converted to async (aiohttp) for faster scraping, but rate limiting makes this less impactful

## Trade-offs

| Decision | Trade-off |
|----------|-----------|
| Sequential scraping | Slower but simpler and respects rate limits |
| Regex parsing | Fast but brittle if site changes HTML structure |
| No database | Simple but no historical price tracking |
| Single competitor | Focused but doesn't capture the full market |

## Future Improvements

- **Multiple competitors**: Add scrapers for other eyewear retailers
- **Price history**: Store results in SQLite to track price trends over time
- **Async scraping**: Use aiohttp for concurrent requests (with rate limiting)
- **Scheduled runs**: Cron job or cloud function for automatic daily monitoring
- **Alerting**: Email/Slack notifications when significant price changes are detected
- **Dashboard**: Web UI to visualize pricing data and trends
