# чтение/дополнение/запись data/output.json
import json
from pathlib import Path
from src.models.shemas import ShemaResult


def read_jsonl(file_path: str) -> list[dict]:
    """Читает JSONL файл и возвращает список словарей."""
    result = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                result.append(json.loads(line))
    return result


def write_json_store(file_path: str, data: ShemaResult) -> None:
    """Записывает данные в JSON файл."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True) # создаем директории, если их нет

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def write_json_result_parse(file_path: str, data: list[dict]) -> None:
    """Записывает список статей в JSONL файл (каждая строка - отдельный JSON объект)."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True) # создаем директории, если их нет

    with open(file_path, 'w', encoding='utf-8') as f:
        for item in data:
            json_line = json.dumps(item, ensure_ascii=False)
            f.write(json_line + '\n')