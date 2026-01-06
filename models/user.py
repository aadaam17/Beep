from dataclasses import dataclass
from typing import List

@dataclass
class User:
    username: str
    followers: List[str]
    following: List[str]
