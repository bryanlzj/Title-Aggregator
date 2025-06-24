import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time
import re
from urllib.parse import urlparse

CACHE_FILE = 'cached_articles.json'


def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [(datetime.fromisoformat(d[0]), d[1], d[2]) for d in data]
        except Exception as e:
            print(f"❌ Failed to load cache: {e}")
    return []


def save_cache(articles):
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump([(d[0].isoformat(), d[1], d[2])
                      for d in articles], f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Failed to save cache: {e}")


def normalize_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"


def fetch_articles_for_month(year, month):
    url = f"https://www.theverge.com/archives/{year}/{month:02d}/1"
    print(f"Scraping {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    articles = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        title = a_tag.get_text(strip=True)

        if re.match(r"^/\d{4}/\d{1,2}/\d{1,2}/", href):
            try:
                parts = href.strip("/").split("/")
                pub_date = datetime(
                    int(parts[0]), int(parts[1]), int(parts[2]))
                full_url = f"https://www.theverge.com{href}"
            except (IndexError, ValueError):
                continue

            if title and pub_date >= datetime(2022, 1, 1):
                articles.append((pub_date, title, full_url))

    print(f"✅ {len(articles)} articles found for {year}-{month:02d}")
    return articles


def scrape_the_verge():
    cached = load_cache()
    if cached:
        print("✅ Loaded articles from cache.")
        return sorted(cached, reverse=True)

    articles = []
    seen = set()
    years = [2022, 2023, 2024, 2025]
    months = range(1, 13)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(fetch_articles_for_month, year, month)
            for year in years for month in months
        ]

        for future in futures:
            try:
                month_articles = future.result()
                for pub_date, title, url in month_articles:
                    clean_url = normalize_url(url)
                    if clean_url not in seen:
                        seen.add(clean_url)
                        articles.append((pub_date, title, url))
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Error processing future: {e}")

    save_cache(articles)
    print("💾 Articles saved to cache.")
    return sorted(articles, reverse=True)
