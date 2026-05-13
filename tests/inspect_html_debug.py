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

            # The previous error might have been related to how I was finding containers
            # Let's try a broader search first
            containers = soup.find_all('div', class_=lambda x: x and 'product-small' in x)
            print(f"Found {len(containers)} containers with class 'product-small'")

            if not containers:
                print("No containers found with 'product-small' in class. Searching for all divs...")
                all_divs = soup.find_all('div')
                print(f"Found {len(all_divs)} total divs.")
                # Let's look at the classes of the first 10 divs
                for i, div in enumerate(all_divs[:10]):
                    print(f"Div {i} class: {div.get('class')}")

            for i, container in enumerate(containers[:3]):
                print(f"\n--- Container {i} ---")
                # Print the container's HTML snippet
                print(container.prettify())

                # Specifically look for the <a> tag and its text
                link_elem = container.find('a')
                if link_elem:
                    print(f"  Found <a> tag. Text: '{link_elem.get_text(strip=True)}'")
                    print(f"  Href: '{link_elem.get('href')}'")
                else:
                    print("  No <a> tag found in this container.")

    except Exception as e:
        print(f"Error during debugging: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(debug_html())
