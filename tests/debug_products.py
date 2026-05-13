import asyncio
from src.adapters.redwhite_adapter import RedWhiteMobileAdapter

async def main():
    url = "https://redwhitemobile.com/new-phones/"
    adapter = RedWhiteMobileAdapter(source_name="test", base_url=url)
    products = await adapter.run()
    print(f"Found {len(products)} products")
    for p in products[:10]:
        print(f"- {p.family_name} ({p.price} {p.currency})")

if __name__ == "__main__":
    asyncio.run(main())
