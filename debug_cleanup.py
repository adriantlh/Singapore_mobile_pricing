import re
from rapidfuzz import process, fuzz
from typing import Dict, Optional

class MockNormalizer:
    def __init__(self):
        self.brands = {"samsung": "1", "apple": "2", "google": "3"}
        self.brand_names = ["Samsung", "Apple", "Google"]
    
    def _extract_storage(self, text: str):
        match = re.search(r'(\d+\s?(GB|TB))', text, re.IGNORECASE)
        return match.group(1).upper() if match else None

    def _extract_ram(self, text: str):
        match = re.search(r'\b(\d+)\s?(GB|G)?(?=\s?/|/|\s|$)', text, re.IGNORECASE)
        if match:
            val = match.group(1)
            if val in ["2", "3", "4", "6", "8", "12", "16", "18", "24", "32"]:
                return val.upper() + (match.group(2).upper() if match.group(2) else "")
        return None

    def normalize(self, raw_title: str):
        raw_title = re.sub(r'^(new|used|refurbished)\s+', '', raw_title, flags=re.IGNORECASE).strip()
        clean_title = raw_title.lower()
        
        detected_brand_id = None
        brand_canonical_name = "Unknown"
        for brand_name in self.brands:
            if re.search(rf'(?i)\b{re.escape(brand_name)}\b', clean_title):
                detected_brand_id = self.brands[brand_name]
                brand_canonical_name = brand_name.title()
                clean_title = re.sub(rf'(?i)\b{re.escape(brand_name)}\b', '', clean_title).strip()
                break
        
        storage = self._extract_storage(raw_title)
        ram = self._extract_ram(raw_title)
        
        if storage: clean_title = re.sub(rf'(?i)\b{re.escape(storage)}\b', '', clean_title).strip()
        if ram: clean_title = re.sub(rf'(?i)\b{re.escape(ram)}(gb|g)?\b', '', clean_title).strip()
        
        # AGGRESSIVE spec stripping
        clean_title = re.sub(r'\b\d+/\d+\b', '', clean_title).strip()
        clean_title = re.sub(r'(?i)\([^)]*(gb|tb|ram|\d|/)[^)]*\)', '', clean_title).strip()
        clean_title = re.sub(r'\(\s*\)', '', clean_title).strip()
        
        keywords = ["used", "refurbished", "new", "5g", "4g", "lte", "wifi", "cellular", "gps", "singapore", "export", "telco", "set", "activated", "with", "and", "remote", "mic", "gb", "tb", "ram", "galaxy", "pixel", "iphone", "ipad", "watch", "airpods"]
        for word in keywords:
            clean_title = re.sub(rf'(?i)\b{re.escape(word)}\b', '', clean_title).strip()
        
        clean_title = re.sub(r'[\d/\s\(\)-]+$', '', clean_title).strip()
        print(f"DEBUG clean_title after keywords: '{clean_title}'")

        suggested_name = clean_title.title()
        
        # Model Number Logic (Simplified)
        model_num = None
        if "apple" in brand_canonical_name.lower():
            m = re.search(r'(?i)(iphone|watch|ipad|airpods)\s*(1[0-7]|[2-9]|se|pro|air)\b', raw_title)
            if m: model_num = m.group(1).title() + " " + m.group(2).upper()
        elif "samsung" in brand_canonical_name.lower():
            m = re.search(r'(?i)\b(s2[0-6]|z\s?(fold|flip)\s?[1-7]|tab\s?s[1-9]|a\d{2})\b', raw_title)
            if m: model_num = m.group(1).upper()
        
        if model_num:
            cat_words = ["Iphone", "Watch", "Ipad", "Airpods", "Fold", "Flip", "Tab"]
            merged = False
            for cat in cat_words:
                if cat.lower() in suggested_name.lower() and cat.lower() in model_num.lower():
                    mods = [m for m in ["Plus", "Max", "Pro", "Fe", "Ultra", "Mini"] if m.lower() in suggested_name.lower() and m.lower() not in model_num.lower()]
                    suggested_name = model_num
                    if mods: suggested_name += " " + " ".join(mods)
                    merged = True
                    break
            if not merged and model_num.lower() not in suggested_name.lower():
                suggested_name = f"{suggested_name} {model_num}"

        final_suggested_name = f"{brand_canonical_name} {suggested_name}"
        final_suggested_name = re.sub(rf'(?i)\b{brand_canonical_name}\b\s+\b{brand_canonical_name}\b', brand_canonical_name, final_suggested_name)
        
        return final_suggested_name.strip()

norm = MockNormalizer()
print(f"Result 1: '{norm.normalize('Samsung Galaxy S26 Ultra (12/256GB)')}'")
print(f"Result 2: '{norm.normalize('Samsung Galaxy S26 Ultra (12/)')}'")
