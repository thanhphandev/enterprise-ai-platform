from pydantic import BaseModel
from typing import Optional, List

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"

class ChatResponse(BaseModel):
    reply: str

class UploadResponse(BaseModel):
    status: str
    filename: str
    chunks_indexed: int

class MessageItem(BaseModel):
    role: str
    content: str

class HistoryResponse(BaseModel):
    session_id: str
    history: List[MessageItem]
