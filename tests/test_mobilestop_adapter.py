import asyncio
import sys
import os

# Add the project root to the python path
sys.path.append(os.getcwd())

from src.adapters.mobilestop_adapter import MobileStopAdapter

async def main():
    adapter = MobileStopAdapter()
    products = await adapter.run()
    
    print(f"\nFound {len(products)} products.")
    for p in products[:10]:
        print(f"[{p.brand_name}] {p.variant_name} - {p.currency} {p.price}")
        print(f"  URL: {p.url}")
        print(f"  Attributes: {p.attributes}")

if __name__ == "__main__":
    asyncio.run(main())
