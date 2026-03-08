# Session Notes — Eyewear Pricing Monitor

## Project Overview
Built a Python service that scrapes designeroptics.com for competitor pricing, matches products to our 50-product catalog via UPC barcodes, suggests optimal prices using a tiered strategy, and generates reports (console + CSV + JSON). Final match rate: 49/50 (98%).

---

## Architecture Decisions

### Why HTTP requests (not browser automation)?
Product data on designeroptics.com is embedded as JSON in `searchResult.push({...})` blocks in the HTML. No JavaScript rendering needed — simple `requests.get()` + regex parsing is faster and has zero dependencies beyond `requests`.

### Why regex instead of BeautifulSoup/lxml?
The data is inside `<script>` tags as structured JSON. Regex extracts it directly — no DOM parsing overhead. Trade-off: it's brittle if the site changes markup, but sufficient for this use case.

### Why UPC matching as primary strategy?
UPC (barcode) is a universal product identifier — it guarantees an exact match regardless of naming differences. Model number matching is the fallback for cases where UPC isn't available.

---

## Pricing Algorithm — Tiered Strategy

**Why tiered instead of flat undercut?**
The data showed price gaps ranging from 3% to 63%. A flat 3% undercut doesn't make sense when the gap is 50% — and undercutting by 5% when the gap is only 3% is unnecessarily aggressive.

| Gap Size | Action | Rationale |
|----------|--------|-----------|
| We're cheaper | Keep price | No margin sacrifice needed |
| < 5% | Match competitor | Small gap — staying close is enough |
| 5-20% | Undercut by 3% | Win on price without deep cuts |
| > 20% | Undercut by 5% | Aggressive repositioning needed |
| Always | Floor at 20% of original | Margin protection |

**Interview point:** In production, the floor should be based on actual product cost/margin data, not a fixed percentage. Different brands have different margin structures.

---

## Key Challenge: Search Query Matching

### The Problem
Initial implementation matched only **18/50 products**. designeroptics.com names products differently than our catalog.

### Issues Discovered (iteratively)

1. **Brand prefixes stripped** — We search "Burberry BE2073", they list it as "Burberry 2073". The "BE" prefix is dropped.
   - Fix: Generate alternate query without brand prefix (BE, AX, MK, HC, VE, TY, MU).

2. **Slashes cause zero results** — "Adidas AOM001O/N" returns 0 results. They list it as "AOM001O_N".
   - Fix: Generate query with base model (strip everything after `/`).

3. **Sunglasses vs eyeglasses** — "Kate Spade Avaline2/S" has `/S` suffix = sunglasses. We were appending "eyeglasses".
   - Fix: Detect `/S` suffix, use "sunglasses" in query.

4. **Alphabetical model names** — "Kate Spade Luella", "Renne", "Emilyn" have no digits. Our regex required a digit in the model number, so it fell back to just "Kate Spade eyeglasses" (too broad).
   - Fix: Strip known color words, use the word before colors as the model name.

5. **False early stopping** — "Burberry BE2073 eyeglasses" returned 24 generic Burberry results. Scraper stopped because results were non-empty, but none matched.
   - Fix: Run matcher after each query variant, stop only when a match is found (not just when results exist).

6. **Deduplication bug** — Used `url` field for dedup, but search results don't have a `url` key. All results collapsed to 1.
   - Fix: Deduplicate by `id` field with `title` fallback.

### Result
Match rate went from **18/50 → 49/50 (98%)**. Only unmatched: Miu Miu MU01YV (not carried by competitor).

### Design principle
All fixes are **general** — no hardcoded brand names or product-specific logic. The query generator produces multiple variants and the pipeline tries them in order.

---

## Performance Optimization

### Problem
Running all query variants for every product was slow — each variant = 1 HTTP request + 1.5s rate limit delay.

### Solution
**Early-stop matching**: try queries in order, run the matcher after each one, stop as soon as a UPC match is found. Most products match on query #1 or #2. Only products that genuinely need alternate queries use extra requests.

---

## Docker

### Problem
macOS version (Monterey/Darwin 22.6.0) was incompatible with latest Docker Desktop.

### Solution
Created a GitHub Actions workflow (`.github/workflows/docker-demo.yml`) that:
1. Builds the Docker image
2. Runs all 32 unit tests inside the container
3. Executes the pipeline with 5 products

This serves as proof the Dockerfile works. The workflow runs automatically on push to main.

---

## Non-Functional Requirements

- **Rate limiting**: 1.5s delay between requests (configurable in `config.py`)
- **Retries**: Up to 3 attempts per request with exponential backoff (1s, 2s, 4s)
- **Timeout**: 15s per request
- **Graceful failure**: Network errors return empty results, product shows as "unmatched"

---

## File Structure

| File | Lines | Purpose |
|------|-------|---------|
| `config.py` | ~25 | All settings in one place |
| `scraper.py` | ~150 | Search queries + HTTP + JSON parsing |
| `matcher.py` | ~100 | UPC matching + model number fallback |
| `pricing.py` | ~90 | Tiered pricing algorithm |
| `report.py` | ~100 | Console + CSV + JSON reports |
| `main.py` | ~95 | Orchestrator with CLI args |
| `test_pricing.py` | ~170 | 32 unit tests |

---

## What I Would Improve With More Time

1. **Multiple competitors** — scrape other eyewear retailers for a broader market view
2. **Price history** — SQLite database to track trends over time
3. **Async scraping** — `aiohttp` for concurrent requests (with rate limiting)
4. **Real margin data** — pricing floor based on actual product costs
5. **Alerting** — email/Slack notifications on significant price changes
6. **Scheduled runs** — cron job or cloud function for daily monitoring

---

## Mistakes / What I'd Do Differently

- **Missed first progress email** — misunderstood the timing requirement. Would set a recurring timer from the start next time.
- **Started with flat undercut** — switched to tiered later. Should have thought through the pricing strategy earlier instead of defaulting to the simplest option.
