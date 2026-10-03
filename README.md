# PETA UMKM — Geospatial & Product Scraper Intelligence Suite

A production-grade, modular web scraping engine and interactive geospatial analytics dashboard designed to discover, extract, enrich, and map Indonesian UMKM (MSMEs) and their marketplace & social commerce products across **Google Maps**, **Instagram**, **Tokopedia**, and **Shopee**.

---

## Key Features

1. **Multi-Source Scraping Pipeline**:
   - **Google Maps Extractor**: Discovers UMKM business names, categories, addresses, ratings, review counts, and exact GPS latitude/longitude coordinates.
   - **Marketplace Extractor (Tokopedia & Shopee)**: Extracts product titles, current prices, discount/original prices, ratings, units sold, product images, and product URLs.
   - **Instagram Social Commerce Extractor**: Extracts public bios, official WhatsApp links (`wa.me/...`), and profile links.
   - **Stealth Browser Engine**: Playwright-based anti-bot evasion with randomized user agents, realistic human scroll/delays, and direct fallback extractors.

2. **Geospatial & Product Intelligence Dashboard**:
   - Built following **Stitch Design System** guidelines (`Geist` typography, dark-zinc precision palette, no emoji clutter, cockpit density).
   - **Interactive Leaflet Map**: Dark-matter vector tiles with categorized UMKM markers (Kuliner, Fashion, Kriya, Herbal), popup summaries, and zoom clustering.
   - **Bento Feed & Catalog**: Searchable and filterable by city (Jakarta, Bandung, Yogyakarta, Solo, Surabaya, Malang, Bali, Medan, Makassar), category, and keyword.
   - **UMKM Inspection Drawer**: Deep-dive into store information, full product catalog, direct WhatsApp connect button, and marketplace links.
   - **In-App Scraper Console**: Trigger live scraping directly from the web interface for any custom query or region.

3. **Data Export & Storage**:
   - **SQLite Database** with full relations (`umkm`, `products`, `scrape_jobs`).
   - **1-Click GeoJSON Export**: Export for GIS tools (QGIS, ArcGIS, Mapbox).
   - **1-Click CSV Export**: Export for spreadsheet analysis (Excel, Pandas, Google Sheets).

---

## Directory Structure

```
├── backend/
│   ├── __init__.py
│   └── server.py              # FastAPI application & REST endpoints
├── database/
│   ├── __init__.py
│   ├── models.py              # Dataclasses & schema (UMKM, Product, ScrapeJob)
│   └── db_manager.py          # SQLite CRUD, stats & GeoJSON/CSV export
├── frontend/
│   ├── DESIGN.md              # Semantic design specification (Stitch standards)
│   ├── index.html             # Dashboard UI
│   ├── styles.css             # Dark-neutral styling
│   └── app.js                 # Leaflet mapping & frontend logic
├── scraper/
│   ├── __init__.py
│   ├── config.py              # Anti-bot user-agents & request headers
│   ├── stealth_browser.py     # Playwright stealth browser launcher
│   ├── gmaps_scraper.py       # Google Maps extractor
│   ├── marketplace_scraper.py # Tokopedia & Shopee extractor
│   └── instagram_scraper.py   # Instagram profile & WhatsApp extractor
├── data/
│   └── umkm_data.db           # SQLite database
├── seed_data.py               # Pre-populated high-fidelity dataset
├── run.py                     # One-command application launcher
└── requirements.txt           # Dependencies
```

---

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

*(Optional for full Playwright browser engine)*:
```bash
playwright install chromium
```

### 2. Seed Initial Data
```bash
python seed_data.py
```

### 3. Launch Dashboard & API
```bash
python run.py
```
Open your browser at `http://127.0.0.1:8000`.

---

## API Endpoints

- `GET /api/stats` — Overall metrics (total UMKM, total products, average price, total sold volume).
- `GET /api/umkm?city=Bandung&category=Kopi&search=Aroma` — Filtered UMKM list with pricing ranges.
- `GET /api/umkm/{id}` — Full UMKM details with associated marketplace products.
- `GET /api/products` — Global marketplace product intelligence feed.
- `POST /api/scrape` — Trigger live extraction job (`{ "source": "all", "query": "Batik Solo", "limit": 6 }`).
- `GET /api/export/geojson` — Download GeoJSON spatial file.
- `GET /api/export/csv` — Download CSV dataset.
