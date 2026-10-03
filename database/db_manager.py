"""
Database Manager for UMKM, Product, and AI Agent Scraper Intelligence
"""
import sqlite3
import json
import os
from typing import List, Dict, Any, Optional
import pandas as pd
from database.models import UMKM, Product, ScrapeJob

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "umkm_data.db")
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "settings.json")

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # UMKM Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS umkm (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT DEFAULT 'Umum',
                address TEXT,
                city TEXT,
                province TEXT,
                latitude REAL DEFAULT 0.0,
                longitude REAL DEFAULT 0.0,
                phone TEXT,
                whatsapp TEXT,
                instagram_handle TEXT,
                tokopedia_url TEXT,
                shopee_url TEXT,
                website TEXT,
                rating REAL DEFAULT 0.0,
                reviews_count INTEGER DEFAULT 0,
                source TEXT DEFAULT 'manual',
                ai_summary TEXT DEFAULT '',
                ai_verified INTEGER DEFAULT 0,
                confidence_score INTEGER DEFAULT 85,
                created_at TEXT
            )
            """)

            # Auto-migrate columns if database already exists
            cursor.execute("PRAGMA table_info(umkm)")
            columns = [col[1] for col in cursor.fetchall()]
            if "ai_summary" not in columns:
                cursor.execute("ALTER TABLE umkm ADD COLUMN ai_summary TEXT DEFAULT ''")
            if "ai_verified" not in columns:
                cursor.execute("ALTER TABLE umkm ADD COLUMN ai_verified INTEGER DEFAULT 0")
            if "confidence_score" not in columns:
                cursor.execute("ALTER TABLE umkm ADD COLUMN confidence_score INTEGER DEFAULT 85")
            if "digital_footprint" not in columns:
                cursor.execute("ALTER TABLE umkm ADD COLUMN digital_footprint TEXT DEFAULT '{}'")

            # Products Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                umkm_id INTEGER,
                title TEXT NOT NULL,
                price REAL DEFAULT 0.0,
                original_price REAL DEFAULT 0.0,
                rating REAL DEFAULT 0.0,
                sold_count INTEGER DEFAULT 0,
                platform TEXT DEFAULT 'tokopedia',
                product_url TEXT,
                image_url TEXT,
                category TEXT,
                description TEXT,
                updated_at TEXT,
                FOREIGN KEY(umkm_id) REFERENCES umkm(id) ON DELETE CASCADE
            )
            """)

            # Scrape Jobs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS scrape_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                query TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                items_count INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TEXT
            )
            """)
            
            conn.commit()

    def get_settings(self) -> Dict[str, Any]:
        if os.path.exists(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "gemini_api_key": os.getenv("GEMINI_API_KEY", ""),
            "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
            "active_llm_provider": "gemini",
            "auto_ai_enrichment": True
        }

    def save_settings(self, settings: Dict[str, Any]):
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)

    def add_or_update_umkm(self, umkm: UMKM) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Check duplicate by name and city
            cursor.execute("SELECT id FROM umkm WHERE name = ? AND city = ?", (umkm.name, umkm.city))
            row = cursor.fetchone()
            if row:
                umkm_id = row["id"]
                cursor.execute("""
                UPDATE umkm SET
                    category = COALESCE(NULLIF(?, ''), category),
                    address = COALESCE(NULLIF(?, ''), address),
                    province = COALESCE(NULLIF(?, ''), province),
                    latitude = CASE WHEN ? != 0.0 THEN ? ELSE latitude END,
                    longitude = CASE WHEN ? != 0.0 THEN ? ELSE longitude END,
                    phone = COALESCE(NULLIF(?, ''), phone),
                    whatsapp = COALESCE(NULLIF(?, ''), whatsapp),
                    instagram_handle = COALESCE(NULLIF(?, ''), instagram_handle),
                    tokopedia_url = COALESCE(NULLIF(?, ''), tokopedia_url),
                    shopee_url = COALESCE(NULLIF(?, ''), shopee_url),
                    website = COALESCE(NULLIF(?, ''), website),
                    rating = CASE WHEN ? > 0 THEN ? ELSE rating END,
                    reviews_count = CASE WHEN ? > 0 THEN ? ELSE reviews_count END,
                    ai_summary = COALESCE(NULLIF(?, ''), ai_summary),
                    ai_verified = CASE WHEN ? = 1 THEN 1 ELSE ai_verified END,
                    confidence_score = CASE WHEN ? > 0 THEN ? ELSE confidence_score END,
                    digital_footprint = COALESCE(NULLIF(?, '{}'), digital_footprint)
                WHERE id = ?
                """, (
                    umkm.category, umkm.address, umkm.province,
                    umkm.latitude, umkm.latitude,
                    umkm.longitude, umkm.longitude,
                    umkm.phone, umkm.whatsapp, umkm.instagram_handle,
                    umkm.tokopedia_url, umkm.shopee_url, umkm.website,
                    umkm.rating, umkm.rating,
                    umkm.reviews_count, umkm.reviews_count,
                    umkm.ai_summary, umkm.ai_verified,
                    umkm.confidence_score, umkm.confidence_score,
                    umkm.digital_footprint,
                    umkm_id
                ))
            else:
                cursor.execute("""
                INSERT INTO umkm (name, category, address, city, province, latitude, longitude,
                                  phone, whatsapp, instagram_handle, tokopedia_url, shopee_url,
                                  website, rating, reviews_count, source, ai_summary, ai_verified,
                                  confidence_score, digital_footprint, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    umkm.name, umkm.category, umkm.address, umkm.city, umkm.province,
                    umkm.latitude, umkm.longitude, umkm.phone, umkm.whatsapp,
                    umkm.instagram_handle, umkm.tokopedia_url, umkm.shopee_url,
                    umkm.website, umkm.rating, umkm.reviews_count, umkm.source,
                    umkm.ai_summary, umkm.ai_verified, umkm.confidence_score,
                    umkm.digital_footprint, umkm.created_at
                ))
                umkm_id = cursor.lastrowid
            conn.commit()
            return umkm_id

    def add_product(self, product: Product) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM products WHERE umkm_id = ? AND title = ?", (product.umkm_id, product.title))
            row = cursor.fetchone()
            if row:
                prod_id = row["id"]
                cursor.execute("""
                UPDATE products SET
                    price = ?, original_price = ?, rating = ?, sold_count = ?,
                    platform = ?, product_url = ?, image_url = ?, updated_at = ?
                WHERE id = ?
                """, (
                    product.price, product.original_price, product.rating, product.sold_count,
                    product.platform, product.product_url, product.image_url, product.updated_at,
                    prod_id
                ))
            else:
                cursor.execute("""
                INSERT INTO products (umkm_id, title, price, original_price, rating, sold_count,
                                      platform, product_url, image_url, category, description, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product.umkm_id, product.title, product.price, product.original_price,
                    product.rating, product.sold_count, product.platform, product.product_url,
                    product.image_url, product.category, product.description, product.updated_at
                ))
                prod_id = cursor.lastrowid
            conn.commit()
            return prod_id

    def get_umkm_list(self, category: Optional[str] = None, city: Optional[str] = None,
                      search: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM umkm WHERE 1=1"
            params = []

            if category and category.lower() != "all":
                query += " AND category LIKE ?"
                params.append(f"%{category}%")

            if city and city.lower() != "all":
                query += " AND (city LIKE ? OR province LIKE ?)"
                params.extend([f"%{city}%", f"%{city}%"])

            if search:
                query += " AND (name LIKE ? OR address LIKE ? OR category LIKE ? OR ai_summary LIKE ?)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param, search_param])

            query += " ORDER BY ai_verified DESC, rating DESC, id DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                item = dict(row)
                cursor.execute("SELECT COUNT(*) as cnt, MIN(price) as min_p, MAX(price) as max_p FROM products WHERE umkm_id = ?", (item["id"],))
                stats = cursor.fetchone()
                item["product_count"] = stats["cnt"] if stats else 0
                item["min_price"] = stats["min_p"] or 0
                item["max_price"] = stats["max_p"] or 0
                result.append(item)
            return result

    def get_umkm_by_id(self, umkm_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM umkm WHERE id = ?", (umkm_id,))
            row = cursor.fetchone()
            if not row:
                return None
            umkm_dict = dict(row)
            cursor.execute("SELECT * FROM products WHERE umkm_id = ? ORDER BY sold_count DESC", (umkm_id,))
            products = [dict(p) for p in cursor.fetchall()]
            umkm_dict["products"] = products
            return umkm_dict

    def get_all_products(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT p.*, u.name as umkm_name, u.city as umkm_city, u.whatsapp as umkm_whatsapp, u.ai_verified, u.confidence_score
            FROM products p
            JOIN umkm u ON p.umkm_id = u.id
            ORDER BY p.sold_count DESC, p.id DESC
            LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as total_umkm FROM umkm")
            total_umkm = cursor.fetchone()["total_umkm"]

            cursor.execute("SELECT COUNT(*) as total_ai FROM umkm WHERE ai_verified = 1")
            total_ai = cursor.fetchone()["total_ai"]

            cursor.execute("SELECT COUNT(*) as total_products, AVG(price) as avg_price, SUM(sold_count) as total_sold FROM products")
            prod_stat = cursor.fetchone()

            cursor.execute("SELECT category, COUNT(*) as count FROM umkm GROUP BY category ORDER BY count DESC LIMIT 8")
            categories = [dict(r) for r in cursor.fetchall()]

            cursor.execute("SELECT city, COUNT(*) as count FROM umkm GROUP BY city ORDER BY count DESC LIMIT 8")
            cities = [dict(r) for r in cursor.fetchall()]

            return {
                "total_umkm": total_umkm,
                "total_ai_verified": total_ai,
                "total_products": prod_stat["total_products"] or 0,
                "avg_product_price": round(prod_stat["avg_price"] or 0),
                "total_sold_volume": prod_stat["total_sold"] or 0,
                "categories": categories,
                "cities": cities
            }

    def export_geojson(self) -> Dict[str, Any]:
        umkms = self.get_umkm_list(limit=1000)
        features = []
        for u in umkms:
            if u["latitude"] and u["longitude"]:
                features.append({
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [u["longitude"], u["latitude"]]
                    },
                    "properties": {
                        "id": u["id"],
                        "name": u["name"],
                        "category": u["category"],
                        "address": u["address"],
                        "city": u["city"],
                        "rating": u["rating"],
                        "whatsapp": u["whatsapp"],
                        "instagram": u["instagram_handle"],
                        "ai_verified": bool(u.get("ai_verified")),
                        "confidence_score": u.get("confidence_score", 85),
                        "ai_summary": u.get("ai_summary", ""),
                        "product_count": u.get("product_count", 0),
                        "tokopedia_url": u["tokopedia_url"],
                        "shopee_url": u["shopee_url"]
                    }
                })
        return {
            "type": "FeatureCollection",
            "features": features
        }

    def purge_all_data(self):
        """Purges all records from umkm, products, and scrape_jobs tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products")
            cursor.execute("DELETE FROM umkm")
            cursor.execute("DELETE FROM scrape_jobs")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('umkm', 'products', 'scrape_jobs')")
            conn.commit()

    def export_csv_dataframe(self) -> pd.DataFrame:
        with self.get_connection() as conn:
            query = """
            SELECT 
                u.id as umkm_id, u.name as umkm_name, u.category, u.address, u.city, u.province,
                u.latitude, u.longitude, u.phone, u.whatsapp, u.instagram_handle,
                u.ai_verified, u.confidence_score, u.ai_summary,
                p.id as product_id, p.title as product_title, p.price, p.rating as product_rating,
                p.sold_count, p.platform, p.product_url
            FROM umkm u
            LEFT JOIN products p ON u.id = p.umkm_id
            """
            return pd.read_sql_query(query, conn)
