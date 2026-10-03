"""
Shopee Live Scraper Actor
Extracts authentic Shopee storefronts, products, live prices, ratings, and store cities.
"""
import time
from typing import Dict, Any, List, Callable
from actors.base_actor import BaseActor, ActorMetadata
from scraper.real_web_scraper import RealWebScraper
from scraper.osint_engine import OSINTEngine

class ShopeeActor(BaseActor):
    def __init__(self):
        metadata = ActorMetadata(
            actor_id="shopee-scraper",
            name="Shopee Storefront & Product Extractor",
            description="Extracts Shopee star merchants, product catalogs, pricing evidence, and Indonesian seller profiles.",
            version="1.1.0",
            category="E-Commerce",
            icon="shopping-bag",
            input_schema={
                "search_query": {
                    "type": "string",
                    "title": "Search Query / Keyword",
                    "description": "Product or brand keyword on Shopee Indonesia (e.g. Sambal Bu Rudy, Kerajinan Rotan)",
                    "required": True,
                    "default": "Kopi Aroma Bandung"
                },
                "max_items": {
                    "type": "integer",
                    "title": "Max Items",
                    "description": "Maximum number of items to scrape",
                    "required": False,
                    "default": 4
                }
            }
        )
        super().__init__(metadata)
        self.osint = OSINTEngine()
        self.web_scraper = RealWebScraper()

    def run(self, input_data: Dict[str, Any], log_cb: Callable[[str], None]) -> List[Dict[str, Any]]:
        query = input_data.get("search_query", "").strip()
        max_items = int(input_data.get("max_items", 4))

        log_cb(f"Starting Shopee Scraper Actor for query: '{query}'...")
        dork_query = f'site:shopee.co.id "{query}"'
        
        log_cb(f"Executing Shopee dork: {dork_query}")
        hits = self.osint.execute_dork(dork_query, limit=max_items * 2)
        log_cb(f"Discovered {len(hits)} matching Shopee URLs.")

        results = []
        for hit in hits[:max_items]:
            target_url = hit["url"]
            log_cb(f"Crawling Shopee store page: {target_url}...")
            parsed = self.web_scraper.scrape_single_url(target_url)
            if parsed:
                umkm, prods = parsed
                p = prods[0] if prods else None
                item = {
                    "platform": "shopee",
                    "store_name": umkm.name,
                    "category": umkm.category,
                    "city": umkm.city,
                    "latitude": umkm.latitude,
                    "longitude": umkm.longitude,
                    "phone": umkm.phone,
                    "whatsapp": umkm.whatsapp,
                    "store_url": target_url,
                    "product_title": p.title if p else "",
                    "price_idr": p.price if p else 0.0,
                    "rating": umkm.rating,
                    "reviews_count": umkm.reviews_count,
                    "image_url": p.image_url if p else "",
                    "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                results.append(item)
                log_cb(f"[PARSED] Shopee Merchant: {umkm.name} ({umkm.city})")
            time.sleep(0.3)

        log_cb(f"Shopee Actor completed. Total extracted: {len(results)} items.")
        return results
