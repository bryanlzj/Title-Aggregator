import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time


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

    for a_tag in soup.find_all("a", class_="_1lkmsmo1", href=True):
        title = a_tag.get_text(strip=True)
        href = a_tag["href"]
        full_url = f"https://www.theverge.com{href}" if href.startswith(
            "/") else href

        # Extract date from URL
        try:
            parts = href.split("/")
            pub_date = datetime(int(parts[1]), int(parts[2]), int(parts[3]))
        except (IndexError, ValueError):
            continue

        if pub_date >= datetime(2022, 1, 1):
            articles.append((pub_date, title, full_url))

    return articles[:1]  # Only get one article per month


def scrape_the_verge():
    articles = []
    seen = set()
    years = [2022, 2023, 2024, 2025]
    months = list(range(1, 13))

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for year in years:
            for month in months:
                futures.append(executor.submit(
                    fetch_articles_for_month, year, month))

        for future in futures:
            month_articles = future.result()
            for article in month_articles:
                if article[2] not in seen:
                    seen.add(article[2])
                    articles.append(article)
            time.sleep(0.1)  # Add small delay to avoid hitting site too hard

    return sorted(articles, reverse=True)
