"""Named Entity Recognition for Turkish text."""
import logging
from transformers import pipeline

logger = logging.getLogger(__name__)

_ner_pipeline = None


def _get_ner():
    """Lazy-load the Turkish NER pipeline."""
    global _ner_pipeline
    if _ner_pipeline is None:
        logger.info("Loading Turkish NER model (this may take a moment)...")
        _ner_pipeline = pipeline(
            "ner",
            model="akdeniz27/bert-base-turkish-cased-ner",
            aggregation_strategy="simple",
            device=-1,  # CPU
        )
        logger.info("Turkish NER model loaded.")
    return _ner_pipeline


def extract_entities(text: str) -> dict:
    """
    Extract named entities from Turkish text.

    Returns:
        dict with keys like:
            - item: str or None (detected product/item name)
            - location: str or None (detected location)
            - raw_entities: list of all detected entities
    """
    ner = _get_ner()
    results = ner(text)

    entities = {
        "item": None,
        "location": None,
        "raw_entities": [],
    }

    for entity in results:
        ent_info = {
            "word": entity["word"],
            "entity_group": entity["entity_group"],
            "score": round(entity["score"], 4),
        }
        entities["raw_entities"].append(ent_info)

        # Map NER labels to our schema
        group = entity["entity_group"]
        if group in ("PER", "ORG", "MISC") and entities["item"] is None:
            entities["item"] = entity["word"]
        elif group == "LOC" and entities["location"] is None:
            entities["location"] = entity["word"]

    return entities


def extract_item_and_location(text: str) -> dict:
    """
    Heuristic entity extraction for inventory commands.
    Falls back to pattern matching if NER doesn't find entities.

    Tries to extract:
        - item_name: the thing being added/searched
        - location: where it should go

    Common patterns:
        "X'i Y'e koy" -> item=X, location=Y
        "X ekle" -> item=X
        "X nerede" -> item=X
    """
    # First try NER
    ner_entities = extract_entities(text)

    item = ner_entities.get("item")
    location = ner_entities.get("location")

    # Fallback: simple heuristic parsing for common Turkish patterns
    if not item or not location:
        item_fb, loc_fb = _heuristic_parse(text)
        if not item:
            item = item_fb
        if not location:
            location = loc_fb

    return {
        "item": item,
        "location": location,
        "raw_entities": ner_entities.get("raw_entities", []),
    }


def _heuristic_parse(text: str) -> tuple:
    """
    Simple heuristic to extract item and location from Turkish commands.

    Patterns:
        "{item}'i/yı/yi/ını {location}'a/e/ya/ye koy/ekle/yerleştir"
        "{item} ekle"
        "{item} nerede"
    """
    import re

    text_lower = text.lower().strip()
    item = None
    location = None

    # Pattern: "X'yi/yı/ı/i Y'ye/ya/a/e koy/ekle/yerleştir/kaydet"
    # e.g., "Mavi dosyayı üst rafa koy"
    location_keywords = ["koy", "ekle", "yerleştir", "kaydet", "taşı"]
    for kw in location_keywords:
        if kw in text_lower:
            parts = text_lower.split(kw)[0].strip()
            # Try to split by accusative/dative suffixes
            # Look for the last word group before a dative suffix as location
            tokens = parts.split()
            if len(tokens) >= 2:
                # Find accusative split point
                for i, token in enumerate(tokens):
                    # Accusative suffixes: -ı, -i, -yı, -yi, -nı, -ni
                    if any(token.endswith(suf) for suf in ["ı", "i", "yı", "yi", "nı", "ni", "ını", "ini", "ünü", "unu"]):
                        item = " ".join(tokens[:i + 1])
                        # Rest before keyword is location
                        remaining = tokens[i + 1:]
                        if remaining:
                            location = " ".join(remaining)
                        break
                if not item:
                    # Fallback: first half is item, second half is location
                    mid = len(tokens) // 2
                    item = " ".join(tokens[:mid])
                    location = " ".join(tokens[mid:])
            elif len(tokens) == 1:
                item = tokens[0]
            break

    # Pattern: "X nerede" / "X nerede?"
    if not item:
        match = re.match(r"(.+?)\s+nerede", text_lower)
        if match:
            item = match.group(1).strip()

    # Pattern: "X ekle" (simple add)
    if not item:
        match = re.match(r"(.+?)\s+ekle", text_lower)
        if match:
            item = match.group(1).strip()

    # Clean up suffixes from extracted item
    if item:
        item = _clean_suffix(item)
    if location:
        location = _clean_suffix(location)

    return item, location


def _clean_suffix(text: str) -> str:
    """Remove common Turkish accusative/dative suffixes for cleaner names."""
    import re
    # Remove trailing suffixes like -yı, -yi, -ya, -ye, -a, -e, etc.
    # But be careful not to remove too much
    text = re.sub(r"[''](?:y[ıiuü]|n[ıiuü]|[ıiuü]|y[ae]|n[ae]|d[ae]n?|t[ae]n?)$", "", text)
    return text.strip()
