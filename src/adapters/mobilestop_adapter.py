import httpx
import json
import re
from typing import Any, Dict, List, Optional
from src.adapters.base_adapter import BaseAdapter
from src.models import ProductVariantInput

class MobileStopAdapter(BaseAdapter):
    """
    Adapter for MobileStop (mobilestop.sg) using Shopify's products.json endpoint.
    """

    def __init__(self, source_name: str = "MobileStop", base_url: str = "https://mobilestop.sg"):
        super().__init__(source_name, base_url)
        self.json_url = f"{base_url.rstrip('/')}/products.json?limit=250"

    async def scrape(self) -> str:
        proxy = self.get_proxy()
        try:
            async with httpx.AsyncClient(follow_redirects=True, timeout=20.0, proxy=proxy) as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/json"
                }
                response = await client.get(self.json_url, headers=headers)
                response.raise_for_status()
                return response.text
        except Exception as e:
            print(f"[{self.source_name}] Scrape error: {e}")
            return ""

    def parse(self, content: str) -> List[Dict[str, Any]]:
        try:
            data = json.loads(content)
        except Exception as e:
            print(f"[{self.source_name}] JSON parse error: {e}")
            return []

        products = data.get("products", [])
        raw_items = []

        for p in products:
            vendor = p.get("vendor", "").strip()
            title = p.get("title", "").strip()
            handle = p.get("handle", "")
            product_type = p.get("product_type", "").lower()

            # Filter for Big 3 brands (Google, Apple, Samsung)
            brand = "Unknown"
            vendor_lower = vendor.lower()
            if "apple" in vendor_lower or "iphone" in title.lower():
                brand = "Apple"
            elif "samsung" in vendor_lower:
                brand = "Samsung"
            elif "google" in vendor_lower or "pixel" in title.lower():
                brand = "Google"
            
            # Skip if not the Big 3 or if it's clearly an accessory (unless we want accessories)
            # MobileStop has a lot of cases. We want phones.
            if brand == "Unknown":
                continue
            
            # Rough filter to exclude obvious non-phone items
            if any(x in title.lower() for x in ["case", "screen protector", "cable", "charger", "adapter", "strap", "band"]):
                continue

            # Extract Image URL from Shopify images array
            image_url = ""
            images = p.get("images", [])
            if images:
                image_url = images[0].get("src", "")

            for variant in p.get("variants", []):
                price = float(variant.get("price", 0))
                if price == 0:
                    continue

                variant_title = variant.get("title", "")
                full_name = f"{title} {variant_title}".strip()
                
                raw_items.append({
                    "brand": brand,
                    "model_title": title,
                    "variant_title": variant_title,
                    "full_name": full_name,
                    "price": price,
                    "url": f"{self.base_url}/products/{handle}",
                    "image_url": image_url,
                    "vendor": vendor,
                    "product_type": p.get("product_type"),
                    "options": variant.get("option1"), # Shopify often puts storage/color in option1, 2, 3
                    "option2": variant.get("option2"),
                    "option3": variant.get("option3"),
                    "sku": variant.get("sku"),
                    "available": variant.get("available")
                })

        return raw_items

    def validate(self, raw_data: Dict[str, Any]) -> ProductVariantInput:
        brand_name = raw_data['brand']
        full_name = raw_data['full_name']
        
        attributes = {
            "condition": "new", # Usually Shopify stores sell new items unless stated
            "vendor": raw_data['vendor'],
            "product_type": raw_data['product_type'],
            "sku": raw_data['sku'],
            "available": raw_data['available']
        }

        # Extract storage
        storage_match = re.search(r'(\d+\s?(GB|TB))', full_name, re.IGNORECASE)
        if storage_match:
            attributes["storage"] = storage_match.group(1).upper().replace(" ", "")
        
        # Extract color (best effort from options or title)
        # Often in Shopify, option1 is 'Color' or 'Size'
        if raw_data['options']:
            attributes["option1"] = raw_data['options']
        if raw_data['option2']:
            attributes["option2"] = raw_data['option2']
        if raw_data['option3']:
            attributes["option3"] = raw_data['option3']

        return ProductVariantInput(
            brand_name=brand_name,
            family_name=raw_data['model_title'],
            family_slug=re.sub(r'[^a-z0-9]+', '-', raw_data['model_title'].lower()).strip('-'),
            variant_name=raw_data['variant_title'] if raw_data['variant_title'] != "Default Title" else raw_data['model_title'],
            attributes=attributes,
            source_name=self.source_name,
            source_url=self.base_url,
            price=raw_data['price'],
            currency="SGD",
            url=raw_data['url'],
            image_url=raw_data.get('image_url'),
            metadata={}
        )
