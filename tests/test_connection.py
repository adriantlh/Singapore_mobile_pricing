import httpx
import asyncio

async def test_connection():
    url = "https://redwhitemobile.com/new-phones/"
    print(f"Testing connection to: {url}")
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(url)
            print(f"Status Code: {response.status_code}")
            print(f"Content length: {len(response.text)}")
            print(f"First 100 chars: {response.text[:100]}")
    except Exception as e:
        print(f"Connection error: {repr(e)}")

if __name__ == "__main__":
    asyncio.run(test_connection())
