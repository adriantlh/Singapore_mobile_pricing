import httpx
import re
from bs4 import BeautifulSoup
from typing import Any, Dict, List
from src.adapters.base_adapter import BaseAdapter
from src.models import ProductVariantInput

class WhyMobileAdapter(BaseAdapter):
    """
    Adapter for WhyMobile.com.
    """

    async def scrape(self) -> str:
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = await client.get(self.base_url, headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"[{self.source_name}] Scrape error: {e}")
            return ""

    def parse(self, html_content: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []
        seen_urls = set()

        # Product cards are in div.uk-card.uk-card-default
        containers = soup.find_all('div', class_=lambda x: x and 'uk-card' in x and 'uk-card-default' in x)

        for container in containers:
            try:
                # 1. Model Name
                model_elem = container.find('h3', class_=lambda x: x and 'uk-h4' in x)
                if not model_elem:
                    continue
                model = model_elem.get_text(strip=True)

                # 2. Category and Condition
                card_body = container.find('div', class_='uk-card-body')
                if not card_body:
                    continue
                
                muted_texts = card_body.find_all('div', class_=lambda x: x and 'uk-text-muted' in x)
                category = "Unknown"
                condition = "new"
                if len(muted_texts) >= 1:
                    category = muted_texts[0].get_text(strip=True)
                if len(muted_texts) >= 2:
                    condition_text = muted_texts[1].get_text(strip=True).lower()
                    if 'used' in condition_text or 'refurbished' in condition_text:
                        condition = 'used'
                    else:
                        condition = 'new'

                # 3. URL
                link_elem = container.find('a', class_='wm-modal')
                product_url = ""
                if link_elem and 'href' in link_elem.attrs:
                    product_url = "https://www.whymobile.com" + link_elem['href']
                
                if not product_url or product_url in seen_urls:
                    continue
                seen_urls.add(product_url)

                # 4. Price
                price_elem = container.find('div', class_=lambda x: x and 'uk-text-bold' in x)
                if not price_elem:
                    continue
                
                price_text = price_elem.get_text(strip=True)
                if "Call" in price_text:
                    price_val = 0.0
                else:
                    cleaned_price = re.sub(r'[^\d.]', '', price_text)
                    price_val = float(cleaned_price) if cleaned_price else 0.0

                if price_val == 0.0:
                    continue 

                # 5. Promo/Warranty
                footer = container.find('div', class_='uk-card-footer')
                promo = ""
                if footer:
                    promo_elem = footer.find('p')
                    if promo_elem:
                        promo = promo_elem.get_text(strip=True)

                products.append({
                    "brand": "Unknown", 
                    "model": model,
                    "url": product_url,
                    "price": price_val,
                    "currency": "SGD",
                    "condition": condition,
                    "category": category,
                    "promo": promo
                })
            except Exception:
                continue

        return products

    def validate(self, raw_data: Dict[str, Any]) -> ProductVariantInput:
        model_name = raw_data['model']
        brand_name = "Unknown"
        upper_model = model_name.upper()
        if "APPLE" in upper_model or "IPHONE" in upper_model: brand_name = "Apple"
        elif "SAMSUNG" in upper_model or "GALAXY" in upper_model: brand_name = "Samsung"
        elif "GOOGLE" in upper_model or "PIXEL" in upper_model: brand_name = "Google"
        
        if brand_name == "Unknown":
            if "Apple" in self.source_name: brand_name = "Apple"
            elif "Samsung" in self.source_name: brand_name = "Samsung"
            elif "Google" in self.source_name: brand_name = "Google"

        attributes = {"condition": raw_data['condition'], "original_category": raw_data['category']}
        storage_match = re.search(r'(\d+\s?(GB|TB))', model_name, re.IGNORECASE)
        if storage_match:
            attributes["storage"] = storage_match.group(1).upper().replace(" ", "")

        return ProductVariantInput(
            brand_name=brand_name,
            family_name=model_name,
            family_slug=re.sub(r'[^a-z0-9]+', '-', model_name.lower()).strip('-'),
            variant_name=model_name,
            attributes=attributes,
            source_name=self.source_name,
            source_url="https://www.whymobile.com",
            price=raw_data['price'],
            currency="SGD",
            url=raw_data['url'],
            metadata={"promo": raw_data['promo']}
        )
