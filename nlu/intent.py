"""Intent detection using zero-shot classification with Turkish DistilBERT."""
import logging
from transformers import pipeline
from config import ZERO_SHOT_LABELS, LABEL_TO_INTENT

logger = logging.getLogger(__name__)

_classifier = None


def _get_classifier():
    """Lazy-load the zero-shot classification pipeline."""
    global _classifier
    if _classifier is None:
        logger.info("Loading zero-shot classification model (this may take a moment)...")
        _classifier = pipeline(
            "zero-shot-classification",
            model="emrecan/bert-base-turkish-cased-mean-nli-stsb-tr",
            device=-1,  # CPU
        )
        logger.info("Zero-shot classification model loaded.")
    return _classifier


def detect_intent(text: str) -> dict:
    """
    Detect the user's intent from Turkish text using zero-shot classification.

    Returns:
        dict with keys:
            - intent: str (e.g., "add_item", "query_location")
            - confidence: float (0.0 - 1.0)
            - label: str (the matched Turkish label)
    """
    classifier = _get_classifier()

    result = classifier(
        text,
        candidate_labels=ZERO_SHOT_LABELS,
        hypothesis_template="Bu cümle {} ile ilgili.",
    )

    top_label = result["labels"][0]
    top_score = result["scores"][0]

    intent = LABEL_TO_INTENT.get(top_label, "unknown")

    return {
        "intent": intent,
        "confidence": round(top_score, 4),
        "label": top_label,
    }
