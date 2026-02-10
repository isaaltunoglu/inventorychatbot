"""Chat endpoint: NLU-powered natural language inventory management."""
import logging
from fastapi import APIRouter
from models import ChatRequest, ChatResponse, NLUResult
from nlu.intent import detect_intent
from nlu.ner import extract_item_and_location
from nlu.normalizer import normalize_for_search, lemmatize
import database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a Turkish natural language message and execute the appropriate
    inventory action.
    """
    message = request.message.strip()
    if not message:
        return ChatResponse(reply="Lütfen bir mesaj girin.")

    # Step 1: Normalize the text
    normalized = lemmatize(message)
    logger.info(f"Normalized: '{message}' -> '{normalized}'")

    # Step 2: Detect intent
    intent_result = detect_intent(message)
    intent = intent_result["intent"]
    confidence = intent_result["confidence"]
    logger.info(f"Intent: {intent} (confidence: {confidence})")

    # Step 3: Extract entities
    entities = extract_item_and_location(message)
    item_name = entities.get("item")
    location = entities.get("location")
    logger.info(f"Entities: item={item_name}, location={location}")

    # Build NLU result
    nlu_result = NLUResult(
        intent=intent,
        confidence=confidence,
        entities={"item": item_name, "location": location},
        normalized_text=normalized,
    )

    # Step 4: Execute action based on intent
    try:
        if intent == "add_item":
            return await _handle_add(item_name, location, nlu_result)
        elif intent == "remove_item":
            return await _handle_remove(item_name, nlu_result)
        elif intent == "query_location":
            return await _handle_query(item_name, normalized, nlu_result)
        elif intent == "list_items":
            return await _handle_list(nlu_result)
        elif intent == "update_quantity":
            return await _handle_update(item_name, message, nlu_result)
        else:
            return ChatResponse(
                reply=f"Komutu anlayamadım. Lütfen tekrar deneyin. (Algılanan niyet: {intent}, güven: {confidence:.2f})",
                nlu=nlu_result,
            )
    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        return ChatResponse(
            reply=f"İşlem sırasında bir hata oluştu: {str(e)}",
            nlu=nlu_result,
        )


async def _handle_add(item_name: str, location: str, nlu: NLUResult) -> ChatResponse:
    """Handle add_item intent."""
    if not item_name:
        return ChatResponse(
            reply="Hangi ürünü eklemek istediğinizi anlayamadım. Lütfen 'X ürününü Y konumuna ekle' şeklinde deneyin.",
            nlu=nlu,
        )

    location = location or "belirtilmedi"
    new_item = await database.add_item(item_name=item_name, location=location)

    return ChatResponse(
        reply=f"✅ '{item_name}' başarıyla '{location}' konumuna eklendi. (ID: {new_item['id']})",
        nlu=nlu,
        data=[new_item],
    )


async def _handle_remove(item_name: str, nlu: NLUResult) -> ChatResponse:
    """Handle remove_item intent."""
    if not item_name:
        return ChatResponse(
            reply="Hangi ürünü silmek istediğinizi anlayamadım.",
            nlu=nlu,
        )

    # Search for the item first
    normalized_name = normalize_for_search(item_name)
    items = await database.search_items(normalized_name)

    if not items:
        # Try original name
        items = await database.search_items(item_name)

    if not items:
        return ChatResponse(
            reply=f"❌ '{item_name}' adında bir ürün bulunamadı.",
            nlu=nlu,
        )

    # Delete the first match
    deleted = await database.delete_item(items[0]["id"])
    if deleted:
        return ChatResponse(
            reply=f"🗑️ '{items[0]['item_name']}' (ID: {items[0]['id']}) envantardan silindi.",
            nlu=nlu,
        )
    return ChatResponse(reply="Silme işlemi başarısız.", nlu=nlu)


async def _handle_query(item_name: str, normalized: str, nlu: NLUResult) -> ChatResponse:
    """Handle query_location intent."""
    if not item_name:
        return ChatResponse(
            reply="Neyi aradığınızı anlayamadım. Lütfen 'X nerede?' şeklinde sorun.",
            nlu=nlu,
        )

    # Search with normalized then original
    items = await database.search_items(normalize_for_search(item_name))
    if not items:
        items = await database.search_items(item_name)

    if not items:
        return ChatResponse(
            reply=f"🔍 '{item_name}' adında bir ürün envanterimizde bulunamadı.",
            nlu=nlu,
        )

    if len(items) == 1:
        i = items[0]
        return ChatResponse(
            reply=f"📍 '{i['item_name']}' -> Konum: {i['location']}, Miktar: {i['quantity']}",
            nlu=nlu,
            data=items,
        )

    lines = [f"📍 '{item_name}' için {len(items)} sonuç bulundu:"]
    for i in items:
        lines.append(f"  • {i['item_name']} -> {i['location']} (Miktar: {i['quantity']})")

    return ChatResponse(reply="\n".join(lines), nlu=nlu, data=items)


async def _handle_list(nlu: NLUResult) -> ChatResponse:
    """Handle list_items intent."""
    items = await database.get_all_items()

    if not items:
        return ChatResponse(reply="📦 Envanter boş.", nlu=nlu)

    lines = [f"📦 Envanterinizde {len(items)} ürün var:"]
    for i in items:
        lines.append(f"  • [{i['id']}] {i['item_name']} -> {i['location']} (Miktar: {i['quantity']})")

    return ChatResponse(reply="\n".join(lines), nlu=nlu, data=items)


async def _handle_update(item_name: str, original_msg: str, nlu: NLUResult) -> ChatResponse:
    """Handle update_quantity intent."""
    if not item_name:
        return ChatResponse(
            reply="Hangi ürünü güncellemek istediğinizi anlayamadım.",
            nlu=nlu,
        )

    # Try to extract a number from the message
    import re
    numbers = re.findall(r"\d+", original_msg)
    quantity = int(numbers[0]) if numbers else None

    # Find the item
    items = await database.search_items(normalize_for_search(item_name))
    if not items:
        items = await database.search_items(item_name)

    if not items:
        return ChatResponse(
            reply=f"❌ '{item_name}' adında bir ürün bulunamadı.",
            nlu=nlu,
        )

    if quantity is None:
        return ChatResponse(
            reply=f"'{items[0]['item_name']}' ürünü bulundu ancak yeni miktarı belirleyemedim. Lütfen bir sayı belirtin.",
            nlu=nlu,
        )

    updated = await database.update_item(items[0]["id"], quantity=quantity)
    return ChatResponse(
        reply=f"✅ '{updated['item_name']}' miktarı {quantity} olarak güncellendi.",
        nlu=nlu,
        data=[updated],
    )
