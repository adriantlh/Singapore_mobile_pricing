import httpx
import re
import json
import html
import asyncio
from bs4 import BeautifulSoup
from typing import Any, Dict, List
from src.adapters.base_adapter import BaseAdapter
from src.models import ProductVariantInput

class MisterMobileAdapter(BaseAdapter):
    """
    Adapter for MisterMobile.com.sg.
    Handles sub-page variation scraping to capture all storage/condition variants.
    """

    async def scrape(self) -> str:
        all_variations = []
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
            # 1. Collect all product links from all pages
            product_links = []
            seen_product_urls = set()
            current_url = self.base_url
            
            # If the URL is already a single product, just scrape it
            if "/product/" in self.base_url:
                product_links = [self.base_url]
            else:
                page_count = 0
                while current_url and page_count < 10: # Limit to 10 pages for sanity
                    print(f"[{self.source_name}] Fetching listing: {current_url}")
                    resp = await client.get(current_url)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    
                    items = soup.find_all('div', class_='mm-product-item')
                    for item in items:
                        a = item.find('a', class_='mm-product-link')
                        if a and a.get('href'):
                            p_url = a['href']
                            if p_url not in seen_product_urls:
                                product_links.append(p_url)
                                seen_product_urls.add(p_url)
                    
                    # Find next page
                    next_link = soup.find('link', rel='next')
                    if next_link and next_link.get('href') and next_link['href'] != current_url:
                        current_url = next_link['href']
                        page_count += 1
                    else:
                        current_url = None

            # 2. Fetch each product page and extract variations
            print(f"[{self.source_name}] Found {len(product_links)} products. Fetching details...")
            
            # Use semi-concurrency to avoid overwhelming the site (batch size of 5)
            batch_size = 5
            for i in range(0, len(product_links), batch_size):
                batch = product_links[i:i + batch_size]
                tasks = [self._fetch_product_variations(client, url) for url in batch]
                results = await asyncio.gather(*tasks)
                for res in results:
                    if res:
                        all_variations.extend(res)
                
                print(f"[{self.source_name}] Collected {len(all_variations)} variations so far...")

        return json.dumps(all_variations)

    async def _fetch_product_variations(self, client, url):
        try:
            resp = await client.get(url)
            # Find variation JSON blob in the HTML
            match = re.search(r'data-product_variations="([^"]+)"', resp.text)
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            title_elem = soup.find('h1', class_='product_title')
            base_title = title_elem.get_text(strip=True) if title_elem else "Unknown"
            
            # Extract brand from breadcrumbs
            brand = "Unknown"
            breadcrumb = soup.find('nav', class_='woocommerce-breadcrumb')
            if breadcrumb:
                links = breadcrumb.find_all('a')
                # Often the last link before the current page is the Brand/Category
                if len(links) >= 2:
                    brand = links[-1].get_text(strip=True)

            # Extract Image URL
            image_url = ""
            gallery = soup.find('div', class_='woocommerce-product-gallery')
            if gallery:
                img = gallery.find('img')
                if img:
                    image_url = img.get('src', '')

            variations_data = []
            if match:
                # Decode JSON from the data attribute
                v_json = html.unescape(match.group(1))
                vars = json.loads(v_json)
                for v in vars:
                    # Some variations might be out of stock but listed
                    # We only care about those with a valid price
                    if v.get('display_price'):
                        variations_data.append({
                            "base_title": base_title,
                            "brand": brand,
                            "url": url,
                            "image_url": image_url,
                            "price": float(v['display_price']),
                            "attributes": v['attributes'],
                            "variation_id": v['variation_id'],
                            "is_in_stock": v.get('is_in_stock', True)
                        })
            else:
                # Handle simple products with no variations
                price_elem = soup.find('p', class_='price')
                if price_elem:
                    # Pick the last price if it's a range or sale
                    price_text = price_elem.get_text(strip=True)
                    # Extract last numerical value (handle $100 - $200 format)
                    prices = re.findall(r'[\d,.]+', price_text.replace(',', ''))
                    if prices:
                        variations_data.append({
                            "base_title": base_title,
                            "brand": brand,
                            "url": url,
                            "image_url": image_url,
                            "price": float(prices[-1]),
                            "attributes": {},
                            "variation_id": None,
                            "is_in_stock": True
                        })
            return variations_data
        except Exception as e:
            print(f"[{self.source_name}] Error fetching variations from {url}: {e}")
            return None

    def parse(self, html_content: str) -> List[Dict[str, Any]]:
        # Our scrape() already returns a JSON list of variations
        return json.loads(html_content)

    def validate(self, raw_data: Dict[str, Any]) -> ProductVariantInput:
        attrs = raw_data['attributes']
        
        # Normalize condition
        # attribute_pa_condition values: 'mint', 'pristine', 'satisfactory'
        cond_attr = attrs.get('attribute_pa_condition', '').lower()
        condition = "new"
        if any(c in cond_attr for c in ['mint', 'pristine', 'satisfactory', 'used']):
            condition = "used"
        
        # Override condition if source URL suggests it
        if 'used-phone' in self.base_url:
            condition = "used"

        storage = attrs.get('attribute_pa_storage', None)
        color = attrs.get('attribute_pa_color', None)

        # Build descriptive variant name
        variant_name = raw_data['base_title']
        if storage: variant_name += f" {storage.upper()}"
        if color: variant_name += f" {color.title()}"

        return ProductVariantInput(
            brand_name=raw_data['brand'],
            family_name=raw_data['base_title'],
            family_slug=raw_data['base_title'].lower().replace(" ", "-"),
            variant_name=variant_name,
            attributes={
                "storage": storage.upper() if storage else None,
                "color": color.title() if color else None,
                "condition": condition,
                "variation_id": raw_data['variation_id']
            },
            source_name=self.source_name,
            source_url=self.base_url,
            price=raw_data['price'],
            currency="SGD",
            url=raw_data['url'],
            image_url=raw_data.get('image_url'),
            metadata={"is_in_stock": raw_data['is_in_stock']}
        )
