"""
Base Actor Class for Apify-compatible Modular Scrapers
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field, asdict

@dataclass
class ActorMetadata:
    actor_id: str
    name: str
    description: str
    version: str = "1.0.0"
    category: str = "E-Commerce"
    icon: str = "shopping-bag"
    author: str = "PetaUMKM Core"
    input_schema: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)

class BaseActor(ABC):
    def __init__(self, metadata: ActorMetadata):
        self.metadata = metadata

    @abstractmethod
    def run(self, input_data: Dict[str, Any], log_cb: Callable[[str], None]) -> List[Dict[str, Any]]:
        """Executes the actor logic and yields scraped records"""
        pass
