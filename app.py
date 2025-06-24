import os

from flask import Flask, render_template
from scraper import scrape_all  # import the new function

app = Flask(__name__)


@app.route("/")
def index():
    articles = scrape_all()  # use the multithreaded function
    return render_template("index.html", articles=articles)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
