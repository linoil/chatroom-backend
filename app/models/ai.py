from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    model: str
    messages: List[dict]
    stream: bool = True

