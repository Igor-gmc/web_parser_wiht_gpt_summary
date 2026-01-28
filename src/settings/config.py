# KEYWORDS, промпт, параметры парсинга, LLM, пути и т.д.

from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # загрузка переменных окружения из .env файла

@dataclass(frozen=True)
class settings:
    KEYWORDS = ["example", "keywords", "here"]
    FEED_URL = "https://habr.com/ru/articles/"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    HEADERS = {"User-Agent": USER_AGENT}
    SELENIUM_TIMEOUT = 10  # seconds
    RETRIES = 3 # количество попыток при неудаче
    MAX_ARTICLES = 50 # сколько превью обрабатывать за запуск
    
    WORKDIR: Path = Path(".data") # рабоочая директория
    OUTPUT_NAME: Path = Path("output.jsonl") # Имя готового файла с обработанными данными
    LOG_PATH: Path = Path("logs/app.log") # Путь к лог файлу

    ENABLE_SEMANTIC = True # опционально: семантический анализ с LLM и записать в jsonl, если False, то анализ статьи строго по ключевым словам
    LLM_MODEL = "gpt-4o-mini" # модель LLM для анализа
    OPENAI_API_KEY_ENV = "OPENAI_API_KEY"
    LLM_TEMPERATURE = 0.1 # креативность ответов LLM
    MAX_TOKENS = 1500 # максимальное количество токенов в ответе LLM
    SEMANTIC_THRESHOLD = 0.75 # порог похожести для семантичес
    
    LOG_MAX_BYTES = 10 * 1024 * 1024 # максимальный размер лог файла в байтах
    CLEANUP_LOG_ON_START = True # лог удаляется при старте программы

    # Прописываем вычисляемые пути
    @property
    def OUTPUT_PATH(self) -> Path:
        return self.WORKDIR / self.OUTPUT_NAME # полный путь к готовому файлу jsonl с обработанными данными
    
    @property
    def CACHE_LLM_DIR(self) -> Path:
        return self.WORKDIR / "cache/llm" # директория для кеша LLM ответов
    
    @property
    def CACHE_PAGES_DIR(self) -> Path:
        return self.WORKDIR / "cache/pages" # директория для кеша загруженных страниц
    