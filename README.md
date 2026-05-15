# SG Mobile Price Tracker

A pricing aggregator designed to track and monitor mobile phone prices across various Singaporean retailers, including both new and refurbished markets.

## 🚀 Overview

This system automatically scrapes pricing information from multiple sources, normalizes the data, and stores it in a central database to provide historical price tracking and deal discovery.

### Key Features
- **Adapter-Based Scraping**: Modular scrapers for different site structures (Static, Dynamic, and Site-specific).
- **Price Comparison**: Aggregates and compares prices for the exact same model across multiple retailers side-by-side.
- **Precision Normalization**: Intelligently strips noise while ensuring model numbers and specs (Storage, RAM, Color) are preserved for accurate grouping.
- **Price History**: Tracks price changes over time to identify trends and best deals.
- **Responsive Dashboard**: A modern React-based frontend to visualize current prices and historical data.

## 🛠 Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic
- **Database**: PostgreSQL 15 (Time-series price logs + JSONB attributes)
- **Scraping**: BeautifulSoup4, HTTPX (Playwright support planned)
- **Frontend**: React (TypeScript), Tailwind CSS, Lucide React, Recharts
- **Containerization**: Docker, Docker Compose

## 📁 Project Structure

```text
.
├── src/
│   ├── api/            # FastAPI implementation
│   ├── adapters/       # Site-specific scraping logic
│   ├── models.py       # Pydantic data models
│   ├── database.py     # Database connection management
│   ├── ingestor.py     # Data upsert and normalization logic
│   └── manager.py      # CLI/Management utilities
├── frontend/           # React application
├── tests/              # Verification and debug scripts
├── schema.sql          # PostgreSQL database schema
└── docker-compose.yml  # System orchestration
```

## 🚦 Getting Started

### Prerequisites
- Docker and Docker Compose

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Singapore_mobile_pricing
   ```

2. **Launch the system**:
   ```bash
   docker-compose up -d
   ```
   This will start:
   - **PostgreSQL**: Accessible at `localhost:5432`
   - **API**: Accessible at `localhost:8000`
   - **Frontend**: Accessible at `localhost:80`

3. **Initialize the Database**:
   The schema is automatically applied during container startup via `docker-entrypoint-initdb.d`.

4. **Run a Sample Ingestion**:
   To populate the database with sample data:
   ```bash
   docker exec -it singapore_mobile_pricing-api-1 python src/main.py
   ```

## 📊 Current Status

### Completed
- [x] **Database Schema**: Full support for brands, families, variants, and time-series price logs.
- [x] **Intelligence Engine**: Robust `Normalizer` for fuzzy matching and precision generational naming.
- [x] **Cross-Source Overlap**: Accurate grouping of identical models across different retailers.
- [x] **Big 3 Focus**: Optimized tracking for **Apple, Samsung, and Google** devices.
- [x] **API & Frontend**: Functional dashboard with side-by-side multi-source price comparison and purchase links.
- [x] **Tracked Retailers**: 
    - **RedWhite Mobile** (Static / New & Used)
    - **Mister Mobile** (Deep Variation Scrape / New & Used)
    - **WhyMobile** (Static / Brand-Specific & Used)
    - **MobileStop** (Shopify JSON / Accessories & Variants)

### In Progress / Planned
- [ ] **Orchestrator**: Automated scheduling of scraping jobs via Celery/Redis.
- [ ] **Alerting**: Notification system for price drops.
- [ ] **Dynamic Scrapers**: Playwright support for high-protection sites.
- [ ] **Proxy Rotation**: Enhanced resilience against bot detection.

## 🧪 Testing
Run test scripts to verify adapters or database connectivity:
```bash
PYTHONPATH=. python3 tests/test_redwhite_ingestion.py
```

## 📜 License
Internal Project - All Rights Reserved.
