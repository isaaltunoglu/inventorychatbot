"""Application configuration."""
import os

# Database
DATABASE_PATH = os.getenv("DATABASE_PATH", "inventory.db")

# NLU Models (Hugging Face)
INTENT_MODEL = "dbmdz/distilbert-base-turkish-cased"
NER_MODEL = "akdeniz27/bert-base-turkish-cased-ner"

# Intent labels for zero-shot classification
INTENT_LABELS = {
    "add_item": ["ürün ekle", "envantere ekle", "ekle", "koy", "yerleştir", "kaydet"],
    "remove_item": ["sil", "kaldır", "çıkar", "ürün sil"],
    "query_location": ["nerede", "konumu", "yeri", "bul", "ara"],
    "list_items": ["listele", "göster", "hepsini göster", "envanter"],
    "update_quantity": ["güncelle", "miktar değiştir", "adet güncelle", "sayı değiştir"],
}

# Zero-shot candidate labels (Turkish)
ZERO_SHOT_LABELS = [
    "ürün ekleme",
    "ürün silme",
    "konum sorgulama",
    "envanter listeleme",
    "miktar güncelleme",
]

# Mapping from zero-shot label to intent key
LABEL_TO_INTENT = {
    "ürün ekleme": "add_item",
    "ürün silme": "remove_item",
    "konum sorgulama": "query_location",
    "envanter listeleme": "list_items",
    "miktar güncelleme": "update_quantity",
}

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
