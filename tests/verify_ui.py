import asyncio
from playwright.async_api import async_playwright

async def run_ui_test():
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1280, 'height': 800})
        page = await context.new_page()

        print("--- Navigating to http://localhost:80 ---")
        try:
            await page.goto("http://localhost:80", timeout=30000)
            await page.wait_for_load_state("networkidle")
        except Exception as e:
            print(f"Failed to load page: {e}")
            await browser.close()
            return

        # 1. Check Header Title
        title = await page.inner_text("h1")
        print(f"Page Title Found: {title}")

        # 2. Check for Theme Toggle Button
        # We added a label "Theme" and icons Moon/Sun
        theme_btn = await page.query_selector("button:has-text('Theme')")
        if not theme_btn:
            # Fallback check for the button without text (if screen is narrow)
            theme_btn = await page.query_selector("header button svg")
        
        if theme_btn:
            print("✅ Theme toggle button FOUND.")
            
            # Check current theme on HTML tag
            initial_theme = await page.get_attribute("html", "data-theme")
            print(f"Initial theme: {initial_theme or 'dark (default)'}")

            # Click the button
            print("Clicking theme toggle...")
            await theme_btn.click()
            await page.wait_for_timeout(500) # Wait for transition

            new_theme = await page.get_attribute("html", "data-theme")
            print(f"Theme after click: {new_theme}")

            if new_theme != initial_theme:
                print("✅ Theme switch SUCCESSFUL.")
            else:
                print("❌ Theme attribute did not change.")
        else:
            print("❌ Theme toggle button NOT FOUND.")
            # Print all buttons in header for debugging
            buttons = await page.query_selector_all("header button")
            print(f"Found {len(buttons)} buttons in header.")
            for i, btn in enumerate(buttons):
                text = await btn.inner_text()
                print(f"  - Button {i}: '{text.strip()}'")

        # 3. Check for Category Filters
        categories = ["All", "Phone", "Watch", "Tablet", "Accessory"]
        for cat in categories:
            cat_btn = await page.query_selector(f"button:has-text('{cat}')")
            if cat_btn:
                print(f"✅ Category button '{cat}' FOUND.")
            else:
                print(f"❌ Category button '{cat}' NOT FOUND.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_ui_test())
