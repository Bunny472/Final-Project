import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, Blueprint
from flask_cors import CORS

pc_builder_bp = Blueprint('pc_builder_bp', __name__)




def fetch_components(urls):
    components = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        p_items = soup.find_all(class_="p-item")

        for item in p_items:
            try:
                name = item.find(class_="p-item-name").get_text(strip=True)
                price_str = item.find(class_="p-item-price").get_text(strip=True)
                price = float(price_str.replace("৳", "").replace(",", "").strip())
                img_tag = item.find(class_="p-item-img").find("img")
                img_src = img_tag["src"] if img_tag else "No image available"

                components.append({
                    "name": name,
                    "price": price,
                    "img_src": img_src
                })
            except AttributeError:
                continue

    return components

def allocate_budget(budget):
    if budget > 100000:
        allocations = {
            "processor": 0.18,
            "motherboard": 0.12,
            "ram": 0.10,
            "psu": 0.08,
            "gpu": 0.40,
            "storage": 0.07,
            "casing": 0.05
        }
    else:
        allocations = {
            "processor": 0.20,
            "motherboard": 0.15,
            "ram": 0.10,
            "psu": 0.12,
            "gpu": 0.34,
            "storage": 0.08,
            "casing": 0.06
        }

    allocated_budget = {k: v * budget for k, v in allocations.items()}
    return allocated_budget

def build_pc(budget, urls_dict):
    allocated_budget = allocate_budget(budget)
    selected_components = {}
    total_spent = 0

    for component, urls in urls_dict.items():
        if component == "monitor":
            continue

        components = fetch_components(urls)
        components.sort(key=lambda x: x['price'], reverse=True)

        for c in components:
            if c['price'] <= allocated_budget[component]:
                selected_components[component] = c
                total_spent += c['price']
                break
        else:
            selected_components[component] = None

    remaining_budget = budget - total_spent

    if remaining_budget > 0 and "monitor" in urls_dict:
        monitor_components = fetch_components(urls_dict["monitor"])
        monitor_components.sort(key=lambda x: x['price'], reverse=True)

        for m in monitor_components:
            if m['price'] <= remaining_budget:
                selected_components["monitor"] = m
                total_spent += m['price']
                remaining_budget -= m['price']
                break
        else:
            selected_components["monitor"] = None

    return selected_components, total_spent, remaining_budget


@pc_builder_bp.route('/api/pc-build', methods=['GET'])
def pc_build_api():
    budget = request.args.get('budget', type=float)

    if not budget:
        return jsonify({"error": "Please provide a valid budget as a query parameter."}), 400

    urls_dict = {
        "processor": [
            "https://www.startech.com.bd/component/processor?filter_status=7&sort=p.price&order=DESC&limit=90",
            "https://www.startech.com.bd/component/processor?filter_status=7&sort=p.price&order=ASC&limit=90"
        ],
        "motherboard": [
            "https://www.startech.com.bd/component/motherboard?filter_status=7&sort=p.price&order=DESC&limit=90",
            "https://www.startech.com.bd/component/motherboard?filter_status=7&sort=p.price&order=ASC&limit=90"
        ],
        "gpu": [
            "https://www.startech.com.bd/component/graphics-card?filter_status=7&sort=p.price&order=DESC&limit=90",
            "https://www.startech.com.bd/component/graphics-card?filter_status=7&sort=p.price&order=ASC&limit=90"
        ],
        "ram": [
            "https://www.startech.com.bd/component/ram?filter_status=7&sort=p.price&order=DESC&limit=90",
            "https://www.startech.com.bd/component/ram?filter_status=7&sort=p.price&order=ASC&limit=90"
        ],
        "psu": [
            "https://www.startech.com.bd/component/power-supply?filter_status=7&sort=p.price&order=DESC&limit=90",
            "https://www.startech.com.bd/component/power-supply?filter_status=7&sort=p.price&order=ASC&limit=90"
        ],
        "storage": [
            "https://www.startech.com.bd/component/SSD-Hard-Disk?filter_status=7&sort=p.price&order=DESC&limit=90",
            "https://www.startech.com.bd/component/SSD-Hard-Disk?filter_status=7&sort=p.price&order=ASC&limit=90"
        ],
        "casing": [
            "https://www.startech.com.bd/component/casing?filter_status=7&sort=p.price&order=DESC&limit=90",
            "https://www.startech.com.bd/component/casing?filter_status=7&sort=p.price&order=ASC&limit=90"
        ],
        "monitor": [
            "https://www.startech.com.bd/monitor?filter_status=7&sort=p.price&order=DESC&limit=90",
            "https://www.startech.com.bd/monitor?filter_status=7&sort=p.price&order=ASC&limit=90"
        ]
    }

    pc_build, total_spent, remaining_budget = build_pc(budget, urls_dict)

    response = {
        "budget": budget,
        "pc_build": pc_build,
        "total_spent": total_spent,
        "remaining_budget": remaining_budget
    }

    return jsonify(response)

# if __name__ == "__main__":
#     app.run(debug=True)