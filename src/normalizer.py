import re
import json
import html
from typing import Dict, Optional, Tuple, List
from rapidfuzz import process, fuzz
from src.database import Database

class Normalizer:
    RELEASE_DATES = {
        # Apple
        "Iphone 17": "2025-09-20", "Iphone 16": "2024-09-20", "Iphone 15": "2023-09-22",
        "Iphone 14": "2022-09-16", "Iphone 13": "2021-09-24", "Iphone 12": "2020-10-23",
        "Iphone 11": "2019-09-20", "Iphone SE": "2022-03-18",
        "Watch Series 11": "2025-09-20", "Watch Series 10": "2024-09-20", "Watch Series 9": "2023-09-22",
        "Watch Ultra 2": "2023-09-22", "Watch Ultra": "2022-09-23",
        "Airpods 4": "2024-09-20", "Airpods Pro 2": "2022-09-23", "Airpods Pro": "2019-10-30",
        # Samsung
        "S26": "2026-01-30", "S25": "2025-01-30", "S24": "2024-01-30", "S23": "2023-02-17",
        "Z Fold 7": "2025-08-11", "Z Flip 7": "2025-08-11",
        "Z Fold 6": "2024-07-24", "Z Flip 6": "2024-07-24",
        "Z Fold 5": "2023-08-11", "Z Flip 5": "2023-08-11",
        # Google
        "Pixel 10": "2025-08-13", "Pixel 9": "2024-08-13", "Pixel 8": "2023-10-12", "Pixel 7": "2022-10-13"
    }

    def __init__(self, db: Database):
        self.db = db
        self.brands = {} # name -> id
        self.families = [] # list of (id, name, brand_id, category, released_at)
        self.brand_names = []
        self._load_cache()

    def _load_cache(self):
        target_brands = ["Google", "Apple", "Samsung"]
        brand_rows = self.db.execute("SELECT id, name FROM brands WHERE name IN %s;", (tuple(target_brands),), fetch=True)
        for row in brand_rows:
            self.brands[row['name'].lower()] = row['id']
            self.brand_names.append(row['name'])

        family_rows = self.db.execute("""
            SELECT pf.id, pf.name, pf.brand_id, pf.category, pf.released_at 
            FROM product_families pf
            JOIN brands b ON pf.brand_id = b.id
            WHERE b.name IN %s;
        """, (tuple(target_brands),), fetch=True)
        for row in family_rows:
            self.families.append({
                "id": row['id'], "name": row['name'], "brand_id": row['brand_id'],
                "category": row['category'], "released_at": row['released_at']
            })

    def normalize_brand(self, raw_brand: str) -> str:
        clean_brand = re.sub(r'^(new|used|refurbished)\s+', '', raw_brand, flags=re.IGNORECASE).strip()
        clean_brand = re.sub(r'\s+(accessories|supported|iphones|android|phones|devices)$', '', clean_brand, flags=re.IGNORECASE).strip()
        
        mapping = {"5g supported iphones": "Apple", "5g supported": "Apple", "apple accessories": "Apple", "google pixel": "Google", "samsung galaxy": "Samsung"}
        if clean_brand.lower() in mapping: clean_brand = mapping[clean_brand.lower()]

        if clean_brand.lower() in self.brands:
            for name in self.brand_names:
                if name.lower() == clean_brand.lower(): return name

        match = process.extractOne(clean_brand, self.brand_names, scorer=fuzz.token_set_ratio)
        if match and match[1] > 90: return match[0]
        return "Unknown"

    def normalize(self, raw_title: str) -> Dict:
        # 0. Pre-clean
        raw_title = re.sub(r'^(new|used|refurbished)\s+', '', raw_title, flags=re.IGNORECASE).strip()
        
        # 1. Identify Brand
        detected_brand_id = None
        brand_canonical_name = None
        clean_title = raw_title.lower()
        
        sorted_brand_names = sorted(self.brands.keys(), key=len, reverse=True)
        for b_name in sorted_brand_names:
            if re.search(rf'(?i)\b{re.escape(b_name)}\b', clean_title):
                detected_brand_id = self.brands[b_name]
                brand_canonical_name = [n for n in self.brand_names if n.lower() == b_name.lower()][0]
                clean_title = re.sub(rf'(?i)\b{re.escape(b_name)}\b', '', clean_title).strip()
                break
        
        if not detected_brand_id:
            return {"brand_id": None, "family_id": None, "family_name": None, "confidence": 0, "is_new": False, "attributes": {"raw_title": raw_title}}
        
        # 2. Extract Attributes
        storage = self._extract_storage(raw_title)
        ram = self._extract_ram(raw_title)
        color = self._extract_color(raw_title)
        
        nuance = None
        if "noise cancellation" in raw_title.lower() or "anc" in raw_title.lower():
            nuance = "With Active Noise Cancellation"
            clean_title = re.sub(r'(?i)\b(active|noise|cancellation|anc)\b', '', clean_title).strip()

        # Clean title of technical junk
        if storage: clean_title = re.sub(rf'(?i)\b{re.escape(storage)}\b', '', clean_title).strip()
        if ram: clean_title = re.sub(rf'(?i)\b{re.escape(ram)}(gb|g)?\b', '', clean_title).strip()
        clean_title = re.sub(r'\b\d+/\d+\b', '', clean_title).strip()
        clean_title = re.sub(r'\s+[\d/]+$', '', clean_title).strip()
            
        if color:
            color_pattern = re.escape(color).replace(r'\ ', r'\s+')
            clean_title = re.sub(rf'(?i)\b{color_pattern}\b', '', clean_title).strip()
        
        keywords = ["used", "refurbished", "new", "5g", "4g", "lte", "wifi", "cellular", "gps", "singapore", "export", "telco", "set", "activated", "with", "and", "remote", "mic", "gb", "tb", "ram"]
        for word in keywords:
            clean_title = re.sub(rf'(?i)\b{re.escape(word)}\b', '', clean_title).strip()
        
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        clean_title = re.sub(r'^[^\w\(]+|[^\w\)]+$', '', clean_title).strip()

        # 3. Match Family
        search_space = [f for f in self.families if f["brand_id"] == detected_brand_id]
        family_names = [f["name"] for f in search_space]
        best_match = None
        highest_score = 0
        raw_nums = set(re.findall(r'\b\d+\b', raw_title))

        for f in search_space:
            f_name = f["name"].lower()
            f_nums = set(re.findall(r'\b\d+\b', f["name"]))
            if raw_nums - f_nums: continue
            if f_name in raw_title.lower():
                score = fuzz.token_sort_ratio(f_name, clean_title) + 50
                if score > highest_score:
                    highest_score = score
                    best_match = f

        if highest_score < 90:
            match = process.extractOne(clean_title, family_names, scorer=fuzz.token_set_ratio)
            if match:
                matched_f = search_space[match[2]]
                matched_nums = set(re.findall(r'\b\d+\b', matched_f["name"]))
                if not (raw_nums - matched_nums) and match[1] > highest_score:
                    highest_score = match[1]
                    best_match = matched_f

        # 4. Fallback
        is_new = highest_score < 80
        suggested_name = clean_title.title()
        noise = ["Deep", "Space", "Natural", "Blue", "Silver", "Gold", "Gray", "Grey", "Black", "White", "Titanium", "Cosmic", "Orange", "Desert", "Singapore", "Product", "Red", "Pink", "Yellow", "Purple", "Lavender", "Mist", "Sage", "Soft", "Cloud", "Light", "Sky"]
        for _ in range(2):
            for word in noise:
                suggested_name = re.sub(rf'(?i)\s+{word}$', '', suggested_name).strip()
                suggested_name = re.sub(rf'(?i)^{word}\s+', '', suggested_name).strip()
        
        # Check for hardcoded release date if it's new
        inferred_release_date = None
        if is_new:
            for model_key, date in self.RELEASE_DATES.items():
                if model_key.lower() in raw_title.lower():
                    inferred_release_date = date
                    break

        # Model Number Logic
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

        suggested_name = re.sub(r'\s+', ' ', suggested_name).strip()
        if nuance and nuance.lower() not in suggested_name.lower():
            suggested_name = f"{suggested_name} {nuance}"
        
        final_suggested_name = f"{brand_canonical_name} {suggested_name}"
        final_suggested_name = re.sub(rf'(?i)\b{brand_canonical_name}\b\s+\b{brand_canonical_name}\b', brand_canonical_name, final_suggested_name)

        inferred_category = "phone"
        title_lower = raw_title.lower()
        acc_kw = ["case", "protector", "charger", "cable", "adapter", "adaptor", "earpods", "airpods", "airtag", "pencil", "loop", "ring", "wallet", "connector", "plug", "power bank", "magsafe", "buds"]
        if any(x in title_lower for x in acc_kw): inferred_category = "accessory"
        elif any(x in title_lower for x in ["watch", "gear", "fit", "ultra"]):
            if "watch" in title_lower: inferred_category = "watch"
        elif any(x in title_lower for x in ["tab", "pad", "surface", "folio"]): inferred_category = "tablet"

        return {
            "brand_id": detected_brand_id,
            "family_id": best_match["id"] if best_match and not is_new else None,
            "family_name": best_match["name"] if best_match and not is_new else final_suggested_name,
            "suggested_family_name": final_suggested_name,
            "category": best_match["category"] if best_match and not is_new else inferred_category,
            "released_at": best_match["released_at"] if best_match and not is_new else inferred_release_date,
            "confidence": highest_score, "is_new": is_new,
            "attributes": {"storage": storage, "ram": ram, "color": color, "nuance": nuance, "raw_title": raw_title}
        }

    def _extract_storage(self, text: str) -> Optional[str]:
        match = re.search(r'(\d+\s?(GB|TB))', text, re.IGNORECASE)
        return match.group(1).upper() if match else None

    def _extract_ram(self, text: str) -> Optional[str]:
        match = re.search(r'\b(\d+)\s?(GB|G)?(?=\s?/|/|\s|$)', text, re.IGNORECASE)
        if match:
            val = match.group(1)
            if val in ["2", "3", "4", "6", "8", "12", "16", "18", "24", "32"]:
                return val.upper() + (match.group(2).upper() if match.group(2) else "")
        return None

    def _extract_color(self, text: str) -> Optional[str]:
        colors = ["Black", "White", "Silver", "Gold", "Gray", "Grey", "Space-Black", "Space-Grey", "Titanium", "Natural", "Blue", "Deep-Blue", "Sierra-Blue", "Green", "Alpine-Green", "Red", "Pink", "Yellow", "Purple", "Deep-Purple", "Orange", "Cosmic-Orange", "Midnight", "Starlight", "Graphite", "Space-Black", "Space-Gray", "Space-Grey", "Natural Titanium", "Blue Titanium", "White Titanium", "Black Titanium", "Desert Titanium", "Teal", "Berry", "Ultramarine"]
        for c in colors:
            if re.search(rf'(?i)\b{re.escape(c)}\b', text): return c.replace("-", " ").title()
        return None
