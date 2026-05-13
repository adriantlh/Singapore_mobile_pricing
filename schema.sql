-- PostgreSQL Schema for SG Mobile Price Tracker

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 1. Brands Table
CREATE TABLE IF NOT EXISTS brands (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Product Families Table (e.g., "Samsung Galaxy S25")
CREATE TABLE IF NOT EXISTS product_families (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Product Variants Table (e.g., "S25 256GB Black")
CREATE TABLE IF NOT EXISTS product_variants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    family_id UUID NOT NULL REFERENCES product_abilities(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    -- attributes stores: {"storage": "256GB", "color": "Black", "condition": "new"}
    attributes JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Sources Table (e.g., "Shopee", "Lazada", "Refurbished Store X")
CREATE TABLE IF NOT EXISTS sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    base_url TEXT,
    health_status TEXT NOT NULL DEFAULT 'active', -- 'active', 'devent', 'blocked'
    last_error TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Price Logs Table (The time-series data)
CREATE TABLE IF NOT IF EXISTS price_logs (
    id BIGSERIAL PRIMARY KEY,
    variant_id UUID NOT NULL REFERENCES product_variants(id) ON DELETE CASCADE,
    source_id UUID NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    price NUMERIC(12, 2) NOT NULL,
    currency CHAR(3) NOT NULL DEFAULT 'SGD',
    url TEXT NOT NULL,
    -- metadata stores: {"promo": "Free Case", "battery_health": "95%", "voucher": "SG5OFF"}
    metadata JSONB NOT NULL DEFAULT '{}',
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_product_variants_family_id ON product_variants(family_id);
CREATE INDEX IF NOT EXISTS idx_price_logs_variant_id ON price_logs(variant_id);
CREATE INDEX IF NOT EXISTS idx_price_logs_source_id ON price_logs(source_id);
CREATE INDEX IF NOT EXISTS idx_price_logs_scraped_at ON price_logs(scraped_at);
CREATE INDEX IF NOT EXISTS idx_product_variants_attributes ON product_variants USING GIN (attributes);
CREATE INDEX IF NOT EXISTS idx_price_logs_metadata ON price_logs USING GIN (metadata);
