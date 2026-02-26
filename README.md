# Eyewear Pricing Monitor

A Python service that scrapes competitor pricing from designeroptics.com, matches products to our catalog, suggests optimal prices, and generates reports.

## Prerequisites

- Python 3.11+
- pip

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Run the full pipeline

```bash
python3 main.py
```

This will:
1. Load the product catalog from `test_products.csv`
2. Scrape competitor prices from designeroptics.com
3. Match products by UPC (with model number fallback)
4. Suggest optimal prices based on competitive analysis
5. Output a console report + `results.csv` + `results.json`

### Options

```bash
python3 main.py --help

# Process only first N products (for testing)
python3 main.py --limit 5

# Use a different catalog file
python3 main.py --catalog my_products.csv

# Custom output filenames
python3 main.py --output-csv my_results.csv --output-json my_results.json
```

### Run individual components

```bash
# Test the scraper standalone (scrapes 3 products)
python3 scraper.py

# Test the matcher
python3 matcher.py

# Test the pricing algorithm
python3 pricing.py
```

### Run unit tests

```bash
python3 -m pytest test_pricing.py -v
```

## Docker

```bash
# Build
docker build -t eyewear-monitor .

# Run
docker run eyewear-monitor

# Run with custom limit
docker run eyewear-monitor python3 main.py --limit 5
```

## Configuration

Edit `config.py` to adjust:

| Setting | Default | Description |
|---------|---------|-------------|
| `RATE_LIMIT_DELAY` | 1.5s | Delay between HTTP requests |
| `MAX_RETRIES` | 3 | Max retry attempts per request |
| `UNDERCUT_PERCENT` | 3% | How much to undercut competitor prices |
| `MIN_PRICE_FLOOR_PERCENT` | 20% | Minimum price as % of original (margin protection) |

## Project Structure

```
├── config.py           # Configuration settings
├── scraper.py          # Web scraper for designeroptics.com
├── matcher.py          # Product matching (UPC + name fallback)
├── pricing.py          # Pricing algorithm
├── report.py           # Report generation (CSV, JSON, console)
├── main.py             # Orchestrator / entry point
├── test_pricing.py     # Unit tests
├── test_products.csv   # Input product catalog
├── Dockerfile          # Container setup
├── README.md           # This file
└── DESIGN.md           # Architecture & design decisions
```
