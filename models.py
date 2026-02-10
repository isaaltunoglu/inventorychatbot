"""Pydantic models for request/response schemas."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# --- Inventory ---

class InventoryItemCreate(BaseModel):
    item_name: str
    location: str
    quantity: int = 1


class InventoryItemUpdate(BaseModel):
    item_name: Optional[str] = None
    location: Optional[str] = None
    quantity: Optional[int] = None


class InventoryItem(BaseModel):
    id: int
    item_name: str
    location: str
    quantity: int
    last_updated: str


# --- Chat / NLU ---

class ChatRequest(BaseModel):
    message: str


class NLUResult(BaseModel):
    intent: str
    confidence: float
    entities: dict
    normalized_text: str


class ChatResponse(BaseModel):
    reply: str
    nlu: Optional[NLUResult] = None
    data: Optional[list] = None
