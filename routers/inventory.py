"""Inventory REST API endpoints."""
from fastapi import APIRouter, HTTPException
from models import InventoryItemCreate, InventoryItemUpdate, InventoryItem
import database

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("/", response_model=list[InventoryItem])
async def list_items():
    """List all inventory items."""
    items = await database.get_all_items()
    return items


@router.post("/", response_model=InventoryItem, status_code=201)
async def create_item(item: InventoryItemCreate):
    """Add a new item to the inventory."""
    new_item = await database.add_item(
        item_name=item.item_name,
        location=item.location,
        quantity=item.quantity,
    )
    return new_item


@router.get("/search")
async def search_items(q: str = ""):
    """Search items by name or location."""
    if not q:
        return []
    items = await database.search_items(q)
    return items


@router.put("/{item_id}", response_model=InventoryItem)
async def update_item(item_id: int, item: InventoryItemUpdate):
    """Update an inventory item."""
    updated = await database.update_item(
        item_id=item_id,
        item_name=item.item_name,
        location=item.location,
        quantity=item.quantity,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    return updated


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    """Delete an inventory item."""
    deleted = await database.delete_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ürün bulunamadı")
    return {"message": "Ürün silindi", "id": item_id}
