# SG Mobile Price Tracker

A pricing aggregator designed to track and monitor mobile phone prices across various Singaporean retailers, including both new and refurbished markets.

## 🚀 Overview

This system automatically scrapes pricing information from multiple sources, normalizes the data, and stores it in a central database to provide historical price tracking and deal discovery.

### Key Features
- **Modern UI/UX**: Consumer-friendly 'E-commerce Standard' dashboard with sticky filters, horizontal 'Top Deals' highlights, and interactive brand placeholders.
- **Side-by-Side Comparison**: View and compare live prices from 4 major Singaporean retailers simultaneously.
- **Proactive Deal Alerts**: Automatic detection of significant price drops (≥5%) with daily email notifications.
- **Precision Normalization**: Intelligently strips noise while ensuring flagship model numbers and mid-range variants (Samsung A-series, Pixel Pro XL) are perfectly preserved.
- **Autonomous Scraping**: Fully automated pipeline running every 12 hours with Redis/Celery orchestration.
- **Price History**: Tracks price changes over time to identify trends and best deals.

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
- [x] **Intelligence Engine**: Robust `Normalizer` for fuzzy matching, generational naming, and promotion extraction.
- [x] **Autonomous Pipeline**: 12-hour automated scraping and deal processing via Redis/Celery.
- [x] **Proactive Alerting**: System logs significant price drops and sends daily deal summaries via Email.
- [x] **Cross-Source Overlap**: Accurate grouping of identical models across different retailers.
- [x] **E-commerce Dashboard**: Modern React UI with Top Deals carousel, sticky filters, and direct purchase links.
- [x] **Tracked Retailers**: RedWhite Mobile, Mister Mobile, WhyMobile, MobileStop.

### In Progress / Planned
- [ ] **Dynamic Scrapers**: Playwright support for high-protection sites (Lazada/Shopee).
- [ ] **Advanced Predictions**: Use history data to predict future price trends.

## 🧪 Testing
Run test scripts to verify adapters or database connectivity:
```bash
PYTHONPATH=. python3 tests/test_redwhite_ingestion.py
```

## 📜 License
Internal Project - All Rights Reserved.
