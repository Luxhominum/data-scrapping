"""
Database Models for UMKM & Product Geospatial Intelligence with AI Agent Enrichment
"""
from dataclasses import dataclass, asdict
from typing import Optional, List
import json
from datetime import datetime

@dataclass
class UMKM:
    id: Optional[int] = None
    name: str = ""
    category: str = "Umum"
    address: str = ""
    city: str = ""
    province: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    phone: str = ""
    whatsapp: str = ""
    instagram_handle: str = ""
    tokopedia_url: str = ""
    shopee_url: str = ""
    website: str = ""
    rating: float = 0.0
    reviews_count: int = 0
    source: str = "manual"  # gmaps, instagram, marketplace, ai_agent, seed
    ai_summary: str = ""
    ai_verified: int = 0  # 1 if verified by AI agent / OSINT, 0 otherwise
    confidence_score: int = 85  # 0 - 100
    digital_footprint: str = "{}"  # JSON string of discovered OSINT vectors
    created_at: str = datetime.utcnow().isoformat()

    def to_dict(self):
        return asdict(self)


@dataclass
class Product:
    id: Optional[int] = None
    umkm_id: Optional[int] = None
    title: str = ""
    price: float = 0.0
    original_price: float = 0.0
    rating: float = 0.0
    sold_count: int = 0
    platform: str = "tokopedia"  # tokopedia, shopee, instagram
    product_url: str = ""
    image_url: str = ""
    category: str = ""
    description: str = ""
    updated_at: str = datetime.utcnow().isoformat()

    def to_dict(self):
        return asdict(self)


@dataclass
class ScrapeJob:
    id: Optional[int] = None
    source: str = ""
    query: str = ""
    status: str = "pending"  # pending, running, completed, failed
    items_count: int = 0
    error_message: str = ""
    created_at: str = datetime.utcnow().isoformat()

    def to_dict(self):
        return asdict(self)
