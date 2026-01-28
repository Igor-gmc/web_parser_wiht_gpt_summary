# Web Scraping Pipeline

Парсер статей с Habr.com с фильтрацией по ключевым словам и семантическим анализом через LLM.

## Описание проекта

Проект выполняет следующие задачи:
- Парсинг превью статей с Habr.com с использованием Selenium
- Извлечение даты, заголовка, текста и URL статьи
- Фильтрация статей по ключевым словам (точное совпадение)
- Семантический анализ релевантности через OpenAI GPT (опционально)
- Сохранение результатов в JSONL формате
- Вывод релевантных статей в консоль

## Установка

1. Клонируйте репозиторий
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Создайте файл `.env` в корне проекта (если используете семантический анализ):
   ```
   OPENAI_API_KEY=ваш_ключ_api
   ```

## Использование

### Запуск

```bash
python -m src.main
```

### Настройка параметров

Все настройки находятся в `src/settings/config.py`:

#### Ключевые параметры

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `KEYWORDS` | Список ключевых слов для поиска | `["Python", "Java", "Программирование"]` |
| `ENABLE_SEMANTIC` | Включить семантический анализ через LLM | `True` |
| `MAX_ARTICLES` | Максимум статей для обработки | `100` |
| `LLM_MODEL` | Модель OpenAI для анализа | `gpt-4o-mini` |
| `SELENIUM_TIMEOUT` | Таймаут ожидания загрузки страницы (сек) | `10` |

#### Параметр ENABLE_SEMANTIC

- `ENABLE_SEMANTIC = True` — статьи проверяются по ключевым словам И семантически через LLM. Требуется API ключ OpenAI.
- `ENABLE_SEMANTIC = False` — статьи проверяются только по ключевым словам. API ключ не требуется.

При запуске с `ENABLE_SEMANTIC = True` без API ключа программа выдаст понятную ошибку с вариантами решения.

### Управление кешем парсера

Парсер кеширует результаты в `.data/parser_result.jsonl`. При повторном запуске используются данные из кеша.

**Чтобы запустить парсинг заново:**

```bash
# Удалите файл кеша (Linux/Mac)
rm .data/parser_result.jsonl

# Или на Windows (PowerShell)
Remove-Item .data\parser_result.jsonl

# Или на Windows (CMD)
del .data\parser_result.jsonl
```

После удаления файла следующий запуск `python -m src.main` выполнит парсинг с сайта.

### Выходные файлы

После запуска в директории `.data/` появятся:

| Файл | Описание |
|------|----------|
| `parser_result.jsonl` | Кеш спарсенных статей (date, title, text, url) |
| `output.jsonl` | Все обработанные статьи с результатами анализа |
| `clear_output.jsonl` | Только релевантные статьи (keyword_match ИЛИ semantic_match = true) |

### Вывод в консоль

После обработки в консоль выводятся релевантные статьи в формате:
```
Релевантные статьи:
--------------------------------------------------
2026-01-28T12:29:46.000Z – Заголовок статьи – https://habr.com/ru/articles/...
--------------------------------------------------
```

## Структура проекта

```
web_scraping/
├── .data/                      # Рабочая директория с данными
│   ├── parser_result.jsonl     # Кеш парсера
│   ├── output.jsonl            # Все результаты
│   └── clear_output.jsonl      # Отфильтрованные результаты
├── src/
│   ├── llm/
│   │   ├── client.py           # Клиент OpenAI API
│   │   └── prompts.py          # Промпты для LLM
│   ├── matchers/
│   │   ├── keyword_matcher.py  # Поиск по ключевым словам
│   │   └── semantic_matcher.py # Семантический анализ через LLM
│   ├── models/
│   │   └── shemas.py           # Pydantic схемы данных
│   ├── parsers/
│   │   └── feed_parser.py      # Парсер Habr.com (Selenium)
│   ├── pipeline/
│   │   └── pipeline.py         # Оркестрация пайплайна
│   ├── settings/
│   │   └── config.py           # Настройки проекта
│   ├── storage/
│   │   └── json_store.py       # Чтение/запись JSONL
│   └── main.py                 # Точка входа
├── .env                        # Переменные окружения (не в git)
└── README.md
```

## Описание модулей

### src/main.py
Точка входа приложения. Запускает `run_pipeline()`.

### src/pipeline/pipeline.py
Оркестрация всего процесса:
- `validate_api_key()` — проверяет наличие API ключа если включен семантический анализ
- `get_articles()` — загружает статьи из кеша или парсит с сайта
- `process_article(article)` — обрабатывает одну статью (keywords + semantic)
- `run_pipeline()` — основной цикл обработки всех статей

### src/parsers/feed_parser.py
- `get_driver()` — создаёт Selenium WebDriver с кастомным User-Agent
- `parse_data_from_post(post)` — извлекает date, title, text, url из карточки статьи
- `scroll_and_find_posts(driver)` — скроллит страницу и собирает карточки статей
- `habr_parser()` — основная функция парсинга, возвращает список `{date, title, text, url}`

### src/matchers/keyword_matcher.py
- `keywords_matcher(text)` — проверяет текст на точное совпадение с ключевыми словами из `settings.KEYWORDS`

### src/matchers/semantic_matcher.py
- `semantic_matcher(text)` — отправляет текст в LLM для семантического анализа релевантности

### src/llm/client.py
- `get_llm_client()` — создаёт клиент OpenAI с проверкой API ключа
- `analyze_with_llm(client, text)` — отправляет запрос к LLM и возвращает структурированный ответ

### src/storage/json_store.py
- `read_jsonl(file_path)` — читает JSONL файл в список словарей
- `write_json_result_parse(file_path, data)` — записывает список словарей в JSONL

### src/models/shemas.py
- `ShemaResult` — Pydantic модель результата анализа:
  - `match: bool` — есть ли совпадение
  - `matched_keywords: list[str]` — найденные ключевые слова
  - `reason: str` — обоснование результата

### src/settings/config.py
- `Settings` — dataclass со всеми настройками проекта
- `settings` — экземпляр настроек для импорта

## Формат выходных данных

### parser_result.jsonl (кеш парсера)

```json
{
  "date": "2026-01-28T13:15:03.000Z",
  "title": "Заголовок статьи",
  "text": "Текст превью статьи",
  "url": "https://habr.com/ru/articles/123456/"
}
```

### output.jsonl / clear_output.jsonl

```json
{
  "date": "2026-01-28T13:15:03.000Z",
  "title": "Заголовок статьи",
  "text": "Текст превью статьи",
  "url": "https://habr.com/ru/articles/123456/",
  "keyword_match": {
    "match": true,
    "matched_keywords": ["Python"],
    "reason": "Поиск перебором: В тексте найдены ключевые слова..."
  },
  "semantic_match": {
    "match": true,
    "matched_keywords": ["Python"],
    "reason": "Обоснование LLM: Статья обсуждает..."
  }
}
```

## Лицензия

MIT
