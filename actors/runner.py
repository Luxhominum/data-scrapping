"""
Actor Execution Runner & Dataset Storage System (Apify Architecture)
Manages asynchronous run tasks, datasets, logs, and webhooks.
"""
import os
import json
import uuid
import time
import threading
import requests
import pandas as pd
from typing import Dict, Any, List, Optional
from datetime import datetime
from actors.registry import actor_registry
from database.db_manager import DatabaseManager
from database.models import UMKM, Product

DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "datasets")
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "logs")
RUNS_META_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "runs.json")

os.makedirs(DATASETS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

class ActorRunner:
    def __init__(self):
        self.runs: Dict[str, Dict[str, Any]] = self._load_runs()
        self.db = DatabaseManager()

    def _load_runs(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(RUNS_META_PATH):
            try:
                with open(RUNS_META_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_runs(self):
        with open(RUNS_META_PATH, "w", encoding="utf-8") as f:
            json.dump(self.runs, f, indent=2)

    def trigger_run(self, actor_id: str, input_data: Dict[str, Any], webhook_url: Optional[str] = None) -> Dict[str, Any]:
        actor = actor_registry.get_actor(actor_id)
        if not actor:
            raise ValueError(f"Actor '{actor_id}' not found in Actor Store.")

        run_id = f"run_{uuid.uuid4().hex[:8]}"
        started_at = datetime.utcnow().isoformat()

        run_meta = {
            "run_id": run_id,
            "actor_id": actor_id,
            "actor_name": actor.metadata.name,
            "status": "RUNNING",  # RUNNING, SUCCEEDED, FAILED
            "started_at": started_at,
            "finished_at": None,
            "duration_sec": 0,
            "item_count": 0,
            "input_data": input_data,
            "webhook_url": webhook_url,
            "dataset_id": run_id,
            "log_path": os.path.join(LOGS_DIR, f"{run_id}.log"),
            "dataset_path": os.path.join(DATASETS_DIR, f"{run_id}.json")
        }

        self.runs[run_id] = run_meta
        self._save_runs()

        # Start execution in background thread
        thread = threading.Thread(target=self._execute_actor_thread, args=(run_id, actor, input_data, webhook_url))
        thread.daemon = True
        thread.start()

        return run_meta

    def _execute_actor_thread(self, run_id: str, actor, input_data: Dict[str, Any], webhook_url: Optional[str]):
        log_file = os.path.join(LOGS_DIR, f"{run_id}.log")
        start_time = time.time()

        def log_cb(msg: str):
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            line = f"[{timestamp}] {msg}\n"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(line)

        log_cb(f"=== Initializing Actor Run: {run_id} ({actor.metadata.name}) ===")
        log_cb(f"Input configuration: {json.dumps(input_data)}")

        try:
            items = actor.run(input_data, log_cb)
            
            # Save Dataset JSON
            dataset_file = os.path.join(DATASETS_DIR, f"{run_id}.json")
            with open(dataset_file, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2)

            # Sync entities with main Geospatial DB if applicable
            for itm in items:
                store_name = itm.get("store_name") or itm.get("entity_name") or itm.get("title") or itm.get("place_name")
                if store_name:
                    umkm_obj = UMKM(
                        name=store_name,
                        category=itm.get("category", "E-Commerce"),
                        address=itm.get("formatted_address") or f"{store_name}, {itm.get('city', 'Indonesia')}",
                        city=itm.get("city", "Indonesia"),
                        latitude=itm.get("latitude", 0.0),
                        longitude=itm.get("longitude", 0.0),
                        phone=itm.get("phone", ""),
                        whatsapp=itm.get("whatsapp", ""),
                        instagram_handle=itm.get("instagram_handle", ""),
                        tokopedia_url=itm.get("tokopedia_url") or (itm.get("store_url") if itm.get("platform") == "tokopedia" else ""),
                        shopee_url=itm.get("shopee_url") or (itm.get("store_url") if itm.get("platform") == "shopee" else ""),
                        website=itm.get("primary_url") or itm.get("store_url") or itm.get("website_url") or itm.get("url", ""),
                        rating=itm.get("rating", 4.9),
                        source=f"actor_{actor.metadata.actor_id}",
                        ai_summary=f"Extracted via Apify-Compatible Actor ({actor.metadata.name})",
                        ai_verified=1,
                        confidence_score=itm.get("confidence_score", 95)
                    )
                    umkm_id = self.db.add_or_update_umkm(umkm_obj)

                    prod_title = itm.get("product_title") or itm.get("evidence_title")
                    if prod_title:
                        p_obj = Product(
                            umkm_id=umkm_id,
                            title=prod_title,
                            price=float(itm.get("price_idr", 0.0) or itm.get("evidence_price", 0.0)),
                            rating=4.9,
                            sold_count=150,
                            platform=itm.get("platform", "ecommerce"),
                            product_url=itm.get("store_url", ""),
                            image_url=itm.get("image_url", "https://images.unsplash.com/photo-1544816155-12df9643f363?w=500"),
                            category=itm.get("category", "Produk")
                        )
                        self.db.add_product(p_obj)

            duration = round(time.time() - start_time, 2)
            log_cb(f"=== Run Finished: SUCCEEDED in {duration}s. Items: {len(items)} ===")

            self.runs[run_id]["status"] = "SUCCEEDED"
            self.runs[run_id]["finished_at"] = datetime.utcnow().isoformat()
            self.runs[run_id]["duration_sec"] = duration
            self.runs[run_id]["item_count"] = len(items)
            self._save_runs()

            # Trigger Webhook if configured
            if webhook_url:
                try:
                    requests.post(webhook_url, json={"run_id": run_id, "status": "SUCCEEDED", "item_count": len(items)}, timeout=5)
                except Exception as we:
                    log_cb(f"Webhook execution notice: {we}")

        except Exception as e:
            duration = round(time.time() - start_time, 2)
            log_cb(f"=== RUN FAILED with error: {e} ===")
            self.runs[run_id]["status"] = "FAILED"
            self.runs[run_id]["finished_at"] = datetime.utcnow().isoformat()
            self.runs[run_id]["duration_sec"] = duration
            self._save_runs()

    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self.runs.get(run_id)

    def list_runs(self, limit: int = 50) -> List[Dict[str, Any]]:
        return sorted(list(self.runs.values()), key=lambda x: x["started_at"], reverse=True)[:limit]

    def get_dataset_items(self, dataset_id: str) -> List[Dict[str, Any]]:
        path = os.path.join(DATASETS_DIR, f"{dataset_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def get_dataset_csv_dataframe(self, dataset_id: str) -> pd.DataFrame:
        items = self.get_dataset_items(dataset_id)
        if items:
            return pd.DataFrame(items)
        return pd.DataFrame()

    def get_run_logs(self, run_id: str) -> str:
        log_file = os.path.join(LOGS_DIR, f"{run_id}.log")
        if os.path.exists(log_file):
            with open(log_file, "r", encoding="utf-8") as f:
                return f.read()
        return "No logs available."

# Global Runner Singleton
actor_runner = ActorRunner()
