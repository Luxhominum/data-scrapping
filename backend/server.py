"""
FastAPI Server — Apify-Compatible Modular Web Scraping & Automation Platform (v2)
"""
import os
import io
import asyncio
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, Query, BackgroundTasks, HTTPException, Body
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from database.db_manager import DatabaseManager
from database.models import UMKM, Product
from actors.registry import actor_registry
from actors.runner import actor_runner

app = FastAPI(
    title="Apify-Compatible Scraper & Automation Platform",
    description="Modular Actor Framework, Isolated Run Datasets, and Geospatial Intelligence Suite",
    version="2.0.0"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Mount static files
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

db = DatabaseManager()

# ==========================================
# 1. APIFY REST API V2 (ACTORS & RUNS)
# ==========================================

class ActorRunPayload(BaseModel):
    input: Optional[Dict[str, Any]] = None
    webhook_url: Optional[str] = None

@app.get("/api/v2/acts", summary="List all Actors in Store")
async def list_store_actors():
    """Returns catalog of all registered Actors in the Apify Actor Store"""
    return {
        "status": "success",
        "data": actor_registry.list_actors()
    }

@app.get("/api/v2/acts/{actor_id}", summary="Get Actor Details & Schema")
async def get_actor_detail(actor_id: str):
    actor = actor_registry.get_actor(actor_id)
    if not actor:
        raise HTTPException(status_code=404, detail=f"Actor '{actor_id}' not found.")
    return {
        "status": "success",
        "data": actor.metadata.to_dict()
    }

@app.post("/api/v2/acts/{actor_id}/runs", summary="Trigger Actor Run")
async def run_actor(actor_id: str, payload: Optional[Dict[str, Any]] = Body(None)):
    """Triggers an asynchronous Actor execution run and returns run_id"""
    input_data = payload.get("input", {}) if payload and "input" in payload else (payload or {})
    webhook_url = payload.get("webhook_url") if payload else None

    try:
        run_meta = actor_runner.trigger_run(actor_id, input_data, webhook_url=webhook_url)
        return {
            "status": "success",
            "message": f"Actor '{actor_id}' started successfully.",
            "data": run_meta
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v2/actor-runs", summary="List Execution Runs History")
async def list_actor_runs(limit: int = Query(50)):
    """Returns list of past and active Actor execution runs"""
    return {
        "status": "success",
        "data": actor_runner.list_runs(limit=limit)
    }

@app.get("/api/v2/actor-runs/{run_id}", summary="Get Run Status & Metadata")
async def get_run_status(run_id: str):
    run_meta = actor_runner.get_run(run_id)
    if not run_meta:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found.")
    return {
        "status": "success",
        "data": run_meta
    }

@app.get("/api/v2/actor-runs/{run_id}/logs", summary="Get Live Run Logs")
async def get_run_logs(run_id: str):
    logs = actor_runner.get_run_logs(run_id)
    return PlainTextResponse(content=logs)

# ==========================================
# 2. APIFY DATASETS & EXPORTERS
# ==========================================

@app.get("/api/v2/datasets/{dataset_id}/items", summary="Get Dataset JSON Items")
async def get_dataset_items(dataset_id: str):
    items = actor_runner.get_dataset_items(dataset_id)
    return JSONResponse(content=items)

@app.get("/api/v2/datasets/{dataset_id}/csv", summary="Download Dataset as CSV")
async def download_dataset_csv(dataset_id: str):
    df = actor_runner.get_dataset_csv_dataframe(dataset_id)
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    return StreamingResponse(
        io.BytesIO(stream.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={dataset_id}_dataset.csv"}
    )

@app.get("/api/v2/datasets/{dataset_id}/excel", summary="Download Dataset as Excel")
async def download_dataset_excel(dataset_id: str):
    df = actor_runner.get_dataset_csv_dataframe(dataset_id)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Scraped Data")
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={dataset_id}_dataset.xlsx"}
    )

# ==========================================
# 3. SHOPEE REVIEW STUDIO ENDPOINTS & SSE
# ==========================================

@app.get("/shopee", response_class=HTMLResponse)
async def serve_shopee_studio():
    shopee_path = os.path.join(FRONTEND_DIR, "shopee.html")
    if os.path.exists(shopee_path):
        with open(shopee_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Shopee Studio file not found</h1>", status_code=404)

class ShopeeScrapeRequest(BaseModel):
    url: str
    review_limit: Optional[int] = 50
    all_star_types: Optional[bool] = False
    star_limit_per_type: Optional[int] = 10
    cookie_str: Optional[str] = ""

@app.post("/api/shopee/scrape-url", summary="Trigger Shopee Review Scrape")
async def trigger_shopee_scrape(req: ShopeeScrapeRequest):
    """Triggers an async Shopee Review Extraction run and returns run_id"""
    url = req.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Shopee Product URL is required.")
    
    input_data = {
        "product_url": url,
        "review_limit": req.review_limit or 50,
        "all_star_types": bool(req.all_star_types),
        "star_limit_per_type": req.star_limit_per_type or 10,
        "cookie_str": req.cookie_str or ""
    }

    try:
        run_meta = actor_runner.trigger_run("shopee-review-scraper", input_data)
        return {
            "status": "success",
            "message": "Shopee Review Scraper initiated.",
            "data": run_meta
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/shopee/runs/{run_id}/stream", summary="SSE Live Log & Status Stream")
async def stream_shopee_run_logs(run_id: str):
    """Server-Sent Events stream for live terminal logs and real-time execution status"""
    async def log_event_generator():
        log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "logs", f"{run_id}.log")
        last_pos = 0
        
        while True:
            run_meta = actor_runner.get_run(run_id)
            if not run_meta:
                yield f"data: {json.dumps({'error': 'Run not found'})}\n\n"
                break

            status = run_meta.get("status", "UNKNOWN")
            
            # Read new log lines
            new_logs = []
            if os.path.exists(log_file):
                with open(log_file, "r", encoding="utf-8", errors="ignore") as f:
                    f.seek(last_pos)
                    lines = f.readlines()
                    last_pos = f.tell()
                    new_logs = [l.strip() for l in lines if l.strip()]

            if new_logs:
                for line in new_logs:
                    yield f"data: {json.dumps({'type': 'log', 'line': line, 'status': status})}\n\n"

            if status in ["SUCCEEDED", "FAILED"]:
                # Fetch final dataset preview if available
                items = actor_runner.get_dataset_items(run_id)
                yield f"data: {json.dumps({'type': 'finished', 'status': status, 'item_count': len(items), 'run': run_meta})}\n\n"
                break

            await asyncio.sleep(0.8)

    return StreamingResponse(
        log_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@app.get("/api/shopee/sample-data", summary="Get Rich Sample Product Review Dataset")
async def get_sample_shopee_data():
    """Returns realistic pre-generated sample dataset for testing without running live browser"""
    sample_file = os.path.join(FRONTEND_DIR, "sample_shopee_reviews.json")
    if os.path.exists(sample_file):
        with open(sample_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="application/json; charset=utf-8")
    return JSONResponse(content={
        "product_info": {
            "title": "Bàn Phím Cơ Không Dây Machenike K500 Tri-Mode",
            "price": "650.000 ₫",
            "rating_score": "4.9",
            "total_reviews": 1280,
            "url": "https://shopee.vn/product/123456/7891011"
        },
        "total_scraped_reviews": 0,
        "comments": []
    })

# ==========================================
# 4. SPATIAL DASHBOARD & ENTITIES
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>Index file not found</h1>", status_code=404)

@app.get("/api/stats")
async def get_stats():
    return db.get_stats()

@app.get("/api/umkm")
async def get_umkm_list(
    city: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(100),
    offset: int = Query(0)
):
    return db.get_umkm_list(category=category, city=city, search=search, limit=limit, offset=offset)

@app.get("/api/umkm/{umkm_id}")
async def get_umkm_detail(umkm_id: int):
    detail = db.get_umkm_by_id(umkm_id)
    if not detail:
        raise HTTPException(status_code=404, detail="UMKM not found")
    return detail

@app.get("/api/products")
async def get_products(limit: int = Query(100)):
    return db.get_all_products(limit=limit)

@app.post("/api/purge")
async def purge_database():
    db.purge_all_data()
    return {"status": "success", "message": "Database berhasil dibersihkan total."}

@app.get("/api/export/geojson")
async def export_geojson():
    geojson_data = db.export_geojson()
    return JSONResponse(
        content=geojson_data,
        headers={"Content-Disposition": "attachment; filename=umkm_geospatial_data.geojson"}
    )

@app.get("/api/export/csv")
async def export_csv():
    df = db.export_csv_dataframe()
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    return StreamingResponse(
        io.BytesIO(stream.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=umkm_products_dataset.csv"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
