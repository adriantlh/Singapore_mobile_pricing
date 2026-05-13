import json
from src.database import Database

class Manager:
    def __init__(self, db: Database):
        self.db = db

    def add_brand(self, name: str):
        query = "INSERT INTO brands (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;"
        self.db.execute(query, (name,))
        return f"Brand '{name}' added or already exists."

    def add_family(self, brand_id: str, name: str, slug: str):
        query = "INSERT INTO product_families (brand_id, name, slug) VALUES (%s, %s, %s) ON CONFLICT (slug) DO NOTHING;"
        self.db.execute(query, (brand_id, name, slug))
        return f"Family '{name}' added or already exists."
