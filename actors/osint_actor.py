"""
OSINT Multi-Vector Reconnaissance Actor & Generic Web Crawler Actor
"""
import time
from typing import Dict, Any, List, Callable
from actors.base_actor import BaseActor, ActorMetadata
from scraper.real_web_scraper import RealWebScraper
from scraper.osint_engine import OSINTEngine

class OSINTReconActor(BaseActor):
    def __init__(self):
        metadata = ActorMetadata(
            actor_id="osint-recon-actor",
            name="OSINT Multi-Vector Reconnaissance Actor",
            description="Executes automated 5-vector dorking, Linktree/bio-hub unrolling, WhatsApp contact correlation, and Target Dossier synthesis.",
            version="2.0.0",
            category="OSINT Intelligence",
            icon="shield",
            input_schema={
                "target_entity": {
                    "type": "string",
                    "title": "Target Brand / Entity Name",
                    "description": "Brand name or business entity to investigate (e.g. Danar Hadi Solo, Kopi Aroma Bandung)",
                    "required": True,
                    "default": "Danar Hadi Solo"
                },
                "location_hint": {
                    "type": "string",
                    "title": "City / Location Hint",
                    "description": "Optional Indonesian city filter",
                    "required": False,
                    "default": "Solo"
                }
            }
        )
        super().__init__(metadata)
        self.osint = OSINTEngine()

    def run(self, input_data: Dict[str, Any], log_cb: Callable[[str], None]) -> List[Dict[str, Any]]:
        target = input_data.get("target_entity", "").strip()
        location = input_data.get("location_hint", "").strip()

        log_cb(f"Starting OSINT Multi-Vector Reconnaissance on Target: '{target}' ({location or 'Indonesia'})...")
        log_cb("Vektor 1: Instagram Bio Links & Verified Contacts...")
        log_cb("Vektor 2: Bio Link Hubs (Linktree / Desty / Biolinky)...")
        log_cb("Vektor 3: Tokopedia & Shopee Storefronts...")
        log_cb("Vektor 4: Geolocation Triangulation...")

        pairs = self.osint.run_multi_vector_recon(target, location)
        log_cb(f"OSINT Recon completed. Correlated {len(pairs)} target nodes.")

        results = []
        for umkm, prods in pairs:
            p = prods[0] if prods else None
            item = {
                "platform": "osint_target_dossier",
                "entity_name": umkm.name,
                "category": umkm.category,
                "city": umkm.city,
                "latitude": umkm.latitude,
                "longitude": umkm.longitude,
                "phone": umkm.phone,
                "whatsapp": umkm.whatsapp,
                "instagram_handle": umkm.instagram_handle,
                "tokopedia_url": umkm.tokopedia_url,
                "shopee_url": umkm.shopee_url,
                "primary_url": umkm.website,
                "confidence_score": umkm.confidence_score,
                "digital_footprint": umkm.digital_footprint,
                "evidence_price": p.price if p else 0.0,
                "evidence_title": p.title if p else "",
                "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            results.append(item)
            log_cb(f"[DOSSIER SYNTHESIZED] {umkm.name} | Confidence: {umkm.confidence_score}% | WA: {umkm.whatsapp or 'N/A'}")

        return results


class GenericCrawlerActor(BaseActor):
    def __init__(self):
        metadata = ActorMetadata(
            actor_id="generic-web-crawler",
            name="Generic Web Page & DOM Scraper",
            description="Crawls arbitrary destination URLs live over HTTP, extracting OpenGraph metadata, text, contact links, and price tags.",
            version="1.0.0",
            category="Web Scraping",
            icon="globe",
            input_schema={
                "start_urls": {
                    "type": "string",
                    "title": "Start URLs (One per line)",
                    "description": "List of direct URLs to crawl (e.g. https://tokopedia.com/danarhadi)",
                    "required": True,
                    "default": "https://tokopedia.com/danarhadi"
                }
            }
        )
        super().__init__(metadata)
        self.web_scraper = RealWebScraper()

    def run(self, input_data: Dict[str, Any], log_cb: Callable[[str], None]) -> List[Dict[str, Any]]:
        raw_urls = input_data.get("start_urls", "")
        urls = [u.strip() for u in raw_urls.split("\n") if u.strip().startswith("http")]

        log_cb(f"Starting Generic Web Crawler on {len(urls)} target URLs...")
        results = []

        for u in urls:
            log_cb(f"Visiting URL: {u}...")
            parsed = self.web_scraper.scrape_single_url(u)
            if parsed:
                umkm, prods = parsed
                p = prods[0] if prods else None
                item = {
                    "platform": "generic_web",
                    "title": umkm.name,
                    "url": u,
                    "city": umkm.city,
                    "whatsapp": umkm.whatsapp,
                    "price_idr": p.price if p else 0.0,
                    "image_url": p.image_url if p else "",
                    "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                results.append(item)
                log_cb(f"[EXTRACTED] {umkm.name} | Price: Rp {p.price if p else 0:,.0f}")
            time.sleep(0.3)

        log_cb(f"Crawler finished. Total items extracted: {len(results)}")
        return results
