from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from src.database import Database
import os

app = FastAPI(title="SG Mobile Price Tracker API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()

@app.get("/")
def read_root():
    return {"message": "Welcome to the SG Mobile Price Tracker API"}

@app.get("/api/products")
def get_products():
    """
    Retrieve a list of product variants with their most recent scraped price.
    """
    query = """
    SELECT 
        pv.id, 
        pv.name, 
        pv.attributes, 
        b.name as brand_name,
        pl.price,
        pl.currency,
        pl.scraped_at,
        s.name as source_name
    FROM product_variants pv
    JOIN product_families pf ON pv.family_id = pf.id
    JOIN brands b ON pf.brand_id = b.id
    JOIN (
        SELECT DISTINCT ON (variant_id) variant_id, price, currency, scraped_at, source_id
        FROM price_logs
        ORDER BY variant_id, scraped_at DESC
    ) pl ON pv.id = pl.variant_id
    JOIN sources s ON pl.source_id = s.id
    ORDER BY b.name, pv.name;
    """
    try:
        results = db.execute(query, fetch=True)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{variant_id}/history")
def get_product_history(variant_id: str):
    """
    Retrieve the time-series price logs for a specific product variant.
    """
    query = """
    SELECT price, currency, scraped_at, source_id
    FROM price_logs
    WHERE variant_id = %s
    ORDER BY scraped_at ASC;
    """
    try:
        results = db.execute(query, (variant_id,), fetch=True)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sources")
def get_sources():
    """
    Retrieve source health statuses.
    """
    query = "SELECT id, name, base_url, health_status, last_error FROM sources;"
    try:
        results = db.execute(query, fetch=True)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
