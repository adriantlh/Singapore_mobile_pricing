# Workplan: SG Mobile Price Tracker

This document tracks the active implementation progress of the project.

## Phase 1: The Data Foundation
- [x] **Task 1.1: PostgreSQL Schema Implementation**
    - [x] Design schema with Brands, Families, Variants, Sources, and Price Logs.
    | [x] Implement JSONB for flexible attributes and metadata.
    - [x] Implement indexing for performance.
- [x] **Task 1.2: Ingestor Module Development**
    - [x] Implement `Database` class for connection management.
    - [x] Implement `Ingestor` class with "Upsert" logic.
    - [x] Implement `ProductVariantInput` validation using Pydenc.
- [x] **Task 1.3: CLI Tooling**
    - [x] Completed: Create a CLI to manually add/manage brands and families.

## Phase 2: The Adapter Engine
- [x] **Task 2.1: Base Adapter Class**
    - [x] Completed: Define the abstract interface for all scrapers.
- [x] **Task 2.2: Retail Adapters (Static & JSON)**
    - [x] Completed: Implement scrapers for RedWhite Mobile, Mister Mobile, WhyMobile, and MobileStop.
- [x] **Task 2.3: Used/Refurbished Specialization**
    - [x] Completed: Built deep-scraping logic for specialized used device retailers.
- [x] **Task 2.4: The Intelligence Engine (Standardizer)**
    - [x] Completed: Implemented the `Normalizer` to handle fuzzy matching, precision generational naming, cross-source data overlap, and specialized mid-range/modifier separation (Samsung A-series, Pixel Pro XL/Fold).

## Phase 3: Orchestration & Automation
- [x] **Task 3.1: Infrastructure Setup**
    - [x] Completed: Set up Redis and Celery in Docker Compose.
- [x] **Task 3.2: The Orchestrator**
    - [x] Completed: Implemented Celery tasks with twice-daily scheduling (every 12 hours) for all 4 sources.
- [x] **Task 3.3: Error & Health Monitoring**
    - [x] Completed: Implemented concurrency management and exponential backoff retries (3 attempts) to ensure reliability.

## Phase 4: Resilience & Intelligence
- [x] **Task 4.1: Proxy Integration**
    - [x] Completed: Implemented proxy rotation logic in `BaseAdapter` and all retailer scrapers.
- [ ] **Task 4.2: Promotion Extraction**
    - [ ] Enhance parsing logic for bundle/gift detection.
- [x] **Task 4.3: Alerting System**
    - [x] Completed: Built a price drop detection engine and an Email notification service.

## Phase 5: Visualization
- [x] **Task 5.1: API Layer (FastAPI)**
    - [x] Completed: Create endpoints for product lists, price history, and alerts.
- [x] **Task 5.2: Frontend Dashboard**
    - [x] Completed: Built a modern 'E-commerce Standard' React dashboard with a sticky top bar, horizontal 'Top Deals' carousel, and clear CTA purchase buttons.
- [x] **Task 5.3: Containerization**
    - [x] Completed: Dockerize backend, frontend, and database using Docker Compose.

