from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Post:
    id: str
    author: str
    content: str
    timestamp: int
    comments: Optional[List] = None
    revoked: bool = False
