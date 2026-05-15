import asyncio
from src.database import Database
from src.normalizer import Normalizer
from src.ingestor import Ingestor
from src.adapters.redwhite_adapter import RedWhiteMobileAdapter
from src.adapters.mistermobile_adapter import MisterMobileAdapter
from src.adapters.whymobile_adapter import WhyMobileAdapter
from src.adapters.mobilestop_adapter import MobileStopAdapter
from src.models import ProductVariantInput

async def full_ingest():
    db = Database()
    normalizer = Normalizer(db)
    ingestor = Ingestor(db)
    
    sources = [
        # RedWhite Mobile
        (RedWhiteMobileAdapter, "RedWhite Mobile", "https://redwhitemobile.com/new-phones/", "new"),
        (RedWhiteMobileAdapter, "RedWhite Mobile (Used)", "https://redwhitemobile.com/used-phones-singapore/", "used"),
        # Mister Mobile
        (MisterMobileAdapter, "Mister Mobile", "https://www.mistermobile.com.sg/new-phone-mobile-shop-singapore/", "new"),
        (MisterMobileAdapter, "Mister Mobile (Used)", "https://www.mistermobile.com.sg/used-phone-singapore/?pa_condition:mint,pristine,satisfactory", "used"),
        # WhyMobile
        (WhyMobileAdapter, "WhyMobile (Apple)", "https://www.whymobile.com/products?brand=APL", "new"),
        (WhyMobileAdapter, "WhyMobile (Samsung)", "https://www.whymobile.com/products?brand=SAM", "new"),
        (WhyMobileAdapter, "WhyMobile (Google)", "https://www.whymobile.com/products?brand=GOOG", "new"),
        (WhyMobileAdapter, "WhyMobile (Used)", "https://www.whymobile.com/products?category=PREOWNED", "used"),
        # MobileStop
        (MobileStopAdapter, "MobileStop", "https://mobilestop.sg", "new")
    ]
    
    for adapter_class, source_name, url, default_condition in sources:
        print(f"--- Scraping {source_name} ---")
        try:
            adapter = adapter_class(source_name=source_name, base_url=url)
            valid_products = await adapter.run()
            
            for p in valid_products:
                # Re-normalize to ensure best family mapping
                norm = normalizer.normalize(p.variant_name)
                
                # Filter for Big 3
                if not norm['brand_id']:
                    continue

                p.family_name = norm['family_name'] or p.family_name
                p.family_slug = p.family_name.lower().replace(" ", "-")
                
                # Ensure condition is set if not already
                if not p.attributes.get('condition'):
                    p.attributes['condition'] = default_condition
                
                ingestor.ingest(p, category=norm['category'], released_at=norm['released_at'])
        except Exception as e:
            print(f"Error scraping {source_name}: {e}")

    db.close()

if __name__ == "__main__":
    asyncio.run(full_ingest())
