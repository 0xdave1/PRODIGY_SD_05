from flask import Flask, jsonify, send_file
import requests
from bs4 import BeautifulSoup
import pandas as pd
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def scrape_all_books():
    base_url = "https://books.toscrape.com/catalogue/category/books_1/"
    page = 1
    products = []

    while True:
        url = f"{base_url}page-{page}.html" if page > 1 else f"{base_url}index.html"
        response = requests.get(url)

        if response.status_code != 200:
            break

        soup = BeautifulSoup(response.text, "html.parser")
        books = soup.select(".product_pod")

        if not books:
            break

        for book in books:
            title = book.h3.a["title"]
            price = book.select_one(".price_color").text.strip()
            rating = book.p["class"][1]
            products.append({
                "title": title,
                "price": price,
                "rating": rating
            })

        page += 1

    return products

@app.route("/scrape", methods=["GET"])
def scrape_books():
    products = scrape_all_books()
    df = pd.DataFrame(products)
    df.to_csv("books.csv", index=False)
    return jsonify(products)

@app.route("/download", methods=["GET"])
def download_csv():
    return send_file("books.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
