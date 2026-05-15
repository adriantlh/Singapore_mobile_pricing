from playwright.async_api import async_playwright
import asyncio

async def test_mobyshop_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        print("Navigating to MobyShop...")
        try:
            await page.goto("https://mobyshop.com.sg/", wait_until="networkidle", timeout=60000)
            title = await page.title()
            print(f"Page Title: {title}")
            
            content = await page.content()
            print(f"Content Length: {len(content)}")
            if "Cloudflare" in title or "Just a moment" in title:
                print("Still blocked by Cloudflare (Wait for challenge?)")
                # Wait a bit longer or try to interact
                await asyncio.sleep(10)
                content = await page.content()
                title = await page.title()
                print(f"New Title: {title}")
            else:
                print("Successfully bypassed Cloudflare!")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_mobyshop_playwright())
