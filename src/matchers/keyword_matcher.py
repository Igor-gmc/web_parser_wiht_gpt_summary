# совпадения по ключевым словам (preview/fulltext)

from src.settings import settings
from src.models.shemas import ShemaResult

def keywords_matcher(text: str) -> ShemaResult:
    """Проверяет текст на совпадение с ключевыми словами из настроек."""
    # Приводим текст к нижнему регистру для корректного сравнения
    text_lower = text.lower()
    
    # Ищем ключевые слова в тексте
    matched_keywords = [kw for kw in settings.KEYWORDS if kw.lower() in text_lower]

    if matched_keywords:
        return ShemaResult(
                match=bool(True),
                matched_keywords=matched_keywords,
                reason="Поиск перебором: В тексте найдены ключевые слова из settings.KEYWORDS"
                )
    else:
        return ShemaResult(
                match=bool(False),
                matched_keywords=[],
                reason="Поиск перебором: Ключевые слова из settings.KEYWORDS не найдены в тексте"
                )