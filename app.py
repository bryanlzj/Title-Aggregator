from flask import Flask, render_template
from scraper import scrape_the_verge

app = Flask(__name__)


@app.route("/")
def index():
    articles = scrape_the_verge()
    return render_template("index.html", articles=articles)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
