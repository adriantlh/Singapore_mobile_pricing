# SG Mobile Price Tracker - Project Instructions

This project is a pricing aggregator designed to track and monitor the prices of mobile phones and devices across various Singaporean retailers.

## Core Purpose
The system automatically scrapes pricing information from multiple sources, normalizes the data, and stores it in a central database to provide historical price tracking and deal discovery.

## Architectural Principles

### 1. Catalog-Driven Scrapes
- **Master Catalog**: The system is seeded with a canonical list of Brands and Product Families (10,000+ devices) from external sources.
- **Normalizer Engine**: Every scraped title passes through a `Normalizer` that uses fuzzy matching (`RapidFuzz`) to map it to a canonical model.
- **Auto-Discovery**: If no high-confidence match is found, the system automatically creates a new Brand/Family to ensure no data is lost.
- **Site-Specific Adapters**: Every target website has its own adapter located in `src/adapters/`.
- **Inheritance**: All adapters must inherit from `BaseAdapter`.

### 2. Data Flow
- **Scrape**: Fetch raw HTML/JS content (using `httpx` for static or `Playwright` for dynamic sites).
- **Parse**: Extract fields (Brand, Model, Price, Promo, URL) into a raw dictionary.
- **Validate**: Convert raw dictionaries into standardized `ProductVariantInput` Pydantic models.
- **Ingest**: Use the `Ingestor` module to upsert data into PostgreSQL, maintaining the `price_logs` history.

### 3. Normalization Standards
- **Currency**: All prices must be stored in SGD.
- **Conditions**: Explicitly track "New" vs. "Used/Refurbished" conditions in the product attributes.
- **Deduplication**: Adapters are responsible for deduplicating products (usually by URL) before ingestion.

### 4. Engineering Standards
- **Type Safety**: Use Pydantic models for all data passing through the pipeline.
- **Resilience**: Implement timeouts and error handling in the `scrape` phase to prevent one failing source from blocking the system.
- **Testing**: Every adapter update should be verified with a corresponding test script in the `tests/` directory.

## Current Target Sites
- **RedWhite Mobile**: Static site parsing for New and Used phones. 
  - *Note*: The source data contains inconsistencies, such as mixing payment banners (e.g., "Shopee PayLater") with real products. Aggressive filtering and naming standardization are required.
- **Static Adapter**: General-purpose adapter for simple HTML structures.
