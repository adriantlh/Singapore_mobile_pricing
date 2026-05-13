import asyncio
import re
from src.adapters.redwhite_adapter import RedWhiteMobileAdapter

async def main():
    # Using the URLs that were confirmed to work with curl
    urls = [
        ("RedWhite New Phones", "https://redwhitemobile.com/new-phones/"),
        ("RedWhite Used Phones", "https://redwhitemobile.com/used-phones-singapore/")
    ]

    brands_to_find = ["Samsung", "Apple", "Google"]
    found_products = []

    print("Starting data retrieval for Samsung, Apple, and Google...")

    for label, url in urls:
        print(f"Scraping {label}...")
        adapter = RedWhiteMobileAdapter(source_name=label, base_url=url)
        try:
            products = await adapter.run()
            print(f"  Found {len(products)} total products in {label}")

            for p in products:
                # Debug: print a few product names to see what we are working with
                # print(f"    Checking: {p.family_name}")

                # Check if any of our target brands are in the product name
                if any(brand.lower() in p.family_name.lower() for brand in brands_to_find):
                    # Identify which brand matched
                    matched_brand = next(brand for brand in brands_to_find if brand.lower() in p.family_name.lower())
                    found_products.append({
                        "brand": matched_brand,
                        "name": p.family_name,
                        "price": p.price,
                        "currency": p.currency,
                        "condition": "new" if "new-phones" in url else "used",
                        "url": p.url
                    })
        except Exception as e:
            print(f"Error scraping {label}: {e}")

    if not found_products:
        print("No products found for the specified brands.")
        return

    # Sort by brand and then name
    found_products.sort(key=lambda x: (x['brand'], x['name']))

    print(f"\n{'BRAND':<10} | {'CONDITION':<6} | {'PRICE':<10} | {'PRODUCT NAME'}")
    print("-" * 80)
    for p in found_products:
        price_str = f"{p['price']:.2f} {p['currency']}"
        print(f"{p['brand']:<10} | {p['condition']:<6} | {price_str:<10} | {p['name']}")

if __name__ == "__main__":
    asyncio.run(main())
