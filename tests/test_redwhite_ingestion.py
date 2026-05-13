import asyncio
import os
import sys

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adapters.redwhite_adapter import RedWhiteMobileAdapter
from src.ingestor import Ingestor
from src.database import Database

async def test_redwhite_ingestion():
    print("Starting RedWhiteMobile ingestion test...")

    # Initialize DB and Ingestor
    try:
        db = Database()
        ingestor = Ingestor(db)
    except Exception as e:
        print(f"Failed to initialize Database or Ingestor: {e}")
        return

    # Define the target URLs
    urls = [
        ("RedWhite New Phones", "https://redwhitemobile.com/new-phones/"),
        ("RedWhite Used Phones", "https://redwhitemobile.com/used-phones-singapore/")
    ]

    for source_label, url in urls:
        print(f"\n--- Testing {source_label} ---")
        print(f"URL: {url}")

        # Create adapter
        # Note: RedWhiteMobileAdapter uses the URL to determine condition
        adapter = RedWhiteMobileAdapter(source_name=source_label, base_url=url)

        try:
            # Run the scraper pipeline (scrape -> parse -> validate)
            products = await adapter.run()

            if not products:
                print(f"No products found for {source_label}.")
                continue

            print(f"Found {len(products)} valid products. Starting ingestion...")

            # Ingest each product
            success_count = 0
            for product in products:
                try:
                    ingestor.ingest(product)
                    success_count += 1
                except Exception as e:
                    print(f"Error ingesting product {product.variant_name}: {e}")

            print(f"Ingestion complete for {source_label}. Successfully ingested {success_count}/{len(products)} products.")

        except Exception as e:
            print(f"Error during scraping/parsing for {source_label}: {e}")

    print("\nRedWhiteMobile ingestion test finished.")

if __name__ == "__main__":
    asyncio.run(test_redwhite_ingestion())
