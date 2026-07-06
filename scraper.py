"""
Website Price Scraper
----------------------
Scrapes product listings (title, price, availability, rating) from a
paginated e-commerce-style site and saves the results to a CSV.

Written against https://books.toscrape.com — a public sandbox site built
specifically for scraping practice — so it's safe to demo and share
without touching a live commercial site's terms of service.

The structure (product cards with a title link, a price tag, and a
"next page" link) is the same pattern used by most small e-commerce
sites, so this adapts easily to a real client target: swap the CSS
selectors in `parse_listing_page()` for the client's site and the rest
of the script — pagination, CSV export, delay/retry logic — works as-is.

Usage:
    python scraper.py
    python scraper.py --max-pages 5 --output books.csv
"""

import argparse
import csv
import time
import sys
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
HEADERS = {"User-Agent": "Mozilla/5.0 (portfolio-project scraper; contact: you@example.com)"}


def parse_listing_page(html, page_url):
    """Parse one listing page's HTML and return a list of product dicts."""
    soup = BeautifulSoup(html, "html.parser")
    products = []

    for card in soup.select("article.product_pod"):
        title_tag = card.select_one("h3 a")
        title = title_tag["title"] if title_tag else None

        price_tag = card.select_one("p.price_color")
        price_text = price_tag.get_text(strip=True) if price_tag else ""
        # strip currency symbol, keep the number (e.g. "£51.77" -> 51.77)
        price = "".join(ch for ch in price_text if ch.isdigit() or ch == ".")
        price = float(price) if price else None

        availability_tag = card.select_one("p.instock.availability")
        availability = availability_tag.get_text(strip=True) if availability_tag else None

        rating_tag = card.select_one("p.star-rating")
        rating_word = next(
            (cls for cls in (rating_tag.get("class", []) if rating_tag else []) if cls in RATING_WORDS),
            None,
        )
        rating = RATING_WORDS.get(rating_word)

        products.append({
            "title": title,
            "price_gbp": price,
            "availability": availability,
            "rating_out_of_5": rating,
            "source_page": page_url,
        })

    # find the "next page" link, if any
    next_link = soup.select_one("li.next a")
    next_url = None
    if next_link and next_link.get("href"):
        next_url = requests.compat.urljoin(page_url, next_link["href"])

    return products, next_url


def scrape(base_url=BASE_URL, max_pages=3, delay_seconds=1.0):
    """Follow pagination from base_url, scraping up to max_pages pages."""
    all_products = []
    url = base_url
    page_count = 0

    while url and page_count < max_pages:
        print(f"Fetching page {page_count + 1}: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        products, next_url = parse_listing_page(response.text, url)
        all_products.extend(products)
        print(f"  -> found {len(products)} products")

        url = next_url
        page_count += 1
        if url and page_count < max_pages:
            time.sleep(delay_seconds)  # be polite — don't hammer the server

    return all_products


def save_to_csv(products, output_path):
    if not products:
        print("No products to save.")
        return
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)
    print(f"Saved {len(products)} products to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Scrape product listings to CSV.")
    parser.add_argument("--max-pages", type=int, default=3, help="Number of listing pages to scrape")
    parser.add_argument("--output", default="scraped_products.csv", help="Output CSV path")
    parser.add_argument("--base-url", default=BASE_URL, help="Starting listing page URL")
    args = parser.parse_args()

    try:
        products = scrape(base_url=args.base_url, max_pages=args.max_pages)
    except requests.RequestException as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)

    save_to_csv(products, args.output)


if __name__ == "__main__":
    main()
