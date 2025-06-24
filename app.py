from flask import Flask, render_template
from scraper import scrape_the_verge

app = Flask(__name__)
cached_articles = []


@app.route("/")
def index():
    global cached_articles
    if not cached_articles:
        # This uses multithreaded scraping internally
        cached_articles = scrape_the_verge()
    return render_template("index.html", articles=cached_articles)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
