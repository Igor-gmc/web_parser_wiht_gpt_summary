# KEYWORDS, промпт, параметры парсинга, LLM, пути и т.д.

from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # загрузка переменных окружения из .env файла

@dataclass(frozen=True)
class Settings:
    KEYWORDS: list[str] = field(default_factory=lambda: ["SQL", "Игра", "Программирование"])
    FEED_URL: str = "https://habr.com/ru/articles/"
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    SELENIUM_TIMEOUT: int = 15  # seconds
    RETRIES: int = 3 # количество попыток при неудаче
    MAX_ARTICLES: int = 50 # сколько превью обрабатывать за запуск
    RESULTS_PARSE_OUTPUT_NAME: Path = Path("parser_result.jsonl")

    WORKDIR: Path = Path(".data") # рабоочая директория
    RESULT_OUTPUT_NAME: Path = Path("output.jsonl") # Имя готового файла с обработанными данными
    CLEAR_OUTPUT_NAME: Path = Path("clear_output.jsonl") # Только статьи с совпадениями
    LOG_PATH: Path = Path("logs/app.log") # Путь к лог файлу

    ENABLE_SEMANTIC: bool = True # опционально: семантический анализ с LLM и записать в jsonl, если False, то анализ статьи строго по ключевым словам
    LLM_MODEL: str = "gpt-4o-mini" # модель LLM для анализа
    OPENAI_API_KEY_ENV: str = "OPENAI_API_KEY"
    LLM_TEMPERATURE: float = 0.1 # креативность ответов LLM
    MAX_TOKENS: int = 1500 # максимальное количество токенов в ответе LLM
    SEMANTIC_THRESHOLD: float = 0.75 # порог похожести для семантичес
    RESULT_LLM_NAME: Path = Path("llm_result.jsonl")

    @property
    def HEADERS(self) -> dict:
        return {"User-Agent": self.USER_AGENT}

    # Прописываем вычисляемые пути
    @property
    def OUTPUT_PATH(self) -> Path:
        return self.WORKDIR / self.RESULT_OUTPUT_NAME # полный путь к готовому файлу jsonl с обработанными данными

    @property
    def CLEAR_OUTPUT_PATH(self) -> Path:
        return self.WORKDIR / self.CLEAR_OUTPUT_NAME # только статьи с совпадениями

    @property
    def DATA_LLM_PATH(self) -> Path:
        return self.WORKDIR / self.RESULT_LLM_NAME # для LLM ответов

    @property
    def DATA_PAGES_PATH(self) -> Path:
        return self.WORKDIR / self.RESULTS_PARSE_OUTPUT_NAME # для данных загруженных страниц

# Создаем экземпляр настроек
settings = Settings()
    