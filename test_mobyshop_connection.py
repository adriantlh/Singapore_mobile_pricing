import httpx
import asyncio

async def test_mobyshop():
    url = "https://mobyshop.com.sg/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("Testing HTTP/1.1...")
    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
            resp = await client.get(url)
            print(f"HTTP/1.1 Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Success! Preview: {resp.text[:200]}")
            else:
                print(f"Failed with status: {resp.status_code}")
    except Exception as e:
        print(f"HTTP/1.1 Error: {e}")

    print("\nTesting HTTP/2...")
    try:
        async with httpx.AsyncClient(headers=headers, follow_redirects=True, http2=True) as client:
            resp = await client.get(url)
            print(f"HTTP/2 Status: {resp.status_code}")
            if resp.status_code == 200:
                print(f"Success! Preview: {resp.text[:200]}")
            else:
                print(f"Failed with status: {resp.status_code}")
    except Exception as e:
        print(f"HTTP/2 Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_mobyshop())
