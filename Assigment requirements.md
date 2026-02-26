# E-Commerce Pricing Automation - Home Test

## ⏱️ Time Limit: 3 Hours

## Overview
Build a Python service that monitors competitor pricing for eyewear products and suggests optimal pricing strategies.

### What Success Looks Like
- Working scraper for designeroptics.com
- Successfully scrapes as many products as possible from the test catalog
- Implements a simple pricing recommendation algorithm
- Generates a basic report with pricing suggestions
- Code runs locally with clear setup instructions
- Includes Dockerfile and requirements.txt
- Hourly progress emails sent

## Business Context
We sell eyewear products and need to stay competitive. This service will help us make data-driven pricing decisions by tracking competitor prices and suggesting adjustments to our pricing.

## Objectives
1. Scrape designeroptics.com for product pricing using search-based approach
2. Match competitor products to our catalog
3. Suggest new pricing based on competitor data
4. Provide basic reporting on pricing recommendations

## Requirements

### Core Features
1. **Web Scraping Service**
   - **Target website:** designeroptics.com
   - **Scraping approach:** Search-based (search by product name, e.g., "Burberry BE2108")
   - **Why designeroptics.com:** Works well with simple HTTP requests (no browser automation needed)
   - Extract product prices for products from the test catalog
   - Handle missing products gracefully (not all products may be found)

2. **Price Matching & Suggestion**
   - Match competitor products to our catalog using product names and brands
   - Implement a simple pricing algorithm (choose one):
     - Match the competitor price
     - Undercut the competitor by X%
     - Set price as average of our price and competitor price
   - Handle cases where competitor price is not found

3. **Reporting & Output**
   - Generate a report showing:
     - Products scraped successfully (with competitor prices found)
     - Products not found on competitor site
     - Current vs. suggested pricing
     - Price change recommendations
   - Export results in a structured format (CSV or JSON)

4. **Deployment Readiness**
   - Code must run locally, preferably on Docker.
   - Include requirements.txt with all dependencies
   - Include a Dockerfile (doesn't need to be fully working)
   - Document how to run locally and how you would containerize it
   - **BONUS**: If your scraper works in Docker, demonstrate it!

### Technical Constraints
- **Language**: Python
- **Data Storage**: JSON files or CSV
- **Deployment**: Must run locally, Dockerfile included (working in Docker is a bonus)

### Non-Functional Requirements
- Handle network failures and retries gracefully
- Implement rate limiting to avoid overwhelming competitor sites

## Deliverables

### 1. Working Code
- Complete, runnable implementation
- Clean, documented, production-quality code
- Unit tests for core logic (price calculation, matching, etc.)
- Configuration file for easy customization

### 2. Documentation
- **README.md**: Setup instructions, dependencies, how to run
- **DESIGN.md**: Architecture decisions, data flow, component design
- **API.md** (if applicable): API endpoints and usage
- Inline code comments where complexity warrants explanation

### 3. Design Document
Include in DESIGN.md:
- System architecture diagram
- Data flow (scraping → processing → storage → reporting)
- Technology choices and rationale
- Scalability considerations
- Trade-offs and limitations
- Future improvements

### 4. Deployment Guide
- Instructions to run locally

### 5. Progress Updates
**Required**: Send hourly email updates describing:
- What you've completed in the past hour
- What you're currently working on
- Any blockers or decisions you've made

## Product Catalog
Use the provided `test_products.csv` file containing:
- Eyewear products (curated test set)
- UPC codes for reference
- Current pricing (price and discounted price)
- Brand and product names for search-based matching

## Timeline Expectations
**Time Limit: 3 hours**

This is a timed assessment. You should:
- Track your time carefully
- Send hourly email updates
- Focus on getting core features working over perfection
- Make smart trade-offs given the time constraint


### Hints & Tips
- **Target site**: designeroptics.com uses simple HTTP requests (no browser automation needed)
- **Search strategy**: You may try search by product name 
- **Focus on working code**: Better to have fewer products working perfectly than many broken
- **Use AI tools**

## Submission
Please submit:
1. A Git repository (GitHub, GitLab, or zip file) containing:
   - All source code
   - README.md with setup instructions (how to run locally)
   - DESIGN.md with your architecture explanation
   - Dockerfile (best effort)
   - requirements.txt with all dependencies
2. Your 3 hourly progress update emails
3. A brief summary (2-3 paragraphs) explaining:
   - What pricing algorithm you implemented
   - Any trade-offs or limitations
   - What you would improve with more time
   - Challenges encountered and how you solved them

---

## Tools & Resources

### Allowed Tools
- **AI Coding Assistants**: Claude Code, Cursor, GitHub Copilot, or similar are mandatory. 
