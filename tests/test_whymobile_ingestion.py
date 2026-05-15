import asyncio
import os
import sys
import json

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adapters.whymobile_adapter import WhyMobileAdapter
from src.ingestor import Ingestor
from src.database import Database
from src.normalizer import Normalizer

async def test_whymobile_ingestion():
    print("Starting WhyMobile ingestion test...")

    # Initialize DB, Ingestor, and Normalizer
    try:
        db = Database()
        ingestor = Ingestor(db)
        normalizer = Normalizer(db)
    except Exception as e:
        print(f"Failed to initialize Database, Ingestor, or Normalizer: {e}")
        # If DB fails, we can still test the adapter and normalizer logic
        db = None
        ingestor = None
        print("Continuing without database for local testing...")

    # Define the target URLs
    urls = [
        ("WhyMobile Apple", "https://www.whymobile.com/products?brand=APL"),
        ("WhyMobile Samsung", "https://www.whymobile.com/products?brand=SAM"),
        ("WhyMobile Google", "https://www.whymobile.com/products?brand=GOOG"),
        ("WhyMobile Used", "https://www.whymobile.com/products?type=USE")
    ]

    all_found_products = []

    for source_label, url in urls:
        print(f"\n--- Testing {source_label} ---")
        print(f"URL: {url}")

        adapter = WhyMobileAdapter(source_name=source_label, base_url=url)

        try:
            products = await adapter.run()

            if not products:
                print(f"No products found for {source_label}.")
                continue

            print(f"Found {len(products)} valid products.")
            
            for product in products[:5]: # Show first 5
                print(f"\nRaw Product: {product.variant_name} - S${product.price}")
                
                # Test normalization
                norm = normalizer.normalize(product.variant_name)
                print(f"Normalized Family: {norm['family_name']} ({norm['confidence']}%)")
                print(f"Normalized Category: {norm['category']}")
                print(f"Attributes: {norm['attributes']}")
                
                all_found_products.append({
                    "source": source_label,
                    "name": product.variant_name,
                    "price": product.price,
                    "normalized_family": norm['family_name'],
                    "category": norm['category']
                })

            if ingestor and db:
                print(f"\nStarting ingestion for {len(products)} products...")
                success_count = 0
                for product in products:
                    try:
                        ingestor.ingest(product)
                        success_count += 1
                    except Exception as e:
                        # print(f"Error ingesting product {product.variant_name}: {e}")
                        pass
                print(f"Ingested {success_count}/{len(products)} products.")

        except Exception as e:
            print(f"Error during scraping/parsing for {source_label}: {e}")

    print("\nWhyMobile ingestion test finished.")
    
    # Summary of products
    print(f"\nSummary of first few products found:")
    for p in all_found_products[:20]:
        print(f"[{p['source']}] {p['name']} -> {p['normalized_family']} (S${p['price']})")

    if db:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_whymobile_ingestion())
