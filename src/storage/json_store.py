# чтение/дополнение/запись data/output.json
import json
from pathlib import Path
from src.models.shemas import ShemaResult

def write_json_store(file_path: str, data: ShemaResult) -> None:
    """Записывает данные в JSON файл."""

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True) # создаем директории, если их нет

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)