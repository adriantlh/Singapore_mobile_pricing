import httpx
import re
from bs4 import BeautifulSoup
from typing import Any, Dict, List
from src.adapters.base_adapter import BaseAdapter
from src.models import ProductVariantInput

class RedWhiteMobileAdapter(BaseAdapter):
    """
    Adapter for RedWhiteMobile.com.
    Handles both New and Used phone pages.
    """

    async def scrape(self) -> str:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
                response = await client.get(self.base_url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"[{self.source_name}] Scrape error: {e}")
            return ""

    def parse(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        seen_urls = set()

        # Find all product containers
        containers = soup.find_all('div', class_=lambda x: x and 'product-small' in x)

        for container in containers:
            try:
                # 1. Extract Brand
                brand_elem = container.find(['span', 'p'], class_='category')
                brand = "Unknown"
                if brand_elem:
                    brand = brand_elem.get_text(strip=True)
                    # Strip prefixes like "New Oppo" -> "Oppo"
                    brand = re.sub(r'^(new|used|refurbished)\s+', '', brand, flags=re.IGNORECASE).strip()

                # 2. Extract Link and Model
                title_container = container.find(['p', 'div'], class_='name')
                if not title_container:
                    title_container = container.find(['p', 'div'], class_='product-title')
                
                model_elem = title_container.find('a') if title_container else None
                if not model_elem:
                    continue
                
                model = model_elem.get_text(strip=True)
                product_url = model_elem['href']

                # Deduplicate by URL
                if product_url in seen_urls:
                    continue
                seen_urls.add(product_url)

                # 3. Extract Price
                price_elem = container.find('span', class_='woocommerce-Price-amount')
                if not price_elem:
                    continue

                price_text = price_elem.get_text(strip=True)
                cleaned_price = re.sub(r'[^\d.]', '', price_text)
                if not cleaned_price:
                    continue
                price_val = float(cleaned_price)

                # 4. Extract Metadata (e.g., any promo)
                promo = ""
                badge = container.find('div', class_=lambda x: x and 'badge' in x.lower())
                if badge:
                    promo = badge.get_text(strip=True)

                products.append({
                    "brand": brand,
                    "model": model,
                    "url": product_url,
                    "price": price_val,
                    "currency": "SGD",
                    "promo": promo
                })
            except Exception as e:
                print(f"[{self.source_name}] Error parsing product: {e}")
                continue

        return products

    def validate(self, raw_data: Dict[str, Any]) -> ProductVariantInput:
        # Determine condition based on the source URL
        condition = "new" if "new-phones" in self.base_url else "used"

        brand_name = raw_data['brand']
        model_name = raw_data['model']
        
        attributes = {"condition": condition}

        # Simple parsing of model name to extract storage if present
        storage_match = re.search(r'(\d+\s?(GB|TB))', model_name, re.IGNORECASE)
        if storage_match:
            attributes["storage"] = storage_match.group(1)

        return ProductVariantInput(
            brand_name=brand_name,
            family_name=model_name,
            family_slug=model_name.lower().replace(" ", "-"),
            variant_name=model_name,
            attributes=attributes,
            source_name=self.source_name,
            source_url=self.base_url,
            price=raw_data['price'],
            currency=raw_data['currency'],
            url=raw_data['url'],
            metadata={"promo": raw_data['promo']}
        )
