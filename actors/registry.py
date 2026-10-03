"""
Actor Store Registry
Central catalog of all available modular scrapers/actors.
"""
from typing import Dict, List, Optional
from actors.base_actor import BaseActor
from actors.tokopedia_actor import TokopediaActor
from actors.shopee_actor import ShopeeActor
from actors.shopee_review_actor import ShopeeReviewActor
from actors.instagram_actor import InstagramActor
from actors.gmaps_actor import GoogleMapsActor
from actors.osint_actor import OSINTReconActor, GenericCrawlerActor

class ActorRegistry:
    def __init__(self):
        self._actors: Dict[str, BaseActor] = {}
        self._register_default_actors()

    def _register_default_actors(self):
        actors = [
            TokopediaActor(),
            ShopeeActor(),
            ShopeeReviewActor(),
            InstagramActor(),
            GoogleMapsActor(),
            OSINTReconActor(),
            GenericCrawlerActor()
        ]
        for a in actors:
            self._actors[a.metadata.actor_id] = a

    def get_actor(self, actor_id: str) -> Optional[BaseActor]:
        return self._actors.get(actor_id)

    def list_actors(self) -> List[Dict]:
        return [a.metadata.to_dict() for a in self._actors.values()]

# Global Singleton Registry
actor_registry = ActorRegistry()
