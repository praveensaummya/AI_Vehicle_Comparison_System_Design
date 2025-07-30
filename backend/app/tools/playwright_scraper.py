# app/tools/playwright_scraper.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def extract_ad_details(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=60000)
            # TODO: Adjust selectors for each site as needed!
            title = page.text_content('h1, .ad-title, .title') or "Not Found"
            price = page.text_content('.price, .ad-price, [data-testid=\"ad-price\"]') or "Not Found"
            location = page.text_content('.location, .ad-location') or "Not Found"
            mileage = page.text_content('.mileage, .ad-mileage') or "Not Found"
            year = page.text_content('.year, .ad-year') or "Not Found"
        except PlaywrightTimeoutError:
            title = price = location = mileage = year = "Not Found"
        except Exception as e:
            title = price = location = mileage = year = f"Error: {e}"
        finally:
            browser.close()
        return {
            "title": title.strip() if title else "Not Found",
            "price": price.strip() if price else "Not Found",
            "location": location.strip() if location else "Not Found",
            "mileage": mileage.strip() if mileage else "Not Found",
            "year": year.strip() if year else "Not Found",
            "link": url
        }

def batch_extract_ad_details(urls: list) -> list:
    results = []
    for url in urls:
        results.append(extract_ad_details(url))
    return results