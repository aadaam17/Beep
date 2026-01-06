from dataclasses import dataclass
from typing import List

@dataclass
class Room:
    name: str
    members: List[str]
    type: str = "public"
