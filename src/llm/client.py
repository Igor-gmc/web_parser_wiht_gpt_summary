# обертка над ChatGPT API

import os
from typing import List
from pydantic import BaseModel, Field

from openai import OpenAI

from src.settings.config import settings
from src.llm.prompts import system_prompt

# Pydantic-схема (то, что будет в response.output_parsed)
from src.models.shemas import ShemaResult

def get_llm_client() -> OpenAI:
    """Создает и возвращает клиент OpenAI с заданным API ключом."""
    api_key = os.getenv(settings.OPENAI_API_KEY_ENV)

    if not api_key or not api_key.strip():
        raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")

    return OpenAI(api_key=api_key.strip())

def analyze_with_llm(client: OpenAI, article_text: str) -> ShemaResult:
    """Отправляет запрос к LLM для анализа статьи и возвращает ответ в виде словаря."""
    
    # Переводим статью в сообщение пользователя
    user_message = f"Вот текст статьи:\n{article_text}"
    
    # Формируем запрос для LLM
    response = client.responses.parse(
        model=settings.LLM_MODEL,
        input=[
            {"role": "system", "content": system_prompt},   # Тут используется промпт из src/llm/prompts.py с ключевыми словами settings.KEYWORDS
            {"role": "user", "content": user_message} # статья для анализа
        ],
        text_format=ShemaResult,
        max_output_tokens=settings.MAX_TOKENS,
        temperature=settings.LLM_TEMPERATURE,
    )
    
    result: ShemaResult = response.output_parsed

    if result is None:
        return ShemaResult(match=False, matched_keywords=[], reason="LLM вернула невалидный ответ")

    return result