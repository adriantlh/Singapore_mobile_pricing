import re
from rapidfuzz import process, fuzz
from typing import Dict, Optional

class MockNormalizer:
    def __init__(self):
        self.brands = {"samsung": "1", "apple": "2"}
    
    def _extract_storage(self, text: str):
        match = re.search(r'(\d+\s?(GB|TB))', text, re.IGNORECASE)
        return match.group(1).upper() if match else None

    def _extract_ram(self, text: str):
        match = re.search(r'(\d+)\s?(GB|G)?(?=\s?/|/|\s|$)', text, re.IGNORECASE)
        if match:
            val = match.group(1)
            if val in ["2", "3", "4", "6", "8", "12", "16", "18", "24", "32"]:
                return val.upper() + (match.group(2).upper() if match.group(2) else "")
        return None

    def normalize(self, raw_title: str):
        raw_title = re.sub(r'^(new|used|refurbished)\s+', '', raw_title, flags=re.IGNORECASE).strip()
        detected_brand_id = None
        clean_title = raw_title.lower()
        for brand_name in self.brands:
            if re.search(rf'(?i)\b{re.escape(brand_name)}\b', clean_title):
                detected_brand_id = self.brands[brand_name]
                clean_title = re.sub(rf'(?i)\b{re.escape(brand_name)}\b', '', clean_title).strip()
                break
        
        storage = self._extract_storage(raw_title)
        ram = self._extract_ram(raw_title)
        if storage: clean_title = clean_title.replace(storage.lower(), "").strip()
        if ram:
            clean_title = clean_title.replace(ram.lower(), "").strip()
            clean_title = re.sub(r'\b\d+/\b', '', clean_title).strip()
        
        keywords = ["used", "refurbished", "new", "5g", "4g", "lte", "wifi", "cellular", "gps", "gb", "tb", "ram"]
        for word in keywords:
            clean_title = re.sub(rf'(?i)\b{re.escape(word)}\b', '', clean_title).strip()
        
        clean_title = re.sub(r'\s+\d+$', '', clean_title).strip()
        clean_title = re.sub(r'\s+', ' ', clean_title).strip()
        clean_title = re.sub(r'^[^\w\(]+|[^\w\)]+$', '', clean_title).strip()

        suggested_name = clean_title.title()
        noise = ["Deep", "Space", "Natural", "Blue", "Silver", "Gold", "Gray", "Grey", "Black", "White", "Titanium", "Cosmic", "Orange", "Desert", "Singapore"]
        for _ in range(2):
            for word in noise:
                suggested_name = re.sub(rf'\s+{word}$', '', suggested_name, flags=re.IGNORECASE).strip()
                suggested_name = re.sub(rf'^{word}\s+', '', suggested_name, flags=re.IGNORECASE).strip()
        
        # AGGRESSIVE RAM STRIP
        ram_vals = ["4", "6", "8", "12", "16", "18", "24", "32"]
        for rv in ram_vals:
            pattern = rf'\s+{rv}(/|\s?G)?$'
            if re.search(pattern, suggested_name, re.IGNORECASE):
                all_nums = re.findall(r'\d+', suggested_name)
                if len(all_nums) > 1:
                    suggested_name = re.sub(pattern, '', suggested_name, flags=re.IGNORECASE).strip()
                    break

        raw_no_5g = re.sub(r'(?i)\b5g\b', '', raw_title)
        model_num_match = re.search(r'\b(1[0-7]|[2-9]|SE|S\d+|Z\d+|Fold\d+|Flip\d+)\b', raw_no_5g)
        if model_num_match:
            model_num = model_num_match.group(1)
            if model_num.lower() not in suggested_name.lower():
                suggested_name = f"{suggested_name} {model_num}"
        
        if detected_brand_id:
            suggested_name = f"Samsung {suggested_name}"
            
        return suggested_name

norm = MockNormalizer()
print(f"Result 1: {norm.normalize('Used Samsung Z Flip 6 5G 12/256GB')}")
print(f"Result 2: {norm.normalize('Samsung S26 Ultra 12')}")
