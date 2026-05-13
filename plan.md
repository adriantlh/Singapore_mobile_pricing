# Project Plan: SG Mobile Price Tracker

## 1. Technical Stack Overview
| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.11+ | Core logic, scraping, and data processing. |
| **Database** | PostgreSQL 15+ | Relational storage for Brands/Models + `JSONB` for variants, promos, and **condition metadata**. |
| **Scraping Engine** | Playwright + `playwright-stealth` | Handling JS-heavy sites (Shopee/Lazada) and evading bot detection. |
| **Parsing Engine** | BeautifulSoup4 / HTTPX | High-speed parsing for lightweight, static sites. |
| **Task Orchestration** | Celery + Redis | Managing the queue of scraping jobs and scheduling. |
| **Containerization** | Docker + Docker Compose | Ensuring the environment (DB, Redis, Scrapers) is portable and reproducible. |
| **API Layer** | FastAPI | Providing a structured interface for the frontend/external tools. |
| **Monitoring/Alerting** | Telegram Bot / Custom Dashboard | Alerting when a scraper fails or a major price drop occurs. |

---





## 2. Development Roadmap

### Phase 1: The Data Foundation (The "Source of Truth")
**Goal:** Establish the database schema and the ability to manually inject data.
*   **Task 1.1:** Design and implement the PostgreSQL schema (Brands $\rightarrow$ Families $\rightarrow$ Variants $\rightarrow$ Price Logs).
    *   *Note: Must support `condition` (New/Used/Refurbished) within the `attributes` JSONB.*
*   **Task 1.2:** Create the **Ingestor** module: A Python service that takes standardized JSON and performs the "Upsert" logic.
    *   *Note: Must handle mapping condition-specific metadata (e.g., battery health) to `price_logs`.*
*   **Task 1.3:** Build a basic CLI tool to manually add a new `brand` or `product_family` to the DB.

### Phase 2: The Adapter Engine (The "Workers")
**Goal:** Build the logic to extract data from the web (Retail and Refurbished Store sources).
*   **Task 2.1:** Develop the **Base Adapter Class**: An abstract class that defines the interface all scrapers must follow.
*   **Task 2.2:** Implement **Adapter #1 (Retail - Static)**: A simple scraper for a site with no bot protection.
*   **Task 2.3:** Implement **Adapter #2 (Retail - Dynamic)**: A Playwright-based scraper for complex sites (e.g., Shopee) using `stealth` mode.
*   **Task 2.4:** Implement **Adapter #3 (Refurbished/Used Store)**: An adapter specifically for mobile phone stores that focus on second-hand/refurbished units (extracting battery health, etc.).
*   **Task 2.5:** Implement the **Standardizer**: Logic to ensure all adapters output the exact same JSON structure (handling currency conversion to SGD).

### Phase *Note: We are intentionally avoiding P2P marketplaces like Carousell due to high bot protection complexity.*

### Phase 3: Orchestration & Automation (The "Brain")
**Goal:** Move from manual execution to a self-running system.
*   **Task 3.1:** Set up **Redis and Celery**: Create a task queue where the Orchestrator can "schedule" a scrape job.
*   **Task 3.2:** Build the **Orchestrator**: A service that reads the `sources` table and dispatches Celery tasks based on a schedule.
*   **Task 3.3:** Implement **Error Handling**: Logic to catch 403/429 errors and update the `sources.health_status` in the database.

### Phase 4: Resilience & Intelligence (The "Defense")
**Goal:** Protect the system from being blocked and add value-add tracking.
*   **Task 4.1:** **Proxy Integration**: Integrate a proxy rotation service into the Playwright/HTTPX layers.
*   **Task 4.2:** **Promotion Extraction**: Enhance the Ingestor to specifically parse and store "bundle" or "gift" info into the `JSONB` metadata field.
*   **Task 4.3:** **Alerting System**: A simple module that monitors `price_logs` and sends a notification (via Telegram or Email) when a price drops by $>10\%$.

### Phase 5: Visualization (The "Interface")
**Goal:** Make the data useful for the end-user.
*   **Task 5.1:** **API Layer**: A FastAPI wrapper around the PostgreSQL DB to serve data to a frontend.
*   **Task 5.2:** **Frontend Dashboard**: A simple web interface (Streamlit or React) to view:
    *   Current prices across all stores.
    *   **Filtering by Condition (New vs. Used/Refurbished).**
    *   Price history graphs (Time-series).
    *   "Best Deals" (Highest percentage drop in last 24h).

---

## 3. Critical Success Factors
1.  **Data Integrity:** The Ingestor must be extremely strict about data types to prevent "dirty" data from breaking the dashboard.
2.  **Scraper Stealth:** Continuous monitoring of `health_status` is required to ensure we aren't scraping "empty" pages due to undetected blocks.
3.  **Scalability:** The architecture must allow adding a new "Adapter" by simply dropping a new `.py` and configuration file into a folder.
