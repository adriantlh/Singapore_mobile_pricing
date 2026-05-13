import httpx
from bs4 import BeautifulSoup
import asyncio

async def debug_html():
    url = "https://redwhitemobile.com/new-phones/"
    print(f"Fetching: {url}")
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            containers = soup.find_all('div', class_=lambda x: x and 'product-small' in x)
            print(f"Found {len(containers)} containers with class 'product-small'")

            for i, container in enumerate(containers[:5]):
                print(f"\n--- Container {i} ---")

                # 1. Check for Name
                name_p = container.find('p', class_=lambda x: x and 'product-title' in x)
                if name_p:
                    link_elem = name_p.find('a')
                    if link_elem:
                        print(f"  [Name] Found: '{link_elem.get_text(strip=True)}'")
                        print(f"  [Name] Link: '{link_elem.get('href')}'")
                    else:
                        print("  [Name] Found <p> but no <a> inside.")
                else:
                    print("  [Name] No <p class='product-title'> found.")

                # 2. Check for Price
                # Let's look for anything that looks like a price
                price_elem = container.find(class_=lambda x: x and 'price' in x.lower())
                if price_elem:
                    print(f"  [Price] Found element with 'price' in class: {price_elem.get('class')}")
                    print(f"  [Price] Text: '{price_elem.get_text(strip=True)}'")
                else:
                    print("  [Price] No element with 'price' in class found.")

                # 3. Check for any text in the container that looks like a price (e.g., contains $)
                # This is a fallback
                all_text = container.get_text(separator=' ', strip=True)
                import re
                prices = re_findall(r'[\$\d,.]+', all_text)
                if prices:
                    print(f"  [Price Fallback] Found potential prices in text: {prices}")

    except Exception as e:
        print(f"Error during debugging: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(debug_html())
