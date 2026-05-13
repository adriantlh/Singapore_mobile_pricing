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
    - [x] Implementing: Define the abstract interface for all scrapers.
- [x] **Task 2.2: Adapter #1 (Static Site)**
    - [x] Completed: Implement scraper for a simple, non-JS site.
- [ ] **Task 2.3: Adapter #2 (Dynamic Site)**
    - [ ] Implement Playwright-based scraper with `stealth` mode.
- [ ] **Task 2.4: Adapter #3 (Refurbished/Used Store)**
    - [ ] Implement scraper for second-hand specialized stores.
- [ ] **Task 2.5: The Standardizer**
    - [ ] Implement logic to normalize all incoming data to the standard JSON format.

## Phase 3: Orchestration & Automation
- [ ] **Task 3.1: Infrastructure Setup**
    - [ ] Set up Redis and Celery.
- [ ] **Task 3.2: The Orchestrator**
    - [ ] Implement the scheduler to trigger scrapes based on source configuration.
- [ ] **Task 3.3: Error & Health Monitoring**
    - [ ] Implement logic to update `sources.health_status` on failure.

## Phase 4: Resilience & Intelligence
- [ ] **Task 4.1: Proxy Integration**
    - [ ] Implement proxy rotation in the scraping layer.
- [ ] **Task 4.2: Promotion Extraction**
    - [ ] Enhance parsing logic for bundle/gift detection.
- [ ] ** **Task 4.3: Alerting System
    - [ ] Implement Telegram/Email alerts for significant price drops.

## Phase 5: Visualization
- [x] **Task 5.1: API Layer (FastAPI)**
    - [x] Completed: Create endpoints for product lists, price history, and alerts.
- [x] **Task 5.2: Frontend Dashboard**
    - [x] Completed: Build a React dashboard to visualize trends and "Best Deals".
- [x] **Task 5.3: Containerization**
    - [x] Completed: Dockerize backend, frontend, and database using Docker Compose.

