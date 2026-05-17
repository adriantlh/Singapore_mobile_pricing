import json
from src.database import Database
from src.models import ProductVariantInput
from src.normalizer import Normalizer

class Ingestor:
    def __init__(self, db: Database):
        self.db = db
        self.normalizer = Normalizer(db)

    def ingest(self, data: ProductVariantInput, category: str = "phone", released_at: str = None):
        # 1. Normalize Brand Name
        brand_name = self.normalizer.normalize_brand(data.brand_name)
        if brand_name == "Unknown":
            print(f"Skipping non-target brand: {data.brand_name}")
            return
        
        # 2. Upsert Brand
        brand_query = """
            INSERT INTO brands (name)
            VALUES (%s)
            ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
            RETURNING id;
        """
        brand_res = self.db.execute(brand_query, (brand_name,), fetch=True)
        if not brand_res:
            raise Exception("Failed to upsert brand")
        brand_id = brand_res[0]['id']

        # 3. Upsert Family
        family_query = """
            INSERT INTO product_families (brand_id, name, slug, category, released_at, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (slug) DO UPDATE SET 
                name = EXCLUDED.name,
                category = EXCLUDED.category,
                released_at = COALESCE(EXCLUDED.released_at, product_families.released_at),
                image_url = COALESCE(EXCLUDED.image_url, product_families.image_url)
            RETURNING id;
        """
        family_res = self.db.execute(family_query, (brand_id, data.family_name, data.family_slug, category, released_at, data.image_url), fetch=True)
        if not family_res:
            raise Exception("Failed to upsert family")
        family_id = family_res[0]['id']

        # 3. Upsert Variant
        # We check if a variant with this name exists for this family
        check_variant_query = "SELECT id FROM product_variants WHERE family_id = %s AND name = %s;"
        variant_res = self.db.execute(check_variant_query, (family_id, data.variant_name), fetch=True)

        if variant_res:
            variant_id = variant_res[0]['id']
            # Update attributes in case they changed
            update_variant_query = "UPDATE product_variants SET attributes = %s WHERE id = %s;"
            self.db.execute(update_variant_query, (json.dumps(data.attributes), variant_id))
        else:
            variant_query = """
                INSERT INTO product_variants (family_id, name, attributes)
                VALUES (%s, %s, %s)
                RETURNING id;
            """
            variant_res = self.db.execute(variant_query, (family_id, data.variant_name, json.dumps(data.attributes)), fetch=True)
            if not variant_res:
                raise Exception("Failed to upsert variant")
            variant_id = variant_res[0]['id']

        # 4. Upsert Source
        source_query = """
            INSERT INTO sources (name, base_url)
            VALUES (%s, %s)
            ON CONFLICT (name) DO UPDATE SET base_url = EXCLUDED.base_url
            RETURNING id;
        """
        source_res = self.db.execute(source_query, (data.source_name, data.source_url), fetch=True)
        if not source_res:
            raise Exception("Failed to upsert source")
        source_id = source_res[0]['id']

        # 5. Log Price
        # Detect significant price drops
        last_price_query = """
            SELECT price FROM price_logs 
            WHERE variant_id = %s AND source_id = %s
            ORDER BY scraped_at DESC LIMIT 1;
        """
        last_price_res = self.db.execute(last_price_query, (variant_id, source_id), fetch=True)
        
        if last_price_res:
            old_price = float(last_price_res[0]['price'])
            if data.price < old_price:
                drop_pct = ((old_price - data.price) / old_price) * 100
                if drop_pct >= 5.0:
                    # Log triggered alert
                    alert_query = """
                        INSERT INTO triggered_alerts (variant_id, price_before, price_after, percentage_drop)
                        VALUES (%s, %s, %s, %s);
                    """
                    self.db.execute(alert_query, (variant_id, old_price, data.price, drop_pct))
                    print(f"!!! ALERT: Price drop detected for {data.variant_name}: {old_price} -> {data.price} (-{drop_pct:.1f}%)")

        price_log_query = """
            INSERT INTO price_logs (variant_id, source_id, price, currency, url, metadata)
            VALUES (%s, %s, %s, %s, %s, %s);
        """
        self.db.execute(price_log_query, (
            variant_id,
            source_id,
            data.price,
            data.currency,
            data.url,
            json.dumps(data.metadata)
        ))

        print(f"Successfully ingested price for {data.variant_name} from {data.source_name}")
