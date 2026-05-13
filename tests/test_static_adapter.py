import asyncio
import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.adapters.static_adapter import StaticAdapter

async def test_static_adapter():
    # Test with the mock URL
    adapter = StaticAdapter(source_name="MockStore", base_url="mock://test")

    print("Testing StaticAdapter with mock data...")
    products = await adapter.run()

    if not products:
        print("❌ Test Failed: No products found.")
        return

    product = products[0]
    print(f"✅ Test Passed! Found product: {product.variant_name}")
    print(f"   Price: {product.price} {product.currency}")
    print(f"   Attributes: {product.attributes}")
    print(f"   Metadata: {product.metadata}")

if __name__ == "__main__":
    asyncio.run(test_static_adapter())
