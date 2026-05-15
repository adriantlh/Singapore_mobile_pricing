import json
import os
import re
from datetime import datetime
from src.database import Database

def parse_release_date(date_str):
    if not date_str:
        return None
    # Example: "Released 1999", "Released 2021, September"
    match = re.search(r'(\d{4})', date_str)
    if match:
        year = match.group(1)
        # Just use Jan 1st of that year for simplicity if month is missing
        return f"{year}-01-01"
    return None

def infer_category(name, specs):
    name_lower = name.lower()
    if any(x in name_lower for x in ["watch", "gear", "fit"]):
        return "watch"
    if any(x in name_lower for x in ["tab", "pad", "surface", "folio"]):
        return "tablet"
    
    # Check specs for screen size if possible
    if specs:
        try:
            spec_dict = json.loads(specs)
            display = spec_dict.get("Size", "").lower()
            match = re.search(r'(\d+\.?\d*)\s*inches', display)
            if match:
                size = float(match.group(1))
                if size >= 7.5:
                    return "tablet"
        except:
            pass
            
    return "phone"

def seed_catalog():
    db = Database()
    
    # Paths to seed files (downloaded in root)
    brands_path = "brands_seed.json"
    devices_path = "devices_seed.json"
    
    if not os.path.exists(brands_path) or not os.path.exists(devices_path):
        print("Seed files not found. Run the download command first.")
        return

    print("Loading brands...")
    with open(brands_path, 'r') as f:
        brands_data = json.load(f)["RECORDS"]
    
    print("Loading devices...")
    with open(devices_path, 'r') as f:
        devices_data = json.load(f)["RECORDS"]

    # 1. Map brands for quick lookup
    brand_id_map = {}
    print(f"Seeding {len(brands_data)} brands...")
    for b in brands_data:
        brand_name = b["name"]
        query = "INSERT INTO brands (name) VALUES (%s) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id;"
        res = db.execute(query, (brand_name,), fetch=True)
        if res:
            brand_id_map[b["id"]] = res[0]['id']

    # 2. Seed product families
    print(f"Seeding {len(devices_data)} product families...")
    batch_size = 500
    for i in range(0, len(devices_data), batch_size):
        batch = devices_data[i:i + batch_size]
        for d in batch:
            brand_uuid = brand_id_map.get(d["brand_id"])
            if not brand_uuid:
                continue
            
            family_name = d["name"]
            slug = family_name.lower().replace(" ", "-").replace("/", "-")
            
            release_date = parse_release_date(d.get("released_at"))
            category = infer_category(family_name, d.get("specifications"))
            
            # Upsert family with new fields
            query = """
                INSERT INTO product_families (brand_id, name, slug, category, released_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (slug) DO UPDATE SET 
                    category = EXCLUDED.category,
                    released_at = EXCLUDED.released_at;
            """
            db.execute(query, (brand_uuid, family_name, slug, category, release_date))
        
        print(f"Processed {min(i + batch_size, len(devices_data))}/{len(devices_data)} devices...")

    db.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_catalog()
