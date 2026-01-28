# LLM/embeddings: “похоже по смыслу на KEYWORDS?”

from llm.client import get_llm_client, analyze_with_llm
from src.models.shemas import ShemaResult

def semantic_matcher(article_text: str) -> ShemaResult:
    """Проверяет текст статьи на смысловое соответствие ключевым словам из настроек с помощью LLM."""
    client = get_llm_client() # получаем клиент LLM
    return analyze_with_llm(client, article_text) # анализируем статью с помощью LLM и возвращаем результат видеа словаря