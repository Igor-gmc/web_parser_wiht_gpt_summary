# парсинг ленты + фильтрация по ключевым словам

import os
from src.settings.config import settings
from src.parsers.feed_parser import habr_parser
from src.storage.json_store import read_jsonl, write_json_result_parse
from src.matchers.keyword_matcher import keywords_matcher
from src.matchers.semantic_matcher import semantic_matcher


def validate_api_key() -> None:
    """Проверяет наличие API ключа OpenAI, если включен семантический анализ."""
    if not settings.ENABLE_SEMANTIC:
        return

    api_key = os.getenv(settings.OPENAI_API_KEY_ENV)

    if not api_key or not api_key.strip():
        raise RuntimeError(
            f"\n{'=' * 50}\n"
            f"ОШИБКА: Не найден ключ API OpenAI\n"
            f"{'=' * 50}\n"
            f"ENABLE_SEMANTIC = True, но переменная окружения '{settings.OPENAI_API_KEY_ENV}' не установлена.\n\n"
            f"Варианты решения:\n"
            f"1. Создайте файл .env в корне проекта и добавьте:\n"
            f"   OPENAI_API_KEY=ваш_ключ_api\n\n"
            f"2. Или установите переменную окружения:\n"
            f"   export OPENAI_API_KEY=ваш_ключ_api\n\n"
            f"3. Или отключите семантический анализ в config.py:\n"
            f"   ENABLE_SEMANTIC = False\n"
            f"{'=' * 50}"
        )


def get_articles() -> list[dict]:
    """Получает статьи: парсит с сайта или загружает из кеша."""
    cache_path = settings.DATA_PAGES_PATH

    if cache_path.exists() and cache_path.stat().st_size > 0:
        print(f"Загрузка статей из кеша: {cache_path}")
        return read_jsonl(str(cache_path))

    print("Кеш не найден, запускаем парсинг...")
    return habr_parser()


def process_article(article: dict) -> dict:
    """Обрабатывает одну статью: проверяет по ключевым словам и семантически."""
    text = f"{article.get('title', '')} {article.get('text', '')}"

    # Проверка по ключевым словам
    keyword_result = keywords_matcher(text)

    result = {
        "date": article.get("date", ""),
        "title": article.get("title", ""),
        "text": article.get("text", ""),
        "url": article.get("url", ""),
        "keyword_match": keyword_result.model_dump()
    }

    # Семантическая проверка (если включена)
    if settings.ENABLE_SEMANTIC:
        semantic_result = semantic_matcher(text)
        result["semantic_match"] = semantic_result.model_dump()

    return result


def run_pipeline() -> list[dict]:
    """Запускает весь пайплайн обработки статей."""
    # Проверяем наличие API ключа до начала работы
    validate_api_key()

    print("=" * 50)
    print("Запуск пайплайна")
    print(f"ENABLE_SEMANTIC: {settings.ENABLE_SEMANTIC}")
    print("=" * 50)

    # Получаем статьи
    articles = get_articles()
    print(f"Получено статей: {len(articles)}")

    # Обрабатываем каждую статью
    results = []
    for i, article in enumerate(articles, 1):
        print(f"Обработка статьи {i}/{len(articles)}: {article.get('title', '')[:50]}...")
        processed = process_article(article)
        results.append(processed)

    # Сохраняем все результаты
    output_path = str(settings.OUTPUT_PATH)
    write_json_result_parse(output_path, results)
    print(f"Все результаты сохранены в: {output_path}")

    # Фильтруем статьи с совпадениями (keyword OR semantic)
    matched_results = [
        r for r in results
        if r["keyword_match"]["match"] or r.get("semantic_match", {}).get("match", False)
    ]

    # Сохраняем отфильтрованные результаты (полный JSON)
    clear_output_path = str(settings.CLEAR_OUTPUT_PATH)
    write_json_result_parse(clear_output_path, matched_results)
    print(f"Отфильтрованные результаты сохранены в: {clear_output_path}")

    # Выводим краткую информацию: дата – заголовок – ссылка
    print(f"\nРелевантные статьи:")
    print("-" * 50)
    for r in matched_results:
        print(f"{r.get('date', '')} – {r.get('title', '')} – {r.get('url', '')}")
    print("-" * 50)

    # Статистика
    keyword_matches = sum(1 for r in results if r["keyword_match"]["match"])
    print(f"\nСтатистика:")
    print(f"  Совпадений по ключевым словам: {keyword_matches}/{len(results)}")

    if settings.ENABLE_SEMANTIC:
        semantic_matches = sum(1 for r in results if r.get("semantic_match", {}).get("match", False))
        print(f"  Семантических совпадений: {semantic_matches}/{len(results)}")

    print(f"  Всего релевантных статей: {len(matched_results)}/{len(results)}")

    print("=" * 50)
    print("Пайплайн завершен")
    print("=" * 50)

    return results
