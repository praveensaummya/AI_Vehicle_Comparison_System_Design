# app/utils/ad_stats.py
import re

def parse_price(price_str):
    # Extract numeric value from price string like "LKR 6,500,000"
    match = re.search(r'([\d,]+)', price_str.replace(',', ''))
    if match:
        return int(match.group(1).replace(',', ''))
    return None

def filter_and_stats(ads, min_price=None, max_price=None, year=None, location=None):
    filtered = []
    prices = []
    for ad in ads:
        price = parse_price(ad.get('price', ''))
        ad_year = ad.get('year', '')
        ad_location = ad.get('location', '').lower()
        if price is None:
            continue
        if min_price and price < min_price:
            continue
        if max_price and price > max_price:
            continue
        if year and str(year) != str(ad_year):
            continue
        if location and location.lower() not in ad_location:
            continue
        filtered.append(ad)
        prices.append(price)
    stats = {
        'count': len(prices),
        'min_price': min(prices) if prices else None,
        'max_price': max(prices) if prices else None,
        'avg_price': int(sum(prices) / len(prices)) if prices else None,
    }
    return {'ads': filtered, 'stats': stats}