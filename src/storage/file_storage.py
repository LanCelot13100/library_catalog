#  Модуль для работы с файлами (JSON)
import json
import aiofiles
from typing import List, Dict, Any
from src.storage.base import StorageClient
from src.core.logger import get_logger

logger = get_logger(__name__)


class FileStorageClient(StorageClient):
    """Хранилище данных в JSON файле"""

    def __init__(self, path: str = "data.json"):
        self.path = path
        logger.info(f"FileStorageClient initialized with path: {path}")

    async def get_data(self) -> List[Dict[str, Any]]:
        """Загружает данные из JSON файла"""
        try:
            async with aiofiles.open(self.path, "r", encoding="utf-8") as f:
                content = await f.read()
                if not content.strip():
                    logger.info(f"File {self.path} is empty, returning empty list")
                    return []

                data = json.loads(content)
                logger.info(f"Loaded {len(data)} records from {self.path}")
                return data

        except FileNotFoundError:
            logger.info(f"File {self.path} not found, returning empty list")
            return []

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in file {self.path}: {e}")
            return []

        except Exception as e:
            logger.error(f"Error reading file {self.path}: {e}")
            return []

    async def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Сохраняет данные в JSON файл"""
        try:
            json_content = json.dumps(data, indent=2, ensure_ascii=False)

            async with aiofiles.open(self.path, "w", encoding="utf-8") as f:
                await f.write(json_content)

            logger.info(f"Saved {len(data)} records to {self.path}")

        except Exception as e:
            logger.error(f"Error saving data to file {self.path}: {e}")
            raise