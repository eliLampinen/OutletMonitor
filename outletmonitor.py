import requests
import json
from datetime import datetime
from configFile import API_BASE_URL, BASE_SINGLE

def fetch_items(base_url, page_no=0, page_size=100):
    """Fetch items from the API."""
    url = f"{base_url}&pageNo={page_no}&pageSize={page_size}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])

        items = []
        for product in products:
            # Extract relevant data
            name = product.get("name")
            brand = product.get("brand", {}).get("name")
            price_with_tax = product.get("customerReturnsInfo", {}).get("price_with_tax")
            original_price = product.get("price", {}).get("original")
            rating = product.get("rating", {}).get("averageOverallRating")
            item_id = product.get("customerReturnsInfo", {}).get("id")
            discount_percentage = None

            # Calculate discount percentage
            if original_price and price_with_tax:
                discount_percentage = round(((original_price - price_with_tax) / original_price) * 100, 2)

            items.append({
                "name": name,
                "brand": brand,
                "price_with_tax": price_with_tax,
                "original_price": original_price,
                "discount_percentage": discount_percentage,
                "rating": rating,
                "url": f"{BASE_SINGLE}{item_id}"
            })
        return items

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return []

def compare_and_save_items():
    """Compare new items with previous ones and save results."""
    # Fetch new items
    new_items = []
    for page_no in range(3): # 300 items is good enough, after that the discount precentage drops to under 60%
        new_items.extend(fetch_items(API_BASE_URL, page_no=page_no, page_size=100)) # 100 is max page_size

    # Load previous items if exists
    try:
        with open("items.json", "r") as f:
            old_items = json.load(f)
    except FileNotFoundError:
        old_items = []

    # Find new items
    old_urls = {item['url'] for item in old_items}
    new_entries = [item for item in new_items if item['url'] not in old_urls]

    # Save new entries to a dated file
    if new_entries:
        date_str = datetime.now().strftime("%Y-%m-%d")
        with open(f"{date_str}_new_items.json", "w") as f:
            json.dump(new_entries, f, indent=2, ensure_ascii=False)

    # Overwrite the items.json file with current items
    with open("items.json", "w") as f:
        json.dump(new_items, f, indent=2, ensure_ascii=False)

# Execute the comparison and save
if __name__ == "__main__":
    compare_and_save_items()
