import os
import asyncio
from celery import Celery
from celery.schedules import crontab
from src.database import Database
from src.normalizer import Normalizer
from src.ingestor import Ingestor
from src.adapters.redwhite_adapter import RedWhiteMobileAdapter
from src.adapters.mistermobile_adapter import MisterMobileAdapter
from src.adapters.whymobile_adapter import WhyMobileAdapter
from src.adapters.mobilestop_adapter import MobileStopAdapter

# Initialize Celery
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
app = Celery("sg_mobile_pricing", broker=redis_url)

app.conf.beat_schedule = {
    "scrape-all-sources-12h": {
        "task": "src.orchestrator.scrape_all_sources",
        "schedule": crontab(hour="2,14", minute=0), # Every 12 hours (2 AM & 2 PM)
    },
    "process-triggered-alerts-12h": {
        "task": "src.orchestrator.process_triggered_alerts",
        "schedule": crontab(hour="3,15", minute=0), # Every 12 hours (3 AM & 3 PM)
    },
}
app.conf.timezone = "Asia/Singapore"

async def run_scrape_task(adapter_class, source_name, url, default_condition):
    db = Database()
    normalizer = Normalizer(db)
    ingestor = Ingestor(db)
    
    print(f"[{source_name}] Starting automated scrape...")
    try:
        adapter = adapter_class(source_name=source_name, base_url=url)
        valid_products = await adapter.run()
        
        for p in valid_products:
            norm = normalizer.normalize(p.variant_name)
            if not norm['brand_id']:
                continue

            p.family_name = norm['family_name'] or p.family_name
            p.family_slug = p.family_name.lower().replace(" ", "-")
            
            if not p.attributes.get('condition'):
                p.attributes['condition'] = default_condition
            
            ingestor.ingest(p, category=norm['category'], released_at=norm['released_at'])
    except Exception as e:
        print(f"[{source_name}] Scrape task failed: {e}")
    finally:
        db.close()

@app.task(bind=True, max_retries=3)
def scrape_source(self, source_key):
    """
    Scrapes a specific source by key with retry logic.
    """
    sources = {
        "redwhite_new": (RedWhiteMobileAdapter, "RedWhite Mobile", "https://redwhitemobile.com/new-phones/", "new"),
        "redwhite_used": (RedWhiteMobileAdapter, "RedWhite Mobile (Used)", "https://redwhitemobile.com/used-phones-singapore/", "used"),
        "mistermobile_new": (MisterMobileAdapter, "Mister Mobile", "https://www.mistermobile.com.sg/new-phone-mobile-shop-singapore/", "new"),
        "mistermobile_used": (MisterMobileAdapter, "Mister Mobile (Used)", "https://www.mistermobile.com.sg/used-phone-singapore/?pa_condition:mint,pristine,satisfactory", "used"),
        "whymobile_apple": (WhyMobileAdapter, "WhyMobile (Apple)", "https://www.whymobile.com/products?brand=APL", "new"),
        "whymobile_samsung": (WhyMobileAdapter, "WhyMobile (Samsung)", "https://www.whymobile.com/products?brand=SAM", "new"),
        "whymobile_google": (WhyMobileAdapter, "WhyMobile (Google)", "https://www.whymobile.com/products?brand=GOOG", "new"),
        "whymobile_used": (WhyMobileAdapter, "WhyMobile (Used)", "https://www.whymobile.com/products?category=PREOWNED", "used"),
        "mobilestop": (MobileStopAdapter, "MobileStop", "https://mobilestop.sg", "new")
    }
    
    if source_key not in sources:
        return f"Unknown source: {source_key}"
    
    try:
        adapter_class, source_name, url, default_condition = sources[source_key]
        asyncio.run(run_scrape_task(adapter_class, source_name, url, default_condition))
        return f"Completed scrape for {source_name}"
    except Exception as exc:
        print(f"[{source_key}] Task failed, retrying in 60s... (Attempt {self.request.retries + 1}/3)")
        raise self.retry(exc=exc, countdown=60)

@app.task
def scrape_all_sources():
    """
    Triggers all scrape tasks.
    """
    source_keys = [
        "redwhite_new", "redwhite_used", "mistermobile_new", "mistermobile_used",
        "whymobile_apple", "whymobile_samsung", "whymobile_google", "whymobile_used",
        "mobilestop"
    ]
    for key in source_keys:
        scrape_source.delay(key)
    return "All scrape tasks triggered"

@app.task
def process_triggered_alerts():
    """
    Collects and sends alerts for drops detected in the last 24h.
    """
    from src.notifier import Notifier
    db = Database()
    
    query = """
        SELECT 
            pv.name, 
            ta.price_before as old_price, 
            ta.price_after as new_price, 
            ta.percentage_drop as drop,
            pl.url,
            s.name as source
        FROM triggered_alerts ta
        JOIN product_variants pv ON ta.variant_id = pv.id
        JOIN (
            SELECT DISTINCT ON (variant_id) variant_id, url, source_id
            FROM price_logs
            ORDER BY variant_id, scraped_at DESC
        ) pl ON pv.id = pl.variant_id
        JOIN sources s ON pl.source_id = s.id
        WHERE ta.triggered_at > NOW() - INTERVAL '24 hours'
        ORDER BY ta.percentage_drop DESC;
    """
    alerts = db.execute(query, fetch=True)
    
    if alerts:
        notifier = Notifier()
        notifier.send_price_drop_email(alerts)
    
    db.close()
    return f"Processed {len(alerts)} alerts"
