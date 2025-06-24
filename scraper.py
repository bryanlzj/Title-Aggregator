import requests
from bs4 import BeautifulSoup
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://www.theverge.com/archives/{}/{}/{}"


def scrape_day(year, month, day):
    url = BASE_URL.format(year, month, day)
    print(f"Scraping {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        articles = []

        for a in soup.find_all("a", href=True, class_="_1lkmsmo1"):
            title = a.get_text(strip=True)
            href = a["href"]
            if title and href.startswith("/"):
                full_url = "https://www.theverge.com" + href
                articles.append((datetime(year, month, day), title, full_url))

        return articles
    except Exception as e:
        print(f"❌ Failed {url}: {e}")
        return []


def get_dates():
    dates = []
    start = datetime(2022, 1, 1)
    end = datetime(2025, 6, 1)
    while start <= end:
        dates.append((start.year, start.month, 1))  # scrape 1st of every month
        if start.month == 12:
            start = datetime(start.year + 1, 1, 1)
        else:
            start = datetime(start.year, start.month + 1, 1)
    return dates


def scrape_all():
    articles = []
    dates = get_dates()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(scrape_day, y, m, d) for (y, m, d) in dates]

        for future in as_completed(futures):
            result = future.result()
            if result:
                articles.extend(result)

    return sorted(articles, key=lambda x: x[0], reverse=True)
