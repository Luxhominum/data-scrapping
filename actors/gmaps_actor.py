"""
Google Maps & Geospatial Places Actor
Extracts verified local store coordinates, physical addresses, and contact phone numbers.
"""
import time
from typing import Dict, Any, List, Callable
from actors.base_actor import BaseActor, ActorMetadata
from scraper.real_web_scraper import RealWebScraper
from scraper.osint_engine import OSINTEngine

class GoogleMapsActor(BaseActor):
    def __init__(self):
        metadata = ActorMetadata(
            actor_id="google-maps-scraper",
            name="Google Maps Places & Geolocation Extractor",
            description="Extracts local business listings, physical street addresses, exact GPS coordinates, and phone numbers.",
            version="1.1.0",
            category="Geospatial",
            icon="map-pin",
            input_schema={
                "location_query": {
                    "type": "string",
                    "title": "Business & Location Query",
                    "description": "Store type and city (e.g. Toko Batik Solo, Kafe Kopi Bandung)",
                    "required": True,
                    "default": "Toko Kopi Bandung"
                },
                "max_items": {
                    "type": "integer",
                    "title": "Max Places",
                    "description": "Maximum number of places to geolocate",
                    "required": False,
                    "default": 3
                }
            }
        )
        super().__init__(metadata)
        self.osint = OSINTEngine()
        self.web_scraper = RealWebScraper()

    def run(self, input_data: Dict[str, Any], log_cb: Callable[[str], None]) -> List[Dict[str, Any]]:
        query = input_data.get("location_query", "").strip()
        max_items = int(input_data.get("max_items", 3))

        log_cb(f"Starting Google Maps Geospatial Actor for: '{query}'...")
        dork_query = f'site:google.com/maps/place "{query}"'
        hits = self.osint.execute_dork(dork_query, limit=max_items * 2)

        if not hits:
            hits = self.osint.execute_dork(f'"{query}" maps OR alamat OR telepon', limit=max_items)

        log_cb(f"Discovered {len(hits)} matching place references on live web.")

        results = []
        for hit in hits[:max_items]:
            target_url = hit["url"]
            log_cb(f"Geocoding and extracting place metadata from {target_url}...")
            parsed = self.web_scraper.scrape_single_url(target_url)
            if parsed:
                umkm, prods = parsed
                item = {
                    "platform": "google_maps",
                    "place_name": umkm.name,
                    "formatted_address": umkm.address,
                    "city": umkm.city,
                    "latitude": umkm.latitude,
                    "longitude": umkm.longitude,
                    "phone": umkm.phone,
                    "rating": umkm.rating,
                    "website_url": target_url,
                    "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                }
                results.append(item)
                log_cb(f"[GEOLOCATED] {umkm.name} -> LAT: {umkm.latitude:.4f}, LNG: {umkm.longitude:.4f}")
            time.sleep(0.3)

        log_cb(f"Google Maps Actor completed. Extracted {len(results)} geolocated places.")
        return results
