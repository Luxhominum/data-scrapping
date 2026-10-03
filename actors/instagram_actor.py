"""
Instagram Profile & Social Commerce Actor
Extracts live Instagram business bios, follower handles, WhatsApp contacts, and Linktree hubs.
"""
import time
from typing import Dict, Any, List, Callable
from actors.base_actor import BaseActor, ActorMetadata
from scraper.real_web_scraper import RealWebScraper
from scraper.osint_engine import OSINTEngine

class InstagramActor(BaseActor):
    def __init__(self):
        metadata = ActorMetadata(
            actor_id="instagram-scraper",
            name="Instagram Business & Contact Extractor",
            description="Extracts Instagram profiles, bio contact numbers, WhatsApp links, and bio hubs for Indonesian UMKM.",
            version="1.3.0",
            category="Social Media",
            icon="instagram",
            input_schema={
                "search_query": {
                    "type": "string",
                    "title": "Brand / Niche Keyword",
                    "description": "Instagram business query (e.g. Batik Solo, Kopi Susu Jakarta)",
                    "required": True,
                    "default": "Bakpia Tugu Jogja"
                },
                "max_items": {
                    "type": "integer",
                    "title": "Max Profiles",
                    "description": "Maximum number of profiles to extract",
                    "required": False,
                    "default": 3
                }
            }
        )
        super().__init__(metadata)
        self.osint = OSINTEngine()
        self.web_scraper = RealWebScraper()

    def run(self, input_data: Dict[str, Any], log_cb: Callable[[str], None]) -> List[Dict[str, Any]]:
        query = input_data.get("search_query", "").strip()
        max_items = int(input_data.get("max_items", 3))

        log_cb(f"Executing Instagram Bio Dorking Actor for: '{query}'...")
        dork_query = f'site:instagram.com "{query}" ("wa.me" OR "08" OR "linktr.ee" OR "bit.ly")'
        
        hits = self.osint.execute_dork(dork_query, limit=max_items * 2)
        log_cb(f"Discovered {len(hits)} matching Instagram business profiles.")

        results = []
        for hit in hits[:max_items]:
            target_url = hit["url"]
            log_cb(f"Crawling Instagram profile & bio text: {target_url}...")
            parsed = self.web_scraper.scrape_single_url(target_url)
            if parsed:
                umkm, prods = parsed
                item = {
                    "platform": "instagram",
                    "profile_name": umkm.name,
                    "instagram_handle": umkm.instagram_handle,
                    "city": umkm.city,
                    "latitude": umkm.latitude,
                    "longitude": umkm.longitude,
                    "whatsapp": umkm.whatsapp,
                    "profile_url": target_url,
                    "bio_summary": umkm.ai_summary,
                    "avatar_url": prods[0].image_url if prods else "",
                    "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                results.append(item)
                log_cb(f"[PARSED] @{umkm.instagram_handle} | WhatsApp: {umkm.whatsapp or 'N/A'}")
            time.sleep(0.3)

        log_cb(f"Instagram Actor finished. Extracted {len(results)} profile dossiers.")
        return results
