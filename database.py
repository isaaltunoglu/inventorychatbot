"""SQLite database layer with async support."""
import aiosqlite
from config import DATABASE_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    location TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


async def get_db() -> aiosqlite.Connection:
    """Get a database connection."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db():
    """Initialize database schema."""
    db = await get_db()
    try:
        await db.executescript(SCHEMA)
        await db.commit()
    finally:
        await db.close()


async def add_item(item_name: str, location: str, quantity: int = 1) -> dict:
    """Add an item to the inventory."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO inventory (item_name, location, quantity) VALUES (?, ?, ?)",
            (item_name, location, quantity),
        )
        await db.commit()
        row = await db.execute("SELECT * FROM inventory WHERE id = ?", (cursor.lastrowid,))
        item = await row.fetchone()
        return dict(item)
    finally:
        await db.close()


async def get_all_items() -> list[dict]:
    """Get all inventory items."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM inventory ORDER BY last_updated DESC")
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def search_items(query: str) -> list[dict]:
    """Search items by name or location (case-insensitive, partial match)."""
    db = await get_db()
    try:
        like_query = f"%{query}%"
        cursor = await db.execute(
            "SELECT * FROM inventory WHERE item_name LIKE ? OR location LIKE ? ORDER BY last_updated DESC",
            (like_query, like_query),
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def update_item(item_id: int, item_name: str = None, location: str = None, quantity: int = None) -> dict | None:
    """Update an inventory item."""
    db = await get_db()
    try:
        updates = []
        params = []
        if item_name is not None:
            updates.append("item_name = ?")
            params.append(item_name)
        if location is not None:
            updates.append("location = ?")
            params.append(location)
        if quantity is not None:
            updates.append("quantity = ?")
            params.append(quantity)

        if not updates:
            return None

        updates.append("last_updated = CURRENT_TIMESTAMP")
        params.append(item_id)

        await db.execute(
            f"UPDATE inventory SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        await db.commit()

        cursor = await db.execute("SELECT * FROM inventory WHERE id = ?", (item_id,))
        item = await cursor.fetchone()
        return dict(item) if item else None
    finally:
        await db.close()


async def delete_item(item_id: int) -> bool:
    """Delete an inventory item. Returns True if deleted."""
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()
