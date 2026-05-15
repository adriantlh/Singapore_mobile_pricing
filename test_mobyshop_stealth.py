from playwright.async_api import async_playwright
from playwright_stealth import stealth
import asyncio

async def test_mobyshop_stealth():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth(page)
        
        print("Navigating to MobyShop with stealth...")
        try:
            await page.goto("https://mobyshop.com.sg/apple", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5) # Wait for potential challenges
            
            title = await page.title()
            print(f"Page Title: {title}")
            
            if "Just a moment" in title:
                print("Still blocked. Waiting 15s...")
                await asyncio.sleep(15)
                title = await page.title()
                print(f"New Title: {title}")

            content = await page.content()
            if "Just a moment" not in title and len(content) > 5000:
                print("Successfully bypassed Cloudflare!")
                print(f"Content Preview: {content[:500]}")
                # Save content for analysis
                with open("mobyshop_apple.html", "w") as f:
                    f.write(content)
            else:
                print("Failed to bypass.")
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(test_mobyshop_stealth())
