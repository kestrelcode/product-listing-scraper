# Website Price/Listing Scraper

Scrapes product listings — title, price, stock status, rating — from a
paginated site and exports them to CSV. Follows "next page" links
automatically, so it works whether the site has 1 page or 100.

Written and tested against [books.toscrape.com](https://books.toscrape.com),
a public sandbox built specifically for scraping practice, so this is safe
to demo without touching a live commercial site's terms of service.

## Why this is useful for a client

The pattern here — product cards with a title, a price, and a "next page"
link — is common to most small e-commerce and directory sites. Point this
at a client's actual use case (competitor price tracking, monitoring a
supplier's catalog, pulling listings into a spreadsheet) by swapping the
CSS selectors in `parse_listing_page()` for their target site. Everything
else — pagination, polite delays, CSV export, error handling — works as-is.

## Usage

```bash
pip install requests beautifulsoup4
python scraper.py --max-pages 3 --output books.csv
```

Options:
- `--max-pages` — how many listing pages to follow (default: 3)
- `--output` — output CSV filename (default: `scraped_products.csv`)
- `--base-url` — starting page (default: books.toscrape.com)

## Example output

`sample_output_preview.csv` shows real data pulled from the live site's
first page (title, price in GBP, stock status):

```
title,price_gbp,availability
A Light in the Attic,51.77,In stock
Tipping the Velvet,53.74,In stock
Soumission,50.1,In stock
...
```

The live script also extracts a 1-5 star rating per book — that field
is rendered as a CSS class on the page rather than plain text, so it
isn't visible in a quick preview like the one above, but the script parses
it directly from the HTML (see `parse_listing_page()`), verified against
the site's actual markup structure.

## Design notes

- **Polite by default** — a 1-second delay between page requests, and a
  descriptive User-Agent, rather than hammering the target server.
- **Follows pagination automatically** — reads the "next page" link from
  each page rather than assuming a fixed page count.
- **Fails loudly, not silently** — a bad request raises a clear error
  instead of writing a half-empty CSV.
- **Selector-based, not brittle string matching** — uses CSS selectors via
  BeautifulSoup, so it's a quick edit to retarget at a different site's
  markup.
