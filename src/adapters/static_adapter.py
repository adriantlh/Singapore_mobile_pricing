import httpx
from bs4 import BeautifulSoup
from typing import Any, Dict, List
from src.adapters.base_adapter import BaseAdapter
from src.models import ProductVariantInput

class StaticAdapter(BaseAdapter):
    """
    An adapter for simple, static HTML websites.
    Uses HTTPX for fetching and BeautifulSoup for parsing.
    """

    async def scrape(self) -> str:
        # For testing purposes, if the URL is 'mock://test', return hardcoded HTML
        if self.base_url == "mock://test":
            return """
            <html>
                <body>
                    <div class="product">
                        <h1 class="title">Samsung Galaxy S25</h1>
                        <span class="price">1200.00</span>
                        <span class="currency">SGD</span>
                        <div class="specs">
                            <span class="storage">256GB</span>
                            <span class="color">Black</span>
                        </div>
                        <div class="promo">Free Case</div>
                    </div>
                </body>
            </html>
            """

        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(self.base_url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"[{self.source_name}] Scrape error: {e}")
            return ""

    def parse(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []

        # This logic is specific to our 'mock' structure
        for product_div in soup.find_all('div', class_='product'):
            data = {
                "name": product_div.find('h1', class_='title').get_text(),
                "price": float(product_div.find('span', class_='price').get_text()),
                "currency": product_div.find('span', class_='currency').get_text(),
                "url": self.base_url,
                "storage": product_div.find('span', class_='storage').get_text(),
                "color": product_div.find('span', class_='color').get_text(),
                "promo": product_div.find('div', class_='promo').get_text() if product_div.find('div', class_='promo') else None
            }
            products.append(data)
        return products

    def validate(self, raw_data: Dict[str, Any]) -> ProductVariantInput:
        # Map the raw scraped data to our standardized model
        return ProductVariantInput(
            brand_name="Samsung", # In a real scenario, this would be parsed or looked up
            family_name="Galaxy S25",
            family_slug="samsung-galaxy-s25",
            variant_name=raw_data['name'] + " " + raw_data['storage'] + " " + raw_data['color'],
            attributes={
                "storage": raw_data['storage'],
                "color": raw_data['color'],
                "condition": "new"
            },
            source_name=self.source_name,
            source_url=self.base_url,
            price=raw_data['price'],
            currency=raw_data['currency'],
            url=raw_data['url'],
            metadata={
                "promo": raw_data['promo']
            }
        )
