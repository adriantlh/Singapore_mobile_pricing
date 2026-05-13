import os
from src.database import Database
from src.ingestor import Ingestor
from src.models import ProductVariantInput

# Mocking the environment for testing
# In a real scenario, you would set this in a .env file
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/postgres"

def test_ingestion():
    db = Database()
    ingestor = Ingestor(db)

    # Sample data representing a scraped item
    sample_data = ProductVariantInput(
        brand_name="Samsung",
        family_name="Galaxy S25",
        family_slug="samsung-galaxy-s25",
        variant_name="S25 256GB Black",
        attributes={
            "storage": "256GB",
            "color": "Black",
            "condition": "new"
        },
        source_name="Shopee SG",
        source_url="https://shopee.sg",
        price=1250.00,
        currency="SGD",
        url="https://shopee.sg/product/12345/67890",
        metadata={
            "promo": "Free Case",
            "voucher": "SG5OFF"
        }
    )

    try:
        print("Starting ingestion test...")
        ingestor.ingest(sample_data)
        print("Ingestion test completed successfully!")
    except Exception as e:
        print(f"Ingestion test failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_ingestion()
