from dataclasses import dataclass

@dataclass
class Message:
    sender: str
    receiver: str
    content: str
    timestamp: int
