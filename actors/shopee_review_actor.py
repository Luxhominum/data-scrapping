"""
Shopee Product Review Actor
Extracts full review comments, star ratings, variations, and seller replies directly from a Shopee product URL.
"""
import os
import sys
import time
import json
import re
import datetime
from typing import Dict, Any, List, Callable
from urllib.parse import urlparse
from actors.base_actor import BaseActor, ActorMetadata

class ShopeeReviewActor(BaseActor):
    def __init__(self):
        metadata = ActorMetadata(
            actor_id="shopee-review-scraper",
            name="Shopee Product & Review Comment Extractor",
            description="Extracts all customer reviews, ratings, purchaser variations, attached media, and seller replies from any Shopee product URL.",
            version="1.2.0",
            category="E-Commerce Reviews",
            icon="star",
            input_schema={
                "product_url": {
                    "type": "string",
                    "title": "Shopee Product URL",
                    "description": "Full URL of the Shopee product (e.g. https://shopee.vn/product-name-i.12345.67890 or https://shopee.co.id/...)",
                    "required": True,
                    "default": ""
                },
                "review_limit": {
                    "type": "integer",
                    "title": "Review Limit",
                    "description": "Max number of reviews to extract (0 for all available)",
                    "required": False,
                    "default": 50
                },
                "all_star_types": {
                    "type": "boolean",
                    "title": "Categorize By Star Rating",
                    "description": "If enabled, extracts comments per star rating bucket (5★ down to 1★)",
                    "required": False,
                    "default": False
                },
                "star_limit_per_type": {
                    "type": "integer",
                    "title": "Limit Per Star Type",
                    "description": "Max reviews per star rating category (0 for all)",
                    "required": False,
                    "default": 10
                }
            }
        )
        super().__init__(metadata)

    def run(self, input_data: Dict[str, Any], log_cb: Callable[[str], None]) -> List[Dict[str, Any]]:
        url = input_data.get("product_url", "").strip()
        if not url:
            log_cb("[ERROR] No product URL provided.")
            raise ValueError("product_url is required.")

        review_limit = int(input_data.get("review_limit", 50))
        all_star_types = bool(input_data.get("all_star_types", False))
        star_limit_per_type = int(input_data.get("star_limit_per_type", 10))
        cookie_str = str(input_data.get("cookie_str", "")).strip()

        log_cb(f"Initializing Shopee Review Scraper for URL: {url}")
        log_cb(f"Configuration: limit={review_limit if review_limit > 0 else 'ALL'}, all_star_types={all_star_types}")

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        shopee_scraper_dir = os.path.join(base_dir, "shopee-scraper")
        if shopee_scraper_dir not in sys.path:
            sys.path.insert(0, shopee_scraper_dir)
            sys.path.insert(0, os.path.join(shopee_scraper_dir, "src"))

        # 1. Try Direct HTTP Extraction if cookie or cURL is provided
        if cookie_str:
            try:
                from curl_extractor import scrape_shopee_from_curl_or_cookie
                log_cb("Attempting lightning-fast direct HTTP review extraction using provided session headers/cookie...")
                direct_reviews = scrape_shopee_from_curl_or_cookie(
                    product_url=url,
                    curl_or_cookie=cookie_str,
                    review_limit=review_limit,
                    log_cb=log_cb
                )
                if direct_reviews:
                    log_cb(f"Successfully collected {len(direct_reviews)} customer reviews directly via HTTP API!")
                    return direct_reviews
                else:
                    log_cb("Direct extraction returned 0 reviews. Falling back to browser automation...")
            except Exception as e:
                log_cb(f"Direct extraction notice: {e}. Falling back to browser...")

        # 2. SeleniumBase CDP Automation Scraper (from toptankcpe/shopee-scraper engine)
        try:
            if shopee_scraper_dir not in sys.path:
                sys.path.insert(0, shopee_scraper_dir)
            from app.scraping.handlers.review_scraper import SeleniumBaseReviewScraper
            log_cb("Launching SeleniumBase UC CDP session with automatic anti-bot evasion...")
            
            scraper = SeleniumBaseReviewScraper(
                product_url=url,
                review_limit=review_limit,
                log_cb=log_cb
            )
            reviews = scraper.run()
            log_cb(f"Successfully collected {len(reviews)} customer reviews.")
            return reviews
        except Exception as e:
            log_cb(f"[ERROR] Scraper encountered an exception: {str(e)}")
            raise e
