"""Turkish text normalization using Zeyrek morphological analyzer."""
import logging

logger = logging.getLogger(__name__)

_analyzer = None


def _get_analyzer():
    """Lazy-load the Zeyrek analyzer."""
    global _analyzer
    if _analyzer is None:
        try:
            import zeyrek
            _analyzer = zeyrek.MorphAnalyzer()
            logger.info("Zeyrek morphological analyzer loaded.")
        except Exception as e:
            logger.warning(f"Zeyrek loading failed: {e}. Normalization will be disabled.")
            _analyzer = False  # Mark as failed so we don't retry
    return _analyzer


def lemmatize(text: str) -> str:
    """
    Lemmatize Turkish text: reduce inflected words to root forms.
    E.g., "kalemler" -> "kalem", "dosyayı" -> "dosya"
    """
    analyzer = _get_analyzer()
    if not analyzer:
        return text

    words = text.split()
    lemmatized = []

    for word in words:
        try:
            results = analyzer.lemmatize(word)
            if results:
                # results is a list of (word, [lemmas])
                # Take the first lemma of the first result
                lemmas = results[0][1]
                lemmatized.append(lemmas[0].lower() if lemmas else word.lower())
            else:
                lemmatized.append(word.lower())
        except Exception:
            lemmatized.append(word.lower())

    return " ".join(lemmatized)


def normalize_for_search(text: str) -> str:
    """
    Normalize text for database searching:
    - Lemmatize
    - Lowercase
    - Strip extra whitespace
    """
    return lemmatize(text).strip()
