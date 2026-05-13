import httpx
import asyncio
from bs4 import BeautifulSoup

async def explore_site(url):
    print(f"Exploring: {url}")
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            print(f"Status Code: {response.status_code}")

            soup = BeautifulSoup(response.text, 'html.parser')

            # Let's look for elements that might be products.
            # Common patterns: class="product", class="item", class="price"
            products_found = 0

            # Search for common price patterns in the text
            # We'll look for elements containing "$" or "SGD"
            price_elements = soup.find_all(string=lambda text: "$" in text or "SGD" in text)
            print(	f"Found {len(price_elements)} elements containing '$' or 'SGD'")

            # Let's look for common product container classes
            # We'll print the first 5 product-like elements found
            potential_containers = soup.find_all(['div', 'li', 'article'], class_=lambda x: x and ('product' in x.lower() or 'item' in x.lower()))
            print(f"Found {len(potential_containers)} potential product containers.")

            for i, container in enumerate(potential_containers[:5]):
                print(f"\n--- Container {i+1} snippet ---")
                print(container.get_text(strip=True)[:300])

    except Exception as e:
        print(f"Error exploring {url}: {e}")

async def main():
    urls = [
        "https://redwhitemobile.com/new-phones/",
        "httpshttps://redwhitemobile.com/used-phones-singapore/"
    ]
    # Note: I noticed a typo in the URL above (httpshttps). Fixing it.
    urls = [
        "https://redwhitemobile.com/new-phones/",
        "https://redwhitemobile.com/used-phones-singapore/"
    ]
    for url in urls:
        await explore_site(url)
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())
