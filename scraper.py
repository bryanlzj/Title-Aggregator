import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time
import re


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
    return articles[:1]


def scrape_the_verge():
    articles = []
    seen = set()
    years = [2022, 2023, 2024, 2025]
    months = range(1, 13)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for year in years:
            for month in months:
                futures.append(executor.submit(
                    fetch_articles_for_month, year, month))

        for future in futures:
            try:
                month_articles = future.result()
                for article in month_articles:
                    if article[2] not in seen:
                        seen.add(article[2])
                        articles.append(article)
                time.sleep(0.1)  # slight delay to avoid rate limiting
            except Exception as e:
                print(f"❌ Error processing future: {e}")

    return sorted(articles, reverse=True)
