import httpx
import asyncio
from bs4 import BeautifulSoup

async def inspect_product_structure(url):
    print(f"Inspecting structure of: {url}")
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. Find all elements containing '$'
            price_elements = soup.find_all(string=lambda text: "$" in text or "SGD" in text)
            print(f"Found {len(price_elements)} price-related text elements.")

            if not price_elements:
                print("No price elements found.")
                return

            # 2. For the first few price elements, find their parent container
            for i, price_text in enumerate(price_elements[:5]):
                # We need to find the element that actually contains this text
                # Since price_text is a NavigableString, we find its parent
                parent = price_text.parent

                # Traverse up to find a reasonable "product container"
                # We'll look for the nearest ancestor that has a 'product' or 'item' class
                container = parent
                for _ in range(10): # Traverse up 10 levels
                    if container.name == 'body':
                        break
                    if container.has_attr('class') and any(cls in container['class'] for cls in ['product', 'item', 'product-inner', 'product-type-simple']):
                        break
                    container = container.parent

                print(f"\n--- Product Container {i+1} ---")
                print(f"Container Tag: {container.name}")
                print(f"Container Classes: {container.get('class', 'None')}")

                # Print the inner HTML of this container (truncated)
                inner_html = "".join([str(c) for c in container.contents])
                print(f"Inner HTML Snippet: {inner_html[:500].strip()}...")

                # Try to find the title and price specifically within this container
                title_elem = container.find(['h1', 'h2', 'h3', 'h4', 'h5', 'a'], class_=lambda x: x and 'title' in x.lower())
                if title_elem:
                    print(f"  Found Title: {title_elem.get_text(strip=True)}")

                price_elem = container.find(string=lambda text: "$" in text or "SGD" in text)
                if price_elem:
                    print(f"  Found Price: {price_elem.strip()}")

    except Exception as e:
        print(f"Error: {e}")

async def main():
    url = "https://redwhitemobile.com/new-phones/"
    await inspect_product_structure(url)

if __name__ == "__main__":
    asyncio.run(main())
