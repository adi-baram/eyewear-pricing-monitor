"""Central configuration for the Eyewear Pricing Monitor."""

# Scraper settings
BASE_URL = "https://www.designeroptics.com"
SEARCH_URL_TEMPLATE = BASE_URL + "/search?type=product&q={query}"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
REQUEST_TIMEOUT = 15  # seconds

# Rate limiting
RATE_LIMIT_DELAY = 1.5  # seconds between requests

# Retry settings
MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 2  # exponential backoff: 2^attempt seconds

# Pricing strategy
UNDERCUT_PERCENT = 3  # undercut competitor by this percentage
MIN_PRICE_FLOOR_PERCENT = 20  # never go below this % of our original price

# Output files
OUTPUT_CSV = "results.csv"
OUTPUT_JSON = "results.json"
