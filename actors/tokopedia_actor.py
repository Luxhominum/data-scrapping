"""
Tokopedia Live Scraper Actor
Extracts authentic Tokopedia storefronts, products, live prices, ratings, and store cities.
"""
import time
from typing import Dict, Any, List, Callable
from actors.base_actor import BaseActor, ActorMetadata
from scraper.real_web_scraper import RealWebScraper
from scraper.osint_engine import OSINTEngine

class TokopediaActor(BaseActor):
    def __init__(self):
        metadata = ActorMetadata(
            actor_id="tokopedia-scraper",
            name="Tokopedia Store & Product Scraper",
            description="Scrapes live Tokopedia stores, official merchants, product catalogs, prices, ratings, and store locations.",
            version="1.2.0",
            category="E-Commerce",
            icon="shopping-cart",
            input_schema={
                "search_query": {
                    "type": "string",
                    "title": "Search Query / Store Name",
                    "description": "Keyword to search on Tokopedia (e.g. Batik Danar Hadi, Kopi Gayo)",
                    "required": True,
                    "default": "Batik Solo"
                },
                "max_items": {
                    "type": "integer",
                    "title": "Max Items",
                    "description": "Maximum number of store entities to extract",
                    "required": False,
                    "default": 4
                },
                "extract_contacts": {
                    "type": "boolean",
                    "title": "Extract WhatsApp & Contacts",
                    "description": "Attempt to detect verified WhatsApp numbers and phone channels",
                    "required": False,
                    "default": True
                }
            }
        )
        super().__init__(metadata)
        self.osint = OSINTEngine()
        self.web_scraper = RealWebScraper()

    def run(self, input_data: Dict[str, Any], log_cb: Callable[[str], None]) -> List[Dict[str, Any]]:
        query = input_data.get("search_query", "").strip()
        max_items = int(input_data.get("max_items", 4))
        
        log_cb(f"Starting Tokopedia Scraper Actor for query: '{query}' (Target Max: {max_items})...")
        dork_query = f'site:tokopedia.com "{query}" ("official store" OR "power merchant" OR "terjual" OR "kota")'
        
        log_cb(f"Executing marketplace dork operator: {dork_query}")
        hits = self.osint.execute_dork(dork_query, limit=max_items * 2)
        log_cb(f"Discovered {len(hits)} matching Tokopedia store URLs on live web.")

        results = []
        for hit in hits[:max_items]:
            target_url = hit["url"]
            log_cb(f"Crawling live Tokopedia storefront: {target_url}...")
            parsed = self.web_scraper.scrape_single_url(target_url)
            if parsed:
                umkm, prods = parsed
                p = prods[0] if prods else None
                item = {
                    "platform": "tokopedia",
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
                log_cb(f"[PARSED] {umkm.name} ({umkm.city}) | Price: Rp {p.price if p else 0:,.0f}")
            time.sleep(0.3)

        log_cb(f"Tokopedia Actor completed successfully. Extracted {len(results)} structured store items.")
        return results
