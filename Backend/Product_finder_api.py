from flask import Flask, Blueprint, jsonify, request
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

# Create blueprints for each API
products_bp = Blueprint('products', __name__)
products_potaka_bp = Blueprint('products_potaka', __name__)
products_startech_bp = Blueprint('products_startech_bp', __name__)
products_finder_bp = Blueprint('products_finder_bp', __name__)

# Define routes for each API
@products_bp.route('/api/products', methods=['GET'])
def get_products():
    search_term = request.args.get('search_term', '')

    if not search_term:
        return jsonify({"error": "search_term parameter is required"}), 400

    base_url = "https://www.techlandbd.com/index.php?route=product/search&search="
    fq_param = "&sort=p.price&order=ASC&fq=1&limit=100"
    url = f"{base_url}{search_term}{fq_param}"

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve data from the source"}), 500

    soup = BeautifulSoup(response.content, "html.parser")
    product_thumbs = soup.find_all(class_="product-thumb")

    products = []

    for product_thumb in product_thumbs:
        name = product_thumb.find(class_="name").text.strip()

        try:
            price_text = product_thumb.find(class_="price-new").text.strip()
            price = int(price_text.split("৳")[0].replace(',', '').strip())  # Parse price as integer
        except AttributeError:
            continue
        except ValueError:
            continue

        img_src = product_thumb.find("img")["src"]
        link_value = product_thumb.find(class_="caption").find(class_="name").find("a")["href"]

        product = {
            "name": name,
            "price": price,
            "image_url": img_src,
            "price_value": price,  # Add another property 'price_value'
            "link_value": link_value
        }

        products.append(product)

    return jsonify(products)

@products_startech_bp.route('/api/products_startech_bp', methods=['GET'])
def get_products_startech():
    search_term = request.args.get('search_term', '')

    if not search_term:
        return jsonify({"error": "search_term parameter is required"}), 400

    base_url = "https://www.startech.com.bd/product/search?"
    search_query = search_term.replace(' ', '+')
    limit = 100
    url = f"{base_url}search={search_query}&limit={limit}"

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve data from the website"}), 500

    soup = BeautifulSoup(response.content, "html.parser")
    p_items = soup.find_all(class_="p-item")
    products = []

    for item in p_items:
        price = item.find(class_="p-item-price").find("span").get_text(strip=True)
        if any(char.isdigit() for char in price):
            # Strip non-numerical characters
            stripped_value = re.sub(r'[^\d]', '', price)
            price = int(stripped_value)
        else:
            # No numerical characters found
            break
        # try:
        #     print(price)
        #     price_value = int(price.split("৳")[1].replace(',', '').strip())
        # except (ValueError, IndexError):
        #     price_value = 0  # or any default value you prefer, like 0 or "Invalid"

        img_src = item.find(class_="p-item-img").find("img")["src"]
        name = item.find(class_="p-item-name").get_text(strip=True)
        link_value = item.find(class_="p-item-name").find("a")["href"]

        products.append({
            "price": f"{price}৳",
            "image_url": img_src,
            "name": name,
            "price_value": price, # Add the integer price for sorting
            "link_value": link_value
        })

    products_sorted = sorted(products, key=lambda x: x['price_value'])
    return jsonify(products_sorted)

@products_potaka_bp.route('/api/products-potaka', methods=['GET'])
def get_products_potaka():
    search_term = request.args.get('search_term', '')

    if not search_term:
        return jsonify({"error": "search_term parameter is required"}), 400

    base_url = "https://www.potakait.com/index.php?route=product/search&sort=p.price&order=ASC&search="
    encoded_search_term = urllib.parse.quote(search_term, safe='')
    url = base_url + encoded_search_term

    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({"error": "Failed to retrieve data from the website"}), 500

    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    product_items = soup.find_all(class_="product-layout")

    for item in product_items:
        name_element = item.find(class_="caption").find("a")
        name = name_element.text.strip() if name_element else "Name not available"

        img_src = item.find(class_="product-thumb").find(class_="image").find(class_="product-img").find("img")["src"]
        #img_src = img_element["data-src"] if img_element else "Image not available"

        price_new_element = item.find(class_="price-new")
        price_text = price_new_element.text.strip() if price_new_element else "Price not available"
        # Extract product link
        link_element = item.find("a", class_="product-img")
        link_value = link_element["href"] if link_element else "Link not available"


        try:
            price_value = int(price_text.split("৳")[0].replace(',', '').strip())
        except ValueError:
            price_value = "Price format unrecognized"

        product_data = {
            "name": name,
            "image_url": img_src,
            "price": price_value,
            "price_value": price_value,  # Add another property 'price_value'
            "link_value": link_value
        }

        products.append(product_data)

    return jsonify(products)





# Combine all blueprints into a single Flask app

products_finder_bp.register_blueprint(products_bp)
products_finder_bp.register_blueprint(products_startech_bp)
products_finder_bp.register_blueprint(products_potaka_bp)



# Define a route to merge and sort all products
@products_finder_bp.route('/api/merged-products', methods=['GET'])
def get_merged_products():
    search_term = request.args.get('search_term', '')

    all_products = []

    if search_term:
        urls = [
            f"http://127.0.0.1:5000/api/products?search_term={search_term}",
            f"http://127.0.0.1:5000/api/products-potaka?search_term={search_term}",
            f"http://127.0.0.1:5000/api/products_startech_bp?search_term={search_term}"

        ]

        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                all_products.extend(response.json())

    # Ensure all price values are integers and handle missing or invalid prices
    valid_products = []
    for product in all_products:
        price_value = product.get('price_value', 'N/A')
        try:
            product['price_value'] = int(price_value)
            valid_products.append(product)
        except (ValueError, TypeError):
            # Skip product if price_value is not a valid integer
            print(f"Invalid price value: {price_value} for product: {product}")

    sorted_products = sorted(valid_products, key=lambda x: x['price_value'])
    return jsonify(sorted_products)
